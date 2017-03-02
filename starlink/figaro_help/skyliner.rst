

SKYLINER
========


Purpose
~~~~~~~
Removes a sky spectrum normalised by the height of the 5577 [OI]
emission line


Description
~~~~~~~~~~~
Removes a sky spectrum normalised by the height of the 5577 [OI]
emission line.


Usage
~~~~~


::

    
       SKYLINER IN SKY OUT
       



ADAM parameters
~~~~~~~~~~~~~~~



IN = NDF (Read)
```````````````
The one- or two-dimensional spectrum to be sky-subtracted.



SKY = NDF (Read)
````````````````
The one-dimensional sky spectrum. It must not contain bad pixels as
they could affect the estimation of the [OI] line strength.



OUT = NDF (Write)
`````````````````
The sky-subtracted one- or two-dimensional spectrum.
[parameter_default]



[parameter_spec]...
```````````````````




