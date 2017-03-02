

COLOUR
======


Purpose
~~~~~~~
Set colour table for image display


Description
~~~~~~~~~~~
This routine sets the colour table of the image display device. It can
either be reset to a grey scale, or an RGB lookup table from a 3xN
image can be used. The lookup table must have numbers between 0.0 and
1.0.


Usage
~~~~~


::

    
       colour table
       



ADAM parameters
~~~~~~~~~~~~~~~



TABLE = _CHAR (Read)
````````````````````
The colour table file to be used. The programme will look for this
file in the default directory and then in the standard Figaro
directories. If TABLE is 'grey' or 'gray' this is trapped and a grey
scale table is set up.



IDEV = _CHAR (Read)
```````````````````
The name of the imaging device, normally got from a global parameter
which was set with the IDEV command.



