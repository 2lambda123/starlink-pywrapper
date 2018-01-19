.. inclusion-marker-do-not-remove
Provides a wrapper around the Starlink software suite commands.

This is a package intended to allow easy 'pythonic' calling of
Starlink commands from python. It requires a separate working Starlink
installation to be available.

The wrappred Starlink packages are wrapped each in their own python module,
available as `starlink.<modulename>`, and commands as
starlink.<modulename>.<commandname>.

Getting Started
***************


Setting up the package
----------------------

First of all, you will have to let this module know where your Starlink software suite is installed. You can either directly set the location inside python as:

>>> from starlink import wrapper
>>> wrapper.change_starpath('/path/to/my/starlink/installation')

Alternatively, before you start Python you could set the STARLINK_DIR
environmental variable to the location of your starlink
installation. For example, in a BASH shell you could run `export
STARLINK_DIR=~/star-2017A`.


To see which Starlink is currently being used examine the variable:

>>> wrapper.starpath

or if you are using a module you can do:

>>> print(kappa.wrapper.starpath)


Running the commands.
---------------------

You will need to import each Starlink module that you want to use. For example, to run the `stats` command from KAPPA on a file `my/ndf.sdf` you would do:

>>> from starlink import kappa
>>> statsvals = kappa.stats('my/ndf.sdf')

Each command will return a namedtuple object with all of the output found
in `$ADAM_USER/commandname.sdf`.

To see a field in a namedtuple result, you can do:

>>> print(statsvals.mean)

or to see what fields are available, you can do:

>>> print(statsvals._fields)

(Or inside an ipython terminal session or jupyter notebook you can tab
complete to see the list of available fields.)

Getting help on commands.
*************************


This package includes docstrings for each command, summarising the command and its arguments and keywords. This can be seen in the normal python way, e.g.

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
