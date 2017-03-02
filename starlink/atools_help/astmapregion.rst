

ASTMAPREGION
============


Purpose
~~~~~~~
Transform a Region into a new Frame using a given Mapping


Description
~~~~~~~~~~~
This application returns a pointer to a new Region which corresponds
to supplied Region described by some other specified coordinate
system. A Mapping is supplied which transforms positions between the
old and new coordinate systems. The new Region may not be of the same
class as the original region.


Usage
~~~~~


::

    
       astmapregion this map frame result
       



ADAM parameters
~~~~~~~~~~~~~~~



FMT = LITERAL (Read)
````````````````````
The format in which to store output objects. Can be "AST", "XML",
"STCS", or any FitsChan encoding such as FITS-WCS. Only used if the
output object is written to a text file. An error is reported if the
output object cannot be written using the requested format. ["AST"]



FRAME = LITERAL (Read)
``````````````````````
An NDF or text file holding the Frame that describes the coordinate
system in which the new Region is required. If an NDF is supplied, the
current Frame will be used.



MAP = LITERAL (Read)
````````````````````
An NDF or text file holding the Mapping which transforms positions
from the coordinate system represented by the supplied



