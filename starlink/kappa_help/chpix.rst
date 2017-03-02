

CHPIX
=====


Purpose
~~~~~~~
Replaces the values of selected pixels in an NDF


Description
~~~~~~~~~~~
This application replaces selected elements of an NDF array component
with specified values. The task loops until there are no more elements
to change, indicated by a null value in response to a prompt. For non-
interactive processing, supply the value of parameter NEWVAL on the
command line.


Usage
~~~~~


::

    
       chpix in out section newval [comp]
       



ADAM parameters
~~~~~~~~~~~~~~~



COMP = LITERAL (Read)
`````````````````````
The name of the NDF array component to be modified. The options are:
"Data", "Error", "Quality" or "Variance". "Error" is the alternative
to "Variance" and causes the square of the supplied replacement value
to be stored in the output VARIANCE array. ["Data"]



IN = NDF (Read)
```````````````
NDF structure containing the array component to be modified.



NEWVAL = LITERAL (Read)
```````````````````````
Value to substitute in the output array element or elements. The range
of allowed values depends on the data type of the array being
modified. NEWVAL="Bad" instructs that the bad value appropriate for
the array data type be substituted. Placing NEWVAL on the command line
permits only one section to be replaced. If there are multiple
replacements, a null value (!) terminates the loop. If the section
being modified contains only a single pixel, then the original value
of that pixel is used as the suggested default value.



OLDVAL = LITERAL (Write)
````````````````````````
If the section being modified contains only a single pixel, then the
original value of that pixel is written out to this output parameter.



OUT = NDF (Write)
`````````````````
Output NDF structure containing the modified version of the array
component.



SECTION = LITERAL (Read)
````````````````````````
The elements to change. This is defined as an NDF section, so that
ranges can be defined along any axis, and be given as pixel indices or
axis (data) co-ordinates. So for example "3,4,5" would select the
pixel at (3,4,5); "3:5," would replace all elements in columns 3 to 5;
",4" replaces line 4. See "NDF sections" in SUN/95, or the online
documentation for details. A null value (!) terminates the loop during
multiple replacements.



TITLE = LITERAL (Read)
``````````````````````
Title for the output NDF structure. A null value (!) propagates the
title from the input NDF to the output NDF. [!]



Examples
~~~~~~~~
chpix rawspec spectrum 55 100
Assigns the value 100 to the pixel at index 55 within the one-
dimensional NDF called rawspec, creating the output NDF called
spectrum.
chpix rawspec spectrum 10:19 0 error
Assigns the value 0 to the error values at indices 10 to 19 within the
one-dimensional NDF called rawspec, creating the output NDF called
spectrum. The rawspec dataset must have a variance compoenent.
chpix in=rawimage out=galaxy section="~20,100:109" newval=bad
Assigns the bad value to the pixels in the section ~20,100:109 within
the two-dimensional NDF called rawimage, creating the output NDF
called galaxy. This section is the central 20 pixels along the first
axis, and pixels 110 to 199 along the second.
chpix in=zzcha out=zzcha_c section="45,21," newval=-1
Assigns value -1 to the pixels at index (45,21) within all planes of
the three-dimensional NDF called zzcha, creating the output NDF called
zzcha_c.



Related Applications
~~~~~~~~~~~~~~~~~~~~
KAPPA: ARDMASK, FILLBAD, GLITCH, NOMAGIC, REGIONMASK, SEGMENT,
SETMAGIC SUBSTITUTE, ZAPLIN; Figaro: CSET, ICSET, NCSET, TIPPEX.


Copyright
~~~~~~~~~
Copyright (C) 1995, 1998, 2004 Central Laboratory of the Research
Councils. Copyright (C) 2005 Particle Physics & Astronomy Research
Council. Copyright (C) 2012 Science & Facilities Research Council. All
Rights Reserved.


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


+ The routine correctly processes the AXIS, DATA, QUALITY, LABEL,
TITLE, UNITS, HISTORY, WCS and VARIANCE components of an NDF; and
propagates all extensions. Bad pixels and all non-complex numeric data
types can be handled.
+ The HISTORY component, if present, is simply propagated without
  change.




