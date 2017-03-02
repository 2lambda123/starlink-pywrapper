

Q2BAD
=====


Purpose
~~~~~~~
Converts an NDF's quality into bad values


Description
~~~~~~~~~~~
The routine converts an NDF's quality information into bad values.
There is no QUALITY structure in the output. This is a temporary
measure required whilst Figaro cannot handle NDFs with both a QUALITY
structure and flagged values.


ADAM parameters
~~~~~~~~~~~~~~~



IN = NDF (Read)
```````````````
Input NDF data structure.



OUT = NDF (Write)
`````````````````
Output NDF data structure.



