.. inclusion-marker-do-not-remove

Easily script Starlink commands with Python.

**This package requires a separate working Starlink installation to be
available and the path to be passed to the package**. See
https://starlink.eao.hawaii.edu to download Starlink. It allows easy
*pythonic* calling of Starlink commands from python, where you can use
normal Python arguments and keywords and have access to the call
signatures and help strings through the normal Python help.

There are auto-generated wrapper modules providing easy access to the
Starlink packages KAPPA, CONVERT, ATOOLS, CCDPACK, CUPID, FIGARO,
POLPACK, and SMURF. There are also commands to allow access to the
pipelines ORAC-DR and Picard.



Installation
------------

You should normally install this package via ``pip`` with::

      pip install starlink-pywrapper

This will also install the necessary python dependencies.

You must also have a working Starlink installation, which can be
downloaded from https://starlink.eao.hawaii.edu\.

Running commands
----------------

To run e.g. the KAPPA stats command command on a file
``myndf.sdf``, you would use the :meth:`starlink.kappa.stats`
function, after first importing the package and telling it where
your Starlink installation was

>>> from starlink import kappa
>>> kappa.wrapper.change_starpath('/path/to/my/starlink/installation')
>>> statsinfo = kappa.stats('myndf.sdf')
>>> print(statsinfo.mean)
18.3

As you can see in this example, the returned object from the command
will include all output values that you would previously have either
accessed with KAPPA's ``parget``, or just read from the screen output.


Many other commands will produce a new output NDF file on
disk. For example, the ``makesnr`` command in KAPPA:

>>> snrinfo = kappa.makesnr(in_='myndf.sdf', out='snr.sdf', minvar=0.0)
>>> print(snrinfo.out)
snr.sdf

The returned object is less useful for these commands, although may
contain useful information. The documentation should indicate what
values are returned and what they mean, and can be accessed as normal
in Python:

>>> help(kappa.makesnr)


Differences from standalone Starlink
====================================

 - When using the command line starlink programs, each command will
   often *remember* certain important variables you set previously,
   and use those as the default for the next repeat of that command,
   or the next command you run. This behaviour has been deliberately
   not included in this package, as when writing scripts this
   behaviour can produce suprising results. Instead, the documented
   defaults should always be the default seen by your programs.

 - You do not have to add shell escapes to your strings when passing them
   to Starlink commands.

 - You do not need to use KAPPA's ``parget`` to read the return values of a
   command; instead every return value is included in the returned
   object (a 'namedtuple' type) as a field.

 - Interactive usage of commands where you are prompted to enter
   values is not supported; the full command must be specified when
   running the command.

 - You should not use KAPPA's ``fitslist`` to access FITS header
   values programatically as it will only print values to the terminal
   (if logging is set to DEBUG), and does not provide access to them
   in an Python object. Instead, either use
   :meth:`starlink.kappa.fitsval` to read single values, or use the
   :meth:`starlink.utilities.get_ndf_fitshdr` to read in the entire
   FITS header of an NDF file and return it as an Astropy Header
   object (requires Astropy to be installed).
