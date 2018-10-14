from __future__ import division, print_function
import pylab, argparse, collections, inspect, functools
from itertools import takewhile
import time
import multiprocessing
import numpy as np
from numba import guvectorize, complex128, int32, void, vectorize, float32, float64, uint8
from enum import Enum, auto

Point = collections.namedtuple("Point", ["x", "y"])


class FractalType(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name

    MANDELBROT = auto()
    JULIA = auto()

def pair_reader(dtype):
  return lambda data: Point(*map(dtype, data.lower().split("x")))

DEFAULT_SIZE = "512x512"
DEFAULT_DEPTH = "256"
DEFAULT_ZOOM = "1"
DEFAULT_CENTER = "0x0"
DEFAULT_COLORMAP = "cubehelix"

def repeater(f):

  """
  Returns a generator function that returns a repeated function composition
  iterator (generator) for the function given, i.e., for a function input
  ``f`` with one parameter ``n``, calling ``repeater(f)(n)`` yields the
  values (one at a time)::

     n, f(n), f(f(n)), f(f(f(n))), ...
  Examples

  --------
  >>> func = repeater(lambda x: x ** 2 - 1)
  >>> func
  <function ...>

  >>> gen = func(3)
  >>> gen
  <generator object ...>

  >>> next(gen)
  3

  >>> next(gen) # 3 ** 2 - 1
  8

  >>> next(gen) # 8 ** 2 - 1
  63

  >>> next(gen) # 63 ** 2 - 1
  3968
  """

  @functools.wraps(f)
  def wrapper(n):
    val = n
    while True:
      yield val
      val = f(val)
  return wrapper


def amount(gen, limit=float("inf")):
  """
  Iterates through ``gen`` returning the amount of elements in it. The
  iteration stops after at least ``limit`` elements had been iterated.

  Examples
  --------

  >>> amount(x for x in "abc")
  3

  >>> amount((x for x in "abc"), 2)
  2

  >>> from itertools import count
  >>> amount(count(), 5) # Endless, always return ceil(limit)
  5

  >>> amount(count(start=3, step=19), 18.2)
  19
  """
  size = 0000
  for unused in gen:
    size += 1
    if size >= limit:
      break
  return size


def in_circle(radius):
  """ Returns ``abs(z) < radius`` boolean value function for a given ``z`` """
  return lambda z: z.real ** 2 + z.imag ** 2 < radius ** 2

def fractal_eta(z, func, limit, radius=2):
  """
  Fractal Escape Time Algorithm for pixel (x, y) at z = ``x + y * 1j``.
  Returns the fractal value up to a ``limit`` iteration depth.
  """
  return amount(takewhile(in_circle(radius), repeater(func)(z)), limit)

def cqp(c):
  """ Complex quadratic polynomial, function used for Mandelbrot fractal """
  return lambda z: z ** 2 + c


def get_model(model, depth, c):
  """
  Returns the fractal model function for a single pixel.
  """
  if model == "julia":
    func = cqp(c)
    return lambda x, y: fractal_eta(x + y * 1j, func, depth)

  if model == "mandelbrot":
    return lambda x, y: fractal_eta(0, cqp(x + y * 1j), depth)
  raise ValueError("Fractal not found")

def generate_fractal(model, c=None, size=pair_reader(int)(DEFAULT_SIZE),
                     depth=int(DEFAULT_DEPTH), zoom=float(DEFAULT_ZOOM),
                     center=pair_reader(float)(DEFAULT_CENTER)):
    start = time.time()
    rows = generate_rows(model, c=c, size=size, depth=depth, zoom=zoom, center=center)

    #Generates the intensities for each pixel
    img = pylab.array(rows)
    print('Time taken:', time.time() - start)
    return img

def mandelbrot_set2(xmin, xmax, ymin, ymax, width, height, maxiter, begin, end, data=None):
    r1 = np.linspace(xmin, xmax, width, dtype=np.float64)
    r2 = np.linspace(ymin, ymax, height, dtype=np.float64)
    c = r1 + r2[:, None] * 1j

    offset = end - begin
    data = np.zeros((offset, width))
    for i in range(begin, end):
        for j in range(width):
            data[i - begin, j] = mandelbrot(c[i][j], maxiter)

    return data

def generate_rows(model, c, y0, y1, size=pair_reader(int)(DEFAULT_SIZE),
                     depth=int(DEFAULT_DEPTH), zoom=float(DEFAULT_ZOOM),
                     center=pair_reader(float)(DEFAULT_CENTER)):
    """
    2D Numpy Array with the fractal value for each pixel coordinate.
    """
    num_procs = multiprocessing.cpu_count()

    # Create a pool of workers, one for each row
    pool = multiprocessing.Pool(num_procs)
    procs = [pool.apply_async(generate_row,
                              [model, c, size, depth, zoom, center, row])
                for row in range(size[1])]
    rows = [row_proc.get() for row_proc in procs]
    return np.array(rows)

def generate_row(model, c, size, depth, zoom, center, row):
  """
  Generate a single row of fractal values, enabling shared workload.
  """
  func = get_model(model, depth, c)
  width, height = size
  cx, cy = center
  side = max(width, height)
  sidem1 = side - 1
  deltax = (side - width) / 2 # Centralize
  deltay = (side - height) / 2
  y = (2 * (height - row + deltay) / sidem1 - 1) / zoom + cy
  return [func((2 * (col + deltax) / sidem1 - 1) / zoom + cx, y)
          for col in range(width)]


@vectorize([int32(complex128, int32)])
def mandelbrot(z, maxiter):
    c = z
    for n in range(maxiter):
        if abs(z) > 2:
            return n
        z = z * z + c
        # z = create_function(input('Enter equation in terms of z and c'))
    return maxiter

@guvectorize(['float64[:], float64[:], int32, int64[:,:]'], '(m),(n),() -> (m,n)')
def mandelbrot_set(r1, r2, maxiter, n3):
    height = len(r1)
    width = len(r2)

    for i in range(width):
        for j in range(height):
            n3[j,i] = mandelbrot(r1[i] + 1j * r2[j], maxiter)

# @guvectorize([(complex128[:], uint8[:])], '(n)->(n)', target='parallel')
# def julia_vect(Z,T):
#     c_real = creal
#     c_imag = cimag
#     for i in range(Z.shape[0]):
#         zimag = Z[i].imag
#         zreal = Z[i].real
#         T[i] = 0
#         zreal2 = zreal*zreal
#         zimag2 = zimag*zimag
#         while zimag2 + zreal2 <= 4:
#             zimag = 2* zreal*zimag + cimag
#             zreal = zreal2 - zimag2 + creal
#             zreal2 = zreal*zreal
#             zimag2 = zimag*zimag
#             T[i] += 1

def img2output(img, cmap=DEFAULT_COLORMAP, output=None, show=False):
  """ Plots and saves the desired fractal raster image """
  if output:
    pylab.imsave(output, img, cmap=cmap)
  if show:
    pylab.imshow(img, cmap=cmap)
    pylab.show()

def call_kw(func, kwargs):
  """ Call func(**kwargs) but remove the possible unused extra keys before """
  keys = inspect.getargspec(func).args
  kwfiltered = dict((k, v) for k, v in kwargs.items() if k in keys)
  return func(**kwfiltered)

def exec_command(kwargs):
  """ Fractal command from a dictionary of keyword arguments (from CLI) """
  kwargs["img"] = call_kw(generate_fractal, kwargs)
  call_kw(img2output, kwargs)

def cli_parse_args(args=None, namespace=None):
  """
  CLI (Command Line Interface) parsing based on ``ArgumentParser.parse_args``
  from the ``argparse`` module.
  """

  # CLI interface description
  parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
  )

  parser.add_argument("model", choices=["julia", "mandelbrot"],
                      help="Fractal type/model")

  parser.add_argument("c", nargs="*", default=argparse.SUPPRESS,
                      help="Single Julia fractal complex-valued constant "
                           "parameter (needed for julia, shouldn't appear "
                           "for mandelbrot), e.g. -.7102 + .2698j (with the "
                           "spaces), or perhaps with zeros and 'i' like "
                           "-0.6 + 0.4i. If the argument parser gives "
                           "any trouble, just add spaces between the numbers "
                           "and their signals, like '- 0.6 + 0.4 j'")

  parser.add_argument("-s", "--size", default=DEFAULT_SIZE,
                      type=pair_reader(int),
                      help="Size in pixels for the output file")

  parser.add_argument("-d", "--depth", default=DEFAULT_DEPTH,
                      type=int,
                      help="Iteration depth, the step count limit")

  parser.add_argument("-z", "--zoom", default=DEFAULT_ZOOM,
                      type=float,
                      help="Zoom factor, assuming data is shown in the "
                           "[-1/zoom; 1/zoom] range for both dimensions, "
                           "besides the central point displacement")

  parser.add_argument("-c", "--center", default=DEFAULT_CENTER,
                      type=pair_reader(float),
                      help="Central point in the image")

  parser.add_argument("-m", "--cmap", default=DEFAULT_COLORMAP,
                      help="Matplotlib colormap name to be used")

  parser.add_argument("-o", "--output", default=argparse.SUPPRESS,
                      help="Output to a file, with the chosen extension, "
                           "e.g. fractal.png")

  parser.add_argument("--show", default=argparse.SUPPRESS,
                      action="store_true",
                      help="Shows the plot in the default Matplotlib backend")



  # Process arguments
  ns_parsed = parser.parse_args(args=args, namespace=namespace)

  if ns_parsed.model == "julia" and "c" not in ns_parsed:
    parser.error("Missing Julia constant")

  if ns_parsed.model == "mandelbrot" and "c" in ns_parsed:
    parser.error("Mandelbrot has no constant")

  if "output" not in ns_parsed and "show" not in ns_parsed:
    parser.error("Nothing to be done (no output file name nor --show)")

  if "c" in ns_parsed:
    try:
      ns_parsed.c = complex("".join(ns_parsed.c).replace("i", "j"))
    except ValueError as exc:
      parser.error(exc)
  return vars(ns_parsed)

if __name__ == "__main__":
    xmin, xmax, width = 0, 1, 100
    ymin, ymax, height = 0, 1, 100

    r1 = np.linspace(xmin, xmax, width)
    r2 = np.linspace(ymin, ymax, height)
    n3 = np.ndarray((height, width))
    mandelbrot_set(r1, r2, 256, n3)
    print(n3)