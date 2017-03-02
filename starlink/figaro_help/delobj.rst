

DELOBJ
======


Purpose
~~~~~~~
Delete an object in an HDS file


Description
~~~~~~~~~~~
This routine deletes an HDS object (structure or primitive, scalar or
array) in an HDS file.


Usage
~~~~~


::

    
       delobj object
       



ADAM parameters
~~~~~~~~~~~~~~~



OBJECT = HDSOBJECT (Read)
`````````````````````````
The object to be deleted. Specify beginning with directory and file
name in the syntax of the operating system, followed by the dot-
separated structure hierarchy. Elements of structure arrays are
specified in ordinary brackets (). An array element cannot be deleted.



Examples
~~~~~~~~
delobj file.axis(2).units
The file in question is in the current working directory and has the
standard extension ".sdf". The deleted structure is the UNITS string
in the 2nd element of the structure array AXIS. Note that it would be
impossible to delete AXIS(2), but one could delete AXIS as a whole.
delobj @"/home/resun02/myname/data/file.dst".z.label
Here the file is specified with its complete Unix directory and with
its non-standard extension ".dst". The deleted structure is the LABEL
within the Z structure.



