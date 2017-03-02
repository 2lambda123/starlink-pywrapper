

CMULT
=====


Purpose
~~~~~~~
Multiplies an NDF by a scalar


Description
~~~~~~~~~~~
This application multiplies each pixel of an NDF by a scalar
(constant) value to produce a new NDF.


Usage
~~~~~


::

    
       cmult in scalar out
       



ADAM parameters
~~~~~~~~~~~~~~~



IN = NDF (Read)
```````````````
Input NDF structure whose pixels are to be multiplied by a scalar.



OUT = NDF (Write)
`````````````````
Output NDF structure.



SCALAR = _DOUBLE (Read)
```````````````````````
The value by which the NDF's pixels are to be multiplied.



TITLE = LITERAL (Read)
``````````````````````
A title for the output NDF. A null value will cause the title of the
NDF supplied for parameter IN to be used instead. [!]



Examples
~~~~~~~~
cmult a 12.5 b
Multiplies all the pixels in the NDF called a by the constant value
12.5 to produce a new NDF called b.
cmult in=rawdata out=newdata scalar=-19
Multiplies all the pixels in the NDF called rawdata by -19 to give
newdata.



Related Applications
~~~~~~~~~~~~~~~~~~~~
KAPPA: ADD, CADD, CDIV, CSUB, DIV, MATHS, MULT, SUB.


Copyright
~~~~~~~~~
Copyright (C) 1990-1991 Science & Engineering Research Council.
Copyright (C) 1995, 1998, 2004 Central Laboratory of the Research
Councils. Copyright (C) 2012 Science & Facilities Research Council.
All Rights Reserved.


Licence
~~~~~~~
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either Version 2 of the License, or (at
your option) any later version.
This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
02110-1301, USA.


Implementation Status
~~~~~~~~~~~~~~~~~~~~~


+ This routine correctly processes the AXIS, DATA, QUALITY, LABEL,
TITLE, UNITS, HISTORY, WCS and VARIANCE components of an NDF data
structure and propagates all extensions.
+ Processing of bad pixels and automatic quality masking are
supported.
+ All non-complex numeric data types can be handled. Arithmetic is
  carried out using the appropriate floating-point type, but the numeric
  type of the input pixels is preserved in the output NDF.




