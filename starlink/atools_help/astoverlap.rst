

ASTOVERLAP
==========


Purpose
~~~~~~~
Test if two regions overlap each other


Description
~~~~~~~~~~~
This application determines if the two supplied Regions overlap. The
two Regions are converted to a commnon coordinate system before
performing the check. If this conversion is not possible (for instance
because the two Regions represent areas in different domains), then
the check cannot be performed.


Usage
~~~~~


::

    
       astoverlap this that
       



ADAM parameters
~~~~~~~~~~~~~~~



FMT = LITERAL (Read)
````````````````````
The format in which to store output objects. Can be "AST", "XML",
"STCS", or any FitsChan encoding such as FITS-WCS. Only used if the
output object is written to a text file. An error is reported if the
output object cannot be written using the requested format. ["AST"]



THIS = LITERAL (Read)
`````````````````````
An NDF or text file holding the first region. If an NDF is supplied,
the current Frame in the WCS FrameSet will be used.



THAT = LITERAL (Read)
`````````````````````
An NDF or text file holding the second region. If an NDF is supplied,
the current Frame in the WCS FrameSet will be used.



RESULT = _INTEGER (Write)
`````````````````````````
On exit, this holds an integer indicating if there is any overlap
between the two Regions. Possible values are:
0 - The check could not be performed because the second Region could
not be mapped into the coordinate system of the first Region.
1 - There is no overlap between the two Regions.
2 - The first Region is completely inside the second Region.
3 - The second Region is completely inside the first Region.
4 - There is partial overlap between the two Regions.
5 - The Regions are identical to within their uncertainties.
6 - The second Region is the exact negation of the first Region to
within their uncertainties.



Copyright
~~~~~~~~~
Copyright (C) 2009 Science & Technology Facilities Council. All Rights
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


