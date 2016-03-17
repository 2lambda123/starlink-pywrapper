starlink-wrapper's documentation!
=================================

A package for using Starlink commands from python.

This is a package intended to allow easy 'pythonic' calling of
Starlink commands from python. It requires a working Starlink
installation to be available. Please use the function
`wrapper.change_starpath` to set the correct $STARLINK_DIR path if its not
found automatically.

Starlink packages are available as <modulename>, and commands as
<modulename>.<commandname>. E.g.

>>> from starlink import kappa
>>> ntrace = kappa.ndftrace('my/ndf.sdf')

The help on a command can be seen as:

>>> help(kappa.ndftrace)


A command will return a namedtuple object with all of the output found
in $ADAM_USER/commandname.sdf.


This module uses the standard python logging module. To see the normal
stdout of a starlink command, you will need to set the logging module
to DEBUG.

By default, this package will run commands from a STARLINK_DIR defined
by: 1. The location indicated by $STARLINK_DIR or 2., if that is is
not set, it will attempt to see if the module is installed inside a
Starlink installation and use that.

To see which Starlink is currently being used show:

or
>>> print(kappa.wrapper.starpath)

To change the Starlink path, or set it up if none is automatically
found, use the function:

>>> from starlink import wrapper
>>> wrapper.change_starpath('~/star-2015B')


This package uses subprocess.Popen to wrap the Starlink command calls,
and sets up the necessary environmental variables itself. It uses the
Starlink module to access the output data written into
$ADAM_USER/commandname.sdf and return it to the user.

It uses a local, temporary $ADAM_USER created in the current working
directory and deleted on exit.

Contents:

.. toctree::
   :maxdepth: 2

.. autosummary::
   :toctree: _autosummary

   starlink.wrapper

   starlink.convert
   starlink.cupid
   starlink.kappa
   starlink.smurf

   starlink.ccdpack
   starlink.figaro
   starlink.surf

   starlink.hdsutils




Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
