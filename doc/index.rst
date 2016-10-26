..title:: Starlink-Wrapper's Documentation

Starlink-Wrapper's Documentation
=================================

A package for using Starlink commands from python.

This is a package intended to allow easy 'pythonic' calling of
Starlink commands from python. It requires a working Starlink
installation to be available. Please use the method
:meth:`starlink.wrapper.change_starpath` to set the correct $STARLINK_DIR path
if its not found automatically.

Starlink packages are available as starlink.<modulename>, and commands
as <modulename>.<commandname>.


>>> from starlink import kappa
>>> statsvals = kappa.stats('my/ndf.sdf')

A command will return a namedtuple object with all of the output found
in $ADAM_USER/commandname.sdf.

To see a field in a namedtuple result, you can do:

>>> print(statsvals.mean)

or to see what fields are available, you can either tab complete, or
do:

>>> print(statsvals._fields)

The help on a command can be seen as:

>>> help(kappa.ndftrace)



You can also directly run a starlink command using
:meth:`starlink.wrapper.starcomm` method. This method is used by the starlink
modules to run the commands.

>>> from starlink import wrapper
>>> results = wrapper.starcomm('$KAPPA_DIR/ndftrace', 'ndftrace', 'myndf.sdf')


These modules use the standard python logging module. To see the normal
stdout of a starlink command, you will need to set the logging module
to DEBUG, i.e.:

>>> import logging
>>> logger = logging.getLogger()
>>> logger.setLevel(logging.DEBUG)


By default, this package will run commands from a STARLINK_DIR defined
by the location indicated by the environ variable STARLINK_DIR. If that is is
not set, it will attempt to see if the module is installed inside a
Starlink installation and use that.

To see which Starlink is currently being used examine the variable:

>>> wrapper.starpath

or if you are using a module you can do:

>>> print(kappa.wrapper.starpath)

To change the Starlink path, or set it up if none is automatically
found, use the method :meth:`starlink.change_starpath`, as e.g.:

>>> from starlink import wrapper
>>> wrapper.change_starpath('~/star-2015B')


This package uses subprocess.Popen to wrap the Starlink command calls,
and sets up the necessary environmental variables itself. It uses the
Starlink module to access the output data written into
$ADAM_USER/commandname.sdf and return it to the user.

It uses a local, temporary $ADAM_USER created in the current working
directory and deleted on exit.

Known Issues
============

1. When calling Starlink commands that are really python scripts, such
as :meth:`starlink.smurf.jsasplit`, the module will not raise a proper error
. Please ensure you can see the DEBUG info to identify problems.
(This can be fixed if the scripts raise an exit code on error).

2. If running a command (such as :meth:`starlink.kappa.display` that launches a
GWM xwindow, the command will hang until you close the window. (DSB's
starutil.py module in SMURF has a solution to this already).

3. Also with GWM windows: these are missing the row of buttons along
the bottom, unless the python call reuses an existing xw launched
directly from Starlink. It is not known why.


Contents:

.. toctree::
   :maxdepth: 2

.. autosummary::
   :toctree: _autosummary

   starlink.wrapper
   starlink.hdsutils
   starlink.utilities


   starlink.ccdpack
   starlink.convert
   starlink.cupid
   starlink.figaro
   starlink.kappa
   starlink.smurf
   starlink.surf

   starlink.picard






Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
