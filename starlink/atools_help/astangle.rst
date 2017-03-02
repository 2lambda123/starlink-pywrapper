

ASTANGLE
========


Purpose
~~~~~~~
Calculate the angle subtended by two points at a third point


Description
~~~~~~~~~~~
This application finds the angle at point B between the line joining
points A and B, and the line joining points C and B. These lines will
in fact be geodesic curves appropriate to the Frame in use. For
instance, in SkyFrame, they will be great circles.


Usage
~~~~~


::

    
       astangle this a b c
       



ADAM parameters
~~~~~~~~~~~~~~~



A() = _DOUBLE (Read)
````````````````````
An array with one element for each Frame axis (Naxes attribute)
containing the coordinates of the first point.



B() = _DOUBLE (Read)
````````````````````
An array with one element for each Frame axis (Naxes attribute)
containing the coordinates of the second point.



C() = _DOUBLE (Read)
````````````````````
An array with one element for each Frame axis (Naxes attribute)
containing the coordinates of the third point.



DEGS = _LOGICAL (Read)
``````````````````````
If TRUE, the angle is reported in degrees. Otherwise it is reported in
radians. [FALSE]



FMT = LITERAL (Read)
````````````````````
The format in which to store output objects. Can be "AST", "XML",
"STCS", or any FitsChan encoding such as FITS-WCS. Only used if the
output object is written to a text file. An error is reported if the
output object cannot be written using the requested format. ["AST"]



THIS = LITERAL (Read)
`````````````````````
An NDF, FITS file or text file holding the Frame. If an NDF is
supplied, the current Frame of the WCS FrameSet will be used. If a
FITS file is supplied, the Frame corresponding to the primary axis
descriptions will be used.



Copyright
~~~~~~~~~
Copyright (C) 2011 Science & Technology Facilities Council. All Rights
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


