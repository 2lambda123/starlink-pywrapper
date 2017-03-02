

ASTSKYFRAME
===========


Purpose
~~~~~~~
Create a SkyFrame


Description
~~~~~~~~~~~
This application creates a new SkyFrame and optionally initialises its
attributes. A SkyFrame is a specialised form of Frame which describes
celestial longitude/latitude coordinate systems. The particular
celestial coordinate system to be represented is specified by setting
the SkyFrame's System attribute (currently, the default is FK5)
qualified, as necessary, by a mean Equinox value and/or an Epoch.
All the coordinate values used by a SkyFrame are in radians.


Usage
~~~~~


::

    
       astskyframe options result
       



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
assignments to be used for initialising the new SkyFrame.



RESULT = LITERAL (Read)
```````````````````````
A text file to receive the new SkyFrame.



Copyright
~~~~~~~~~
Copyright (C) 2001 Central Laboratory of the Research Councils. All
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


