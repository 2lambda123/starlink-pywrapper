# Copyright (C) 2016 East Asian Observatory
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
A package for using Starlink commands from python.

Star is a package intended to allow easy 'pythonic' calling of
Starlink commands from python. It requires a working Starlink
installation to be available. Please use the function
`change_starpath` to set the correct $STARLINK_DIR path if its not
found automatically.

Starlink packages are available as star.<modulename>, and commands as
star.<modulename>.<commandname>. E.g.

>>> import star
>>> star.kappa.ndftrace

The help on a command can be seen as:

>>> help(star.kappa.ndftrace)


A command will return a namedtuple object with all of the output found
in $ADAM_USER/commandname.sdf.


This module uses the standard python logging module. To see the normal
stdout of a starlink command, you will need to set the logging module
to DEBUG.

By default, this package will run commands from a STARLINK_DIR defind
as: 1. The location indicated by $STARLINK_DIR or 2., if that is is
not set, it will attempt to see if the module is installed inside a
Starlink installation and use that.

To see which Starlink is currently being used show:

>>> print(utils.starpath)

To change the Starlink path, or set it up if none is automatically
found, use the function:

>>> star.change_starpath('~/star-2015B')


This package uses subprocess.Popen to wrap the Starlink command calls,
and sets up the necessary environmental variables itself. It uses the
Starlink module to access the output data written into
$ADAM_USER/commandname.sdf and return it to the user.

It uses a local, temporary $ADAM_USER created in the current working
directory and deleted on exit.

"""

from . import smurf
from . import cupid
from . import kappa
from . import convert
from . import figaro
from . import surf

from star import change_starpath

__version__ = 0.1
