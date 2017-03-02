

ASTTIMEFRAME
============


Purpose
~~~~~~~
Create a TimeFrame


Description
~~~~~~~~~~~
This application creates a new TimeFrame and optionally initialises
its attributes. A TimeFrame is a specialised form of one-dimensional
Frame that represents various coordinate systems used to describe
moments in time. The particular coordinate system to be used is
specified by setting the TimeFrame's System attribute (the default is
MJD) qualified, as necessary, by other attributes such as zero point,
time scale, units, etc (see the description of the System attribute
for details).


Usage
~~~~~


::

    
       asttimeframe options result
       



ADAM parameters
~~~~~~~~~~~~~~~



FMT = LITERAL (Read)
````````````````````
The format in which to store output objects. Can be "AST", "XML",
"STCS", or any FitsChan encoding such as FITS-WCS. Only used if the
output object is written to a text file. An error is reported if the
output object cannot be written using the requested format. ["AST"]



OPTIONS = LITERAL (Read)
````````````````````````
A string containing an optional comma-separated list of attribute
assignments to be used for initialising the new TimeFrame.



RESULT = LITERAL (Read)
```````````````````````
A text file to receive the new TimeFrame.



Copyright
~~~~~~~~~
Copyright (C) 2006 Central Laboratory of the Research Councils. All
Rights Reserved.


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


