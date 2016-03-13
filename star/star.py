# Copyright (C) 2013-2014 Science and Technology Facilities Council.
# Copyright (C) 2015-2016 East Asian Observatory
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


"""Module for carrying out starlink commands within python.

This uses subprocess.Popen to carry out starlink commands.

This module allows you to use a standard formatted keyword arguments
to call the starlink commands. Shell escapes do not to be used.

By default it will create a new temporary adam directory in the
current folder, and use that as the adam directory for the starlink
processes.

This code was written to allow quick calling of kappa, smurf and cupid
in the way I usually think about them from python scripts, with
regular keyword variables.

Its recommended to set STARLINK_DIR in your environment before opening
python to run this software.

"""



import atexit
import logging
import numpy as np
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time

from collections import namedtuple
from keyword import iskeyword

from astropy.io import fits
from starlink import hds, ndfpack

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Subprocess fix for sig pipe? Attempt to solve a problem
def subprocess_setup():
    # Python installs a SIGPIPE handler by default. This is usually
    # not what non-Python subprocesses expect.
    signal.signal(signal.SIGXFSZ, signal.SIG_DFL)
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)

# Get something sensible for the starpath.
try:
    starpath = os.path.join(os.environ['STARLINK_DIR'])
except KeyError:
    Warning('STARLINK_DIR not defined in environment, defaulting to /stardev/.'
            + 'Please change star.starpath if this is not the correct path.')
    starpath = '/stardev'


# Get the current enivronmental  variables.
env = os.environ.copy()

# Add on the STARLINK libraries to the environmental path
# LD_LIBRARY_PATH (linux) or DYLD_LIBRARY_PATH (mac)

if sys.platform == 'darwin':
    ld_environ = 'DYLD_LIBRARY_PATH'
    javapaths = [os.path.join(starpath,'starjava', 'lib','i386'),
                 os.path.join(starpath, 'starjava', 'lib', 'x86_64')]
else:
    ld_environ = 'LD_LIBRARY_PATH'
    javapaths = [os.path.join(starpath, 'starjava', 'lib', 'amd64')]



starlib = os.path.join(starpath, 'lib')

ldpath = env[ld_environ].split(os.path.pathsep)

if not starlib in ldpath:
    ldpath.append(starlib)
for jp in javapaths:
    if not jp in ldpath:
        ldpath.append(jp)

env[ld_environ] = os.path.pathsep.join(ldpath)


#------------------------------------------
# Set up ADAM directory.

# ADAM dir used will be a termporary file in the current directory,
# that should be automatically deleted when python closes.
adamdir = os.path.relpath(tempfile.mkdtemp(prefix='tmpADAM', dir=os.getcwd()))
atexit.register(shutil.rmtree, adamdir)

# Set this ADAM_USER to be used
env['ADAM_USER'] = adamdir

# Don't ever prompt user for input.
env["ADAM_NOPROMPT"] = "1"

# Produce error codes if starlink command fails.
env['ADAM_EXIT'] = '1'

# Note that this will still only write error messages to stdin,
# not to stderr.

# Allow user to turn on prompting for values if needed.
def set_interactive(choice):

    """
    Function to turn on and off allowing starlink commands to prompt
    the user for values. Not recommended for scripts, but may be
    useful for identifying errors.

    If True, starlink commands can request input from command line.
    If False, set the star module to never prompt for values.

    Uses ADAM_NOPROMPT environmental variable.

    """

    env["ADAM_NOPROMPT"] = str(int(not bool(choice)))


# Set the starlink parameter QUIET to True.
QUIET = True

# Don't use current/last values as default
RESET = True

#--------------------convert utilities

