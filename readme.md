# Distributed Fractal Rendering

Distributed Fractal Rendering (DFR) is an application that renders
high-resolution fractals via a parallelized distributed system. Fractal images
are valued for their aesthetics, but generating them can be computationally
expensive. Factors include the type of fractal and the inclusion of 
visual elements such as scale, resolution, color, and image effects / filters.
As a result, rendering high-quality fractals can be a resource sink,
especially if one is “browsing” or “searching” for the right image.

DFR addresses the computational demands of generating quality fractals by
employing multiple computers as workers for a main host.
The end user interactively specifies the type and visual attributes of the
fractal. Then, the host manages workflow by assigning each worker a task of
computing part of a fractal image. Results are sent to the main host,
who is responsible for piecing together the results and displaying
it for the end user.

### Hello How are you
### I'm Fine how about you
