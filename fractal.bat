# Mandelbrot Images
python -m fractal mandelbrot --size=600x600 --depth=256 --zoom=90 --center=-1.255x0.38 --show
python -m fractal mandelbrot --size=500x500 --depth=80 --zoom=0.8 --center=-0.75x0 --show
python -m fractal mandelbrot --size=500x500 --depth=256 --zoom=6.5 --center=-1.2x0.35 --show
python -m fractal mandelbrot --size=400x300 --depth=80 --zoom=2 --center=-1x0 --show
python -m fractal mandelbrot --size=300x300 --depth=80 --zoom=1.2 --center=-1x0 --show

#Julia Set Images
python -m fractal julia -1.037 +0.17 j --size=600x300 --depth=40 --zoom=0.55 --show
python -m fractal julia -0.8 +0.156 j --size=500x300 --depth=512 --zoom=0.6 --show
python -m fractal julia -0.8 +0.156 j --size=400x230 --depth=50 --zoom=0.65 --show
python -m fractal julia -0.77777 -0.25 j --size=527x331 --depth=200 --zoom=0.7 --show
python -m fractal julia -0.7102 +0.2698 j --size=500x300 --depth=512 --zoom=0.65 --show
python -m fractal julia -0.7 +0.27015 j --size=500x300 --depth=512 --zoom=0.6 --show
python -m fractal julia -0.644 --size=300x200 --depth=25 --zoom=0.6 --show