# Dictionary of values for doing automatic conversion to and from
# non-ndf data formats (to be turned into environ variables).
condict = {
    'NDF_DEL_GASP': "f='^dir^name';touch $f.hdr $f.dat;rm $f.hdr $f.dat",
    'NDF_DEL_IRAF': "f='^dir^name';touch $f.imh $f.pix;rm $f.imh $f.pix",

    'NDF_FORMATS_IN': 'FITS(.fit),FIGARO(.dst),IRAF(.imh),STREAM(.das),'
    'UNFORMATTED(.unf),UNF0(.dat),ASCII(.asc),TEXT(.txt),GIF(.gif),TIFF(.tif),'
    'GASP(.hdr),COMPRESSED(.sdf.Z),GZIP(.sdf.gz),FITS(.fits),FITS(.fts),'
    'FITS(.FTS),FITS(.FITS),FITS(.FIT),FITS(.lilo),FITS(.lihi),FITS(.silo),'
    'FITS(.sihi),FITS(.mxlo),FITS(.mxhi),FITS(.rilo),FITS(.rihi),FITS(.vdlo),'
    'FITS(.vdhi),STREAM(.str),FITSGZ(.fit.gz),FITSGZ(.fits.gz),'
    'FITSGZ(.fts.gz)',

    'NDF_FORMATS_OUT': '.,FITS(.fit),FITS(.fits),FIGARO(.dst),IRAF(.imh)'
    ',STREAM(.das),UNFORMATTED(.unf),UNF0(.dat),ASCII(.asc),TEXT(.txt),'
    'GIF(.gif),TIFF(.tif),GASP(.hdr),COMPRESSED(.sdf.Z),GZIP(.sdf.gz),'
    'FITSGZ(.fts.gz),FITSGZ(.fits.gz)',

    'NDF_FROM_ASCII': "$CONVERT_DIR/convertndf from '^fmt' '^dir' '^name' "
    "'^type' '^fxs' '^ndf'",

    'NDF_FROM_COMPRESSED': "$CONVERT_DIR/convertndf from '^fmt' '^dir' "
    "'^name' '^type' '^fxs' '^ndf'",

    'NDF_FROM_FIGARO': "$CONVERT_DIR/convertndf from '^fmt' '^dir' '^name' "
    "'^type' '^fxs' '^ndf'",

    'NDF_FROM_FITS': "$CONVERT_DIR/convertndf from '^fmt' '^dir' '^name' "
    "'^type' '^fxs' '^ndf'",

    'NDF_FROM_FITSGZ': "$CONVERT_DIR/convertndf from '^fmt' '^dir' '^name'"
    " '^type' '^fxs' '^ndf'",

    'NDF_FROM_GASP': "$CONVERT_DIR/convertndf from '^fmt' '^dir' '^name' "
    "'^type' '^fxs' '^ndf'",

    'NDF_FROM_GIF': "$CONVERT_DIR/convertndf from '^fmt' '^dir' '^name' "
    "'^type' '^fxs' '^ndf'",

    'NDF_FROM_GZIP': "$CONVERT_DIR/convertndf from '^fmt' '^dir' '^name' "
    "'^type' '^fxs' '^ndf'",

    'NDF_FROM_IRAF': "$CONVERT_DIR/convertndf from '^fmt' '^dir' '^name' "
    "'^type' '^fxs' '^ndf'",

    'NDF_FROM_STREAM': "$CONVERT_DIR/convertndf from '^fmt' '^dir' '^name' "
    "'^type' '^fxs' '^ndf'",

    'NDF_FROM_TEXT': "$CONVERT_DIR/convertndf from '^fmt' '^dir' '^name' "
    "'^type' '^fxs' '^ndf'",

    'NDF_FROM_TIFF': "$CxsONVERT_DIR/convertndf from '^fmt' '^dir' '^name' "
    "'^type' '^fxs' '^ndf'",

    'NDF_FROM_UNF0': "$CONVERT_DIR/convertndf from '^fmt' '^dir' '^name' "
    "'^type' '^fxs' '^ndf'",

    'NDF_FROM_UNFORMATTED': "$CONVERT_DIR/convertndf from '^fmt' '^dir' "
    "'^name' '^type' '^fxs' '^ndf'",

    'NDF_SHCVT': '0',
    'NDF_TEMP_COMPRESSED': 'temp_Z_^namecl',
    'NDF_TEMP_FITS': 'temp_fits_^namecl^fxscl',
    'NDF_TEMP_GZIP': 'temp_gz_^namecl',
    'NDF_TO_ASCII': "$CONVERT_DIR/convertndf to '^fmt' '^dir' '^name' "
    "'^type' '^fxs' '^ndf'",
    'NDF_TO_COMPRESSED': "$CONVERT_DIR/convertndf to '^fmt' '^dir' '^name' "
    "'^type' '^fxs' '^ndf'",
    'NDF_TO_FIGARO': "$CONVERT_DIR/convertndf to '^fmt' '^dir' '^name' "
    "'^type' '^fxs' '^ndf'",
    'NDF_TO_FITS': "$CONVERT_DIR/convertndf to '^fmt' '^dir' '^name' "
    "'^type' '^fxs' '^ndf'",
    'NDF_TO_FITSGZ': "$CONVERT_DIR/convertndf to '^fmt' '^dir' '^name' "
    "'^type' '^fxs' '^ndf'",
    'NDF_TO_GASP': "$CONVERT_DIR/convertndf to '^fmt' '^dir' '^name' "
    "'^type' '^fxs' '^ndf'",
    'NDF_TO_GIF': "$CONVERT_DIR/convertndf to '^fmt' '^dir' '^name' "
    "'^type' '^fxs' '^ndf'",
    'NDF_TO_GZIP': "$CONVERT_DIR/convertndf to '^fmt' '^dir' '^name' "
    "'^type' '^fxs' '^ndf'",
    'NDF_TO_IRAF': "$CONVERT_DIR/convertndf to '^fmt' '^dir' '^name' "
    "'^type' '^fxs' '^ndf'",
    'NDF_TO_STREAM': "$CONVERT_DIR/convertndf to '^fmt' '^dir' '^name' "
    "'^type' '^fxs' '^ndf'",
    'NDF_TO_TEXT': "$CONVERT_DIR/convertndf to '^fmt' '^dir' '^name' "
    "'^type' '^fxs' '^ndf'",
    'NDF_TO_TIFF': "$CONVERT_DIR/convertndf to '^fmt' '^dir' '^name' "
    "'^type' '^fxs' '^ndf'",
    'NDF_TO_UNF0': "$CONVERT_DIR/convertndf to '^fmt' '^dir' '^name' "
    "'^type' '^fxs' '^ndf'",
    'NDF_TO_UNFORMATTED': "$CONVERT_DIR/convertndf to '^fmt' '^dir' "
    "'^name' '^type' '^fxs' '^ndf'"
    }


