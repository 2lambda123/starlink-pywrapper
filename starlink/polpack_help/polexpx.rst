

POLEXPX
=======


Purpose
~~~~~~~
Copies information from the POLPACK extension to named FITS keywords


Description
~~~~~~~~~~~
This application is not for general use. It is a version of POLEXP
which is used within the polexp.csh script to export POLPACK
information during on-thr-fly data conversion. In this context, it is
known that only a single input file will be specified, and that it
will be a native NDF. We can therefore make big speed gains by using
NDF directtly instead of indirectly through the NDG library.
The default conversion table described in POLIMP is used.


Usage
~~~~~


::

    
       polexpx in
       



ADAM parameters
~~~~~~~~~~~~~~~



IN = NDF (Read)
```````````````
The input (native) NDF.



Copyright
~~~~~~~~~
Copyright (C) 1999 Central Laboratory of the Research Councils


