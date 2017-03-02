

POLIMPX
=======


Purpose
~~~~~~~
Copies FITS keyword values into the POLPACK extension


Description
~~~~~~~~~~~
This application is not for general use. It is a version of POLIMP
which is used within the polimp.csh script to import POLPACK
information during on-thr-fly data conversion. In this context, it is
known that only a single input file will be specified, and that it
will be a native NDF. We can therefore make big speed gains by using
NDF directtly instead of indirectly through the NDG library.
The default import table described in POLIMP is used. Nothing is
reported on the screen.


Usage
~~~~~


::

    
       polimpx in table
       



ADAM parameters
~~~~~~~~~~~~~~~



IN = NDF (Read)
```````````````
The input (native) NDF.



Notes
~~~~~


+ Any existing values in the POLPACK extension are deleted before
processing the supplied control table.
+ A new Frame is added to the WCS component of each NDF and is given
  the Domain "POLANAL". This Frame is formed by rotating the grid co-
  ordinate Frame so that the first axis is parallel to the analyser
  axis. The angle of rotation is given by the ANGROT value and defaults
  to zero if ANGROT is not specified in the control table. As of POLPACK
  V2.0, the ANGROT value is no longer stored explicitly in the POLPACK
  extension; its value is deduced from the POLANAL Frame in the WCS
  component.




Copyright
~~~~~~~~~
Copyright (C) 1998 Central Laboratory of the Research Councils