# add these to the environment variables
env.update(condict)


# Set up various starlink variables -- not all of these are probably needed...
env['CONVERT_DIR'] = os.path.join(starpath,'bin', 'convert')
env['SMURF_DIR'] = os.path.join(starpath,'bin', 'smurf')
env['KAPPA_DIR'] = os.path.join(starpath,'bin', 'kappa')
env['CUPID_DIR'] = os.path.join(starpath,'bin','cupid')
env['PGPLOT_DIR'] = os.path.join(starpath, 'bin')
env['STARLINK_DIR'] = starpath
#-----------------------------------------------------------------------

# Basic command to execute a starlink application
def star(command, *args, **kwargs):
    """Execute a Starlink application

    Carries out the starlink command, and returns a namedtuple of the
    starlink parameter values (taken from $ADAM_DIR/<com>.sdf

    Args:
        com (str): path of command, e.g. '$KAPPADIR/stats' or '$SMURFDIR/makecube'

    Kwargs:
        returnStdOut (bool): return the commands std out as string

    Other arguments and keyword arguments are evaluated by the command
    being called. Please see the Starlink documentation for the command.

    Returns:
       namedtuple: all the input and output params for this command.

       (if returnStdOut=True: also returns the stdout as a string)

    Usage:
        res = star('kappa', 'stats', ndf='myndf.sdf', order=True)

    Notes:

       Starlink keywords that are reserved python names (e.g. 'in')
       can be called by appending an underscore. E.g.: in_='myndf.sdf'.

    """

    # Get the requested command as a path
    compath = os.path.join(starpath, 'bin', module, com)
    try:
        returnStdOut = kwargs.pop('returnStdOut')
    except KeyError:
        returnStdOut = False

    # Ensure using lowercase for all kwargs.
    kwargs = dict((k.lower(), v) for k, v in kwargs.items())

    # If quiet not set in kwargs, then default to current module
    # default (variable QUIET).
    if not 'quiet' in kwargs and com not in {'jsasplit.py', 'picard_start.sh'}:
        kwargs['quiet'] = QUIET

    # Turn args and kwargs into a single list appropriate for sending to
    # subprocess.Popen.
    arg = _make_argument_list(*args, **kwargs)

    if RESET:
        arg += ['RESET']

    try:
        logger.debug([compath]+arg)

        # Call the process: note errors are written to stdout rather
        # than stderr, so we have to redirect that as well.
        proc = subprocess.Popen([compath]+arg, env=env, shell=False,
                                stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        status = proc.returncode

        # If there was an error, raise a python error and print the
        # starlink output to screen.
        if status != 0:
            raise StandardError('Starlink error occured during command:\n'
                                '%s %s\n ' % (compath, arg) +
                                'stdout and stderr are appended below.\n'
                                + stdout + '\n' + stderr)
        else:
            if stdout != '':
                logger.debug(stdout)

            # Get the parameters for the command from $ADAMDIR/com.sdf:
            result = get_hds_values(com)

            if returnStdOut:
                result = (result, stdout)

            return result

    # Catch errors relating to a non existent command name separately
    # and raise a useful error message.
    except OSError as err:
        if err.errno == 2:
            raise OSError('command %s does not exist; '
                          'perhaps you have mistyped it?'
                          % compath)
        else:
            raise err



def _make_argument_list(*args, **kwargs):
    """

    Turn pythonic list of positional arguments and keyword arguments
    into a list of strings.

    TODO: this should really be more thoroughly checked.

    N.B.: subprocess.Popen works best with each argument as item in
    list, not as a single string. Otherwise it breaks on starlink
    commands that are really python scripts.

    """
    output = []

    # Go through each positional argument.
    for i in args:
        output.append(str(i) + ' ')

    # Go through each keyword argument.
    for key, value in kwargs.items():
        # Strip out trailing '_' (used for starlink keywords that are
        # python reserved words).
        if key[-1] == '_':
            key = key[:-1]
        output.append(str(key)+'='+str(value))

    # Remove trailing space
    output = [i.rstrip() for i in output]

    # Return list of arguments (as a list).
    return output


#set of convenience functions to call commands from different starlink modules.
def kappa(com, *arg, **kwargs):
    """Execute a kappa command."""
    return star('kappa', com, *arg, **kwargs)


def smurf(com, *arg, **kwargs):
    """Execute smurf command."""

    return star('smurf', com, *arg, **kwargs)


def cupid(com, *arg, **kwargs):
    """Execute cupid command."""
    return star('cupid', com, *arg, **kwargs)


def convert(com, *arg, **kwargs):
    """Execute convert command."""
    return star('convert', com, *arg, **kwargs)



class StarError(StandardError):
    def __init__(self, compath, arg, stderr):
        message = 'Starlink error occured during:\n %s %s\n ' % (compath, arg)
        message += '\nThere should be an error message printed to stdout '
        message += '(check above this traceback in ipython)'+stderr
        StandardError.__init__(self, message)


def get_fitshdr(datafile, form='sdf'):
    """
    Return a astropy.io.fits header object.

    kwarg:
    form (str): can be 'sdf' or 'fits'

    """


    if form == 'sdf':
        ndf = ndfpack.Ndf(datafile)
        fitshead = ndf.head['FITS']
        hdr = fits.Header.fromstring('\n'.join(fitshead), sep='\n')

    elif form == 'fits':
        hdr = fits.getheader(datafile)

    else:
        raise StandardError('Unknown file format %s: form must be "sdf" or "fits"' %  form)

    return hdr




def get_hds_values(comname):

    """
    Return a namedtuple with all the values
    from the ADAMDIR/commname.sdf hds file.
    """

    hdsobj = hds.open(os.path.join(adamdir, comname), 'READ')

    # Iterate through it to get all the results.
    results = _hds_iterate_components(hdsobj)

    # Remove the 'ADAM_DYNDEF' component as it never exits?
    if results.has_key('adam_dyndef'):
        results.pop('adam_dyndef')

    # Fix up the nameptr values (if they are the only thing in the
    # dictionary)
    fixuplist = [i for i in results.keys()
                 if (isinstance(results[i], dict) and results[i].keys()==['nameptr'])]

    for i in fixuplist:
        results[i] = results[i]['nameptr']

    class starresults( namedtuple(comname, results.keys()) ):
        def __repr__(self):
            return _hdstrace_print(self)

    result = starresults(**results)

    return result



def _hds_value_get(hdscomp):
    """
    Get a value from an HDS component.

     - adds an '_' to any python reserved keywords.
     - strip white space from strings.

    Return tuple of name, value and type.
    """
    name = hdscomp.name.lower()
    if iskeyword(name):
        name += '_'
    value = hdscomp.get()

    # Remove white space from string objects.
    if 'char' in hdscomp.type.lower():
        if hdscomp.shape:
            value = [i.strip() for i in value]
        else:
            value = value.strip()

    type_ = hdscomp.type
    return name, value, type_



def _hds_iterate_components(hdscomp):

    """Iterate through HDS structure.

    Return nested dictionaries representing the object.

    """
    results_dict={}
    for i in range(hdscomp.ncomp):
        subcomp = hdscomp.index(i)
        if subcomp.struc:
            name = subcomp.name.lower()
            if iskeyword(name):
                name += '_'
            results_dict[name] = _hds_iterate_components(subcomp)
        else:
            name, value, type_ = _hds_value_get(subcomp)
            results_dict[name] = value
    return results_dict



def _hdstrace_print(self):

    """
    Print the results of get_hds_values prettily.
    """
    output = []
    maxlength = len(max(self._fields, key=len))
    space = 4

    for i in self._asdict().items():

        if isinstance(i[1], list) and len(str(i[1])) > 79 - maxlength - space:
            j = ['['+' ' + str(i[1][0])] +  \
                [' '*(maxlength+space+2) + str(n) for n in i[1][1:]] + \
                [' '*(maxlength+space) + ']']
            value = '\n'.join(j)
        else:
            value = i[1]
        output.append('{:>{width}}'.format(str(i[0]), width=maxlength) + ' '*space + str(value))
    return '\n'.join(output)




