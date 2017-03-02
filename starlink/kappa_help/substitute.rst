

SUBSTITUTE
==========


Purpose
~~~~~~~
Replaces all occurrences of a given value in an NDF array with another
value


Description
~~~~~~~~~~~
This application changes all pixels that have a defined value in an
NDF with an alternate value. Other values are unchanged. The number of
replacements is reported.


Usage
~~~~~


::

    
       substitute in out oldval newval [comp]
       



ADAM parameters
~~~~~~~~~~~~~~~



COMP = LITERAL (Read)
`````````````````````
The components whose values are to be substituted. It may be "Data",
"Error", "Variance", or "All". The last of the options forces
substitution in both the data and variance arrays. This parameter is
ignored if the data array is the only array component within the NDF.
["Data"]



IN = NDF (Read)
```````````````
Input NDF structure containing the data and/or variance array to have
some of its elements substituted.



OUT = NDF (Write)
`````````````````
Output NDF structure containing the data and/or variance array that is
a copy of the input array, but with replacemeent values substituted.



NEWVAL = _DOUBLE (Read)
```````````````````````
The value to replace occurrences of OLDVAL. It must lie within the
minimum and maximum values of the data type of the array with higher
precision. The new value is converted to data type of the array being
converted before the search begins. The suggested default is the
current value.



OLDVAL = _DOUBLE (Read)
```````````````````````
The element value to be replaced. The same value is substituted in
both the data and variance arrays when COMP="All". It must lie within
the minimum and maximum values of the data type of the array with
higher precision. The replacement value is converted to data type of
the array being converted before the search begins. The suggested
default is the current value.



TITLE = LITERAL (Read)
``````````````````````
Title for the output NDF structure. A null value (!) propagates the
title from the input NDF to the output NDF. [!]



Examples
~~~~~~~~
substitute aa bb 1 0
This copies the NDF called aa to the NDF bb, except that any pixels
with value 1 in aa are altered to have value 0 in bb.
substitute aa bb oldval=1 newval=0 comp=v
As above except the substitution occurs to the variance values.
substitute in=saturn out=saturn5 oldval=2.5 newval=5 comp=All
This copies the NDF called saturn to the NDF saturn5, except that any
elements in the data and variance arrays that have value 2.5 are
altered to have value 5 in saturn5.



Notes
~~~~~


+ The comparison for floating-point values tests that the difference
  between the replacement value and the element value is less than their
  mean times the precision of the data type.




Related Applications
~~~~~~~~~~~~~~~~~~~~
KAPPA: CHPIX, FILLBAD, GLITCH, NOMAGIC, SEGMENT, SETMAGIC, ZAPLIN;
SPECDRE: GOODVAR.


Copyright
~~~~~~~~~
Copyright (C) 1997-1998, 2004 Central Laboratory of the Research
Councils. Copyright (C) 2012 Science & Technology Facilities Council.
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


+ This routine correctly processes the AXIS, DATA, QUALITY, VARIANCE,
LABEL, TITLE, UNITS, WCS and HISTORY components of an NDF data
structure and propagates all extensions.
+ All non-complex numeric data types can be handled.
+ Any number of NDF dimensions is supported.




