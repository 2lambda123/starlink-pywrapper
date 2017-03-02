

ASTCLEAR
========


Purpose
~~~~~~~
Clear attribute values for an Object


Description
~~~~~~~~~~~
This application clears the values of a specified set of attributes
for an Object. Clearing an attribute cancels any value that has
previously been explicitly set for it, so that the standard default
attribute value will subsequently be used instead. This also causes
the ASTTEST application to return the value FALSE for the attribute,
indicating that no value has been set.


Usage
~~~~~


::

    
       astclear this attrib result
       



ADAM parameters
~~~~~~~~~~~~~~~



ATTRIB = LITERAL (Read)
```````````````````````
A string containing a comma-separated list of the names of the
attributes to be cleared.



FMT = LITERAL (Read)
````````````````````
The format in which to store output objects. Can be "AST", "XML",
"STCS", or any FitsChan encoding such as FITS-WCS. Only used if the
output object is written to a text file. An error is reported if the
output object cannot be written using the requested format. ["AST"]



RESULT = LITERAL (Read)
```````````````````````
An NDF or text file to receive the modified Object. If an NDF is
supplied, the WCS FrameSet within the NDF will be replaced by the new
Object if possible (if it is a FrameSet in which the base Frame has
Domain GRID and has 1 axis for each NDF dimension).



THIS = LITERAL (Read)
`````````````````````
An NDF or text file holding the original Object. If an NDF is
supplied, the WCS FrameSet will be used.



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


