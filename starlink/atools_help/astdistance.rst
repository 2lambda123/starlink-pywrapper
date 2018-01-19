

ASTDISTANCE
===========


Purpose
~~~~~~~
Calculate the distance between two points in a Frame


Description
~~~~~~~~~~~
This application finds the distance between two points whose Frame
coordinates are given. The distance calculated is that along the
geodesic curve that joins the two points. The distance is displayed on
the screen ("<bad>" is displayed if the distance cannot be
calculated).
For example, in a basic Frame, the distance calculated will be the
Cartesian distance along the straight line joining the two points. For
a more specialised Frame describing a sky coordinate system, however,
it would be the distance along the great circle passing through two
sky positions.


Usage
~~~~~


::

    
       astdistance this point1 point2
       



ADAM parameters
~~~~~~~~~~~~~~~



FMT = LITERAL (Read)
````````````````````
The format in which to store output objects. Can be "AST", "XML",
"STCS", or any FitsChan encoding such as FITS-WCS. Only used if the
output object is written to a text file. An error is reported if the
output object cannot be written using the requested format. ["AST"]



DISTANCE = _DOUBLE (Write)
``````````````````````````
The calculated distance.



THIS = LITERAL (Read)
`````````````````````
An NDF, FITS file or text file holding the Frame. If an NDF is
supplied, the current Frame of the WCS FrameSet will be used. If a
FITS file is supplied, the Frame corresponding to the primary axis
descriptions will be used.



POINT1() = _DOUBLE (Read)
`````````````````````````
An array with one element for each Frame axis (Naxes attribute)
containing the coordinates of the first point.



POINT2() = _DOUBLE (Read)
`````````````````````````
An array with one element for each Frame axis (Naxes attribute)
containing the coordinates of the second point.



Copyright
~~~~~~~~~
Copyright (C) 2008 Science & Technology Facilities Council. All Rights
Reserved.


Licence
~~~~~~~
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or (at
your option) any later version.
This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street,Fifth Floor, Boston, MA
02110-1301, USA


