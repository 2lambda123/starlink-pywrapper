

ASTMATCHAXES
============


Purpose
~~~~~~~
Find any corresponding axes in two Frames


Description
~~~~~~~~~~~
This application looks for corresponding axes within two supplied
Frames. A list array of integers is displayed with one element for
each axis in the second supplied Frame. An element in this list will
be set to zero if the associated axis within the second Frame has no
corresponding axis within the first Frame. Otherwise, it will be set
to the index (a non-zero positive integer) of the corresponding axis
within the first supplied Frame.


Usage
~~~~~


::

    
       astmatchaxes frm1 frm2
       



ADAM parameters
~~~~~~~~~~~~~~~



AXES() = _INTEGER (Write)
`````````````````````````
An output parameter to which is written an integer array holding the
indices of the axes (within the first Frame) that correspond to each
axis within the second Frame. Axis indices start at 1. A value of zero
will be stored in the returned array for each axis in the second Frame
that has no corresponding axis in the first Frame.



FMT = LITERAL (Read)
````````````````````
The format in which to store output objects. Can be "AST", "XML",
"STCS", or any FitsChan encoding such as FITS-WCS. Only used if the
output object is written to a text file. An error is reported if the
output object cannot be written using the requested format. ["AST"]



FRM1 = LITERAL (Read)
`````````````````````
An NDF or text file holding the first Frame or FrameSet. If an NDF is
supplied, the WCS FrameSet will be used.



FRM2 = LITERAL (Read)
`````````````````````
An NDF or text file holding the second Frame or FrameSet. If an NDF is
supplied, the WCS FrameSet will be used.



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


