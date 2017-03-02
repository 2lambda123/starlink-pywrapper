

GASP2NDF
========


Purpose
~~~~~~~
Converts an image in GASP format to an NDF


Description
~~~~~~~~~~~
This application converts a GAlaxy Surface Photometry (GASP) format
file into an NDF.


Usage
~~~~~


::

    
       gasp2ndf in out shape=?
       



ADAM parameters
~~~~~~~~~~~~~~~



IN = FILENAME (Read)
````````````````````
A character string containing the name of GASP file to convert. The
extension should not be given, since ".dat" is assumed.



OUT = NDF (Write)
`````````````````
The name of the output NDF.



SHAPE( 2 ) = _INTEGER (Read)
````````````````````````````
The dimensions of the GASP image (the number of columns followed by
the number of rows). Each dimension must be in the range 1 to 1024.
This parameter is only used if supplied on the command line, or if the
header file corresponding to the GASP image does not exist or cannot
be opened.



Examples
~~~~~~~~
gasp2ndf m31_gasp m31
Convert a GASP file called m31_gasp.dat into an NDF called m31. The
dimensions of the image are taken from the header file m31_gasp.hdr.
gasp2ndf n1068 ngc1068 shape=[256,512]
Take the pixel values in the GASP file n1068.dat and create the NDF
ngc1068 with dimensions 256 columns by 512 rows.



Notes
~~~~~


+ A GASP image is limited to a maximum of 1024 by 1024 elements. It
must be two dimensional.
+ The GASP image is written to the NDF's data array. The data array
has type _WORD. No other NDF components are created.
+ If the header file is corrupted, you must remove the offending
  ".hdr" file or specify the shape of the GASP image on the command
  line, otherwise the application will continually abort.




References
~~~~~~~~~~
GASP documentation (MUD/66).


Related Applications
~~~~~~~~~~~~~~~~~~~~
CONVERT: NDF2GASP.


Keywords
~~~~~~~~
CONVERT, GASP


Copyright
~~~~~~~~~
Copyright (C) 1993 Science & Engineering Research Council. Copyright
(C) 2004 Central Laboratory of the Research Councils. All Rights
Reserved.


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


