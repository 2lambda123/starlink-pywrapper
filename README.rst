.. inclusion-marker-do-not-remove
Provides a wrapper around the Starlink software suite commands.

**This package requires a separate working Starlink installation to be
available.** It allow easy 'pythonic' calling of Starlink commands
from python, by settuping the environmental variables inside Python
and then using `subprocess.Popen` to run the Starlink binaries.

The wrapped Starlink packages are each provided in their own python
module, available as `starlink.<modulename>`, and the within the
package as starlink.<modulename>.<commandname>.


Using this package
==================

Setting up the package
----------------------

First of all, you will have to let this module know where your
Starlink software suite is installed. You can either directly set the
location inside python as:

>>> from starlink import wrapper
>>> wrapper.change_starpath('/path/to/my/starlink/installation')

Alternatively, before you start Python you could set the STARLINK_DIR
environmental variable to the location of your starlink
installation. For example, in a BASH shell you could run `export
STARLINK_DIR=~/star-2017A`.


To see which Starlink is currently being used examine the variable
`wrapper.starpath`.

or if you are using a module you can do e.g.:

>>> print(kappa.wrapper.starpath)


Running the commands.
---------------------

You will need to import each Starlink package that you want to use. For
example, to run the `stats` command from KAPPA on a file `myndf.sdf`
you would do:

>>> from starlink import kappa
>>> statsvals = kappa.stats('myndf.sdf')

Each command will return a namedtuple object with all of the output found
in `$ADAM_USER/commandname.sdf`.

To see a field in a namedtuple result, you can do:

>>> print(statsvals.mean)

or to see what fields are available, you can do:

>>> print(statsvals._fields)

(Or inside an ipython terminal session or jupyter notebook you can tab
complete to see the list of available fields.)

Getting help.
-------------

This package includes docstrings for each command, summarising the
command and its arguments and keywords. This can be seen in the normal
python way, e.g.

>>> help(kappa.ndftrace)

At the bottom of the command it should also give you the URL to see
the full documentation in the Starlink User Notes.

To see the available commands in a package, there is a utiliity
'starhelp' that will show you the name and the short one-line
description for each command. You can use it on a Starlink module like so:

>>> from starlink.utilities import starhelp
>>> starhelp(kappa)


`starhelp` can also be called with a command name as the argument: it
will then show you the full documentation for that command within your
python session.

>>> starhelp(kappa.stats)


Directly running a command without using the specific package.
--------------------------------------------------------------


You can also directly run a starlink command using
:meth:`starlink.wrapper.starcomm` method. This method is used by the starlink
modules to run the commands.

>>> from starlink import wrapper
>>> results = wrapper.starcomm('$KAPPA_DIR/ndftrace', 'ndftrace', 'myndf.sdf')

This can be helpful if there is something wrong with the
automatically-generated argument and keyword options in the specific
commands, or if you are trying to run a command that is not included
in the regular packages.

Logging and seeing the full output.
-----------------------------------

These modules use the standard python logging module. To see the normal
stdout of a starlink command, as well as the details of the commanline , you will need to set the logging module
to DEBUG, i.e.:

>>> import logging
>>> logger = logging.getLogger()
>>> logger.setLevel(logging.DEBUG)

You can also return all the information that is normally written to screen by
setting the extra keyword argument `returnstdout=True`. This will cause your command
to return a two part tuple of `(<normal-output>, <string-of-output-from-screen>)`.


ORAC-DR and PICARD
------------------

ORAC-DR and Picard work slighly differently from the other Starlink packages.


Details of package
==================

The commands in this package are (mostly) automatically generated from
a Starlink build using a helper script. This script is present in the
git repo for this project
(https://github.com/Starlink/starlink-pywrapper , see the
'helperfunctions' directory), but is not distributed when you install
the software. Currently the FLUXES package is the only manually
created command.


This package uses subprocess.Popen to wrap the Starlink command calls,
and sets up the necessary environmental variables itself. It uses the
Starlink module to access the output data written into
$ADAM_USER/commandname.sdf and return it to the user. It is not
necessary to setup Starlink before using this script (e.g. by running
`source $STARLINK_DIR/etc/profile` or similar), but you do have to
tell the package where $STARLINK_DIR is, either by setting the
environmental variable before starting Python, or by calling the
`starlink.wrapper.change_starpath` command with the appropriate
location.

This package uses a local, temporary $ADAM_USER created in the current working
directory and deleted on exit, so it is safe to have multiple scripts
running concurrently on the same machine.

This package should be regenerated for each Starlink release; normally
most commands will stay unchanged on a new release, but there are
normally a few additional commands (or deletion of obsolete commands),
and the call signature for some commands may also change.



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
