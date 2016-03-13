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

"""
Low level functions for running Starlink commands from python.

"""

import atexit
import logging
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile


from collections import namedtuple


from . import hdsutils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

testvariable = True


# Subprocess fix for sig pipe? Attempt to solve a problem
def subprocess_setup():
    # Python installs a SIGPIPE handler by default. This is usually
    # not what non-Python subprocesses expect.
    signal.signal(signal.SIGXFSZ, signal.SIG_DFL)
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)



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





def setup_starlink_environ(starpath, adamdir,
                           noprompt=True):

    env = {}
    # Add on the STARLINK libraries to the environmental path
    # LD_LIBRARY_PATH (linux) or DYLD_LIBRARY_PATH (mac)
    if sys.platform == 'darwin':
        ld_environ = 'DYLD_LIBRARY_PATH'
        javapaths = [os.path.join(starpath,'starjava', 'lib','i386'),
                     os.path.join(starpath, 'starjava', 'lib', 'x86_64')]
    elif sys.platform != 'darwin':
        ld_environ = 'LD_LIBRARY_PATH'
        javapaths = [os.path.join(starpath, 'starjava', 'lib', 'amd64')]


    starlib = os.path.join(starpath, 'lib')

    #ldpath = env[ld_environ].split(os.path.pathsep)
    ldpath = []
    if not starlib in ldpath:
        ldpath.append(starlib)
    for jp in javapaths:
        if not jp in ldpath:
            ldpath.append(jp)

    env[ld_environ] = os.path.pathsep.join(ldpath)

    # Don't ever prompt user for input.
    if noprompt:
        env["ADAM_NOPROMPT"] = "1"

    # Produce error codes if starlink command fails.
    env['ADAM_EXIT'] = '1'

    # Set this ADAM_USER to be used
    env['ADAM_USER'] = adamdir

    # add these to the environment variables
    env.update(condict)

    # Set up various starlink variables -- not all of these are probably needed...
    env['CONVERT_DIR'] = os.path.join(starpath,'bin', 'convert')
    env['SMURF_DIR'] = os.path.join(starpath,'bin', 'smurf')
    env['KAPPA_DIR'] = os.path.join(starpath,'bin', 'kappa')
    env['CUPID_DIR'] = os.path.join(starpath,'bin','cupid')
    env['PGPLOT_DIR'] = os.path.join(starpath, 'bin')
    for i in ['CONVERT_DIR', 'SMURF_DIR', 'KAPPA_DIR', 'CUPID_DIR', 'PGPLOT_DIR']:
        substitution_dict[i] = env[i]

    env['STARLINK_DIR'] = starpath

    # Note that this will still only write error messages to stdin,
    # not to stderr.
    return env




# Basic command to execute a starlink application
def starcomm(command, commandname, *args, **kwargs):
    """Execute a Starlink application

    Carries out the starlink command, and returns a namedtuple of the
    starlink parameter values (taken from $ADAM_DIR/<com>.sdf

    Args:
        command (str): path of command, e.g. '$KAPPADIR/stats' or '$SMURFDIR/makecube'
        commandname (str): name of command (used for getting output valeus)

    Kwargs:
        returnStdOut (bool): return the commands std out as string

    Other arguments and keyword arguments are evaluated by the command
    being called. Please see the Starlink documentation for the command.

    Returns:
       namedtuple: all the input and output params for this command.

       (if returnStdOut=True: also returns the stdout as a string, in form:
       (namedtuple, stdout) = starcomm(command *args, **kwargs)

    Usage:
        res = star('kappa', 'stats', ndf='myndf.sdf', order=True)

    Notes:

       Starlink keywords that are reserved python names (e.g. 'in')
       can be called by appending an underscore. E.g.: in_='myndf.sdf'.

    """

    # Ensure using lowercase for all kwargs.
    kwargs = dict((k.lower(), v) for k, v in kwargs.items())


    # If quiet not set in kwargs, then default to current module
    # default (variable QUIET).
    #if not 'quiet' in kwargs and com not in {'jsasplit.py', 'picard_start.sh'}:
    #    kwargs['quiet'] = QUIET

    returnStdOut = kwargs.get('returnStdOut', False)
        
    # Turn args and kwargs into a single list appropriate for sending to
    # subprocess.Popen.
    arg = _make_argument_list(*args, **kwargs)

    #if RESET:
    #    arg += ['RESET']

    try:
        logger.debug([command]+arg)

        for i in substitution_dict.keys():
            command = command.replace('$' + i, substitution_dict[i])
            command = command.replace('${' + i + '}', substitution_dict[i])
                
        # Call the process: note errors are written to stdout rather
        # than stderr, so we have to redirect that as well.
        proc = subprocess.Popen([command]+arg, env=env, shell=False,
                                stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        status = proc.returncode

        # If there was an error, raise a python error and print the
        # starlink output to screen.
        if status != 0:
            raise StandardError('Starlink error occured during command:\n'
                                '%s %s\n ' % (command, arg) +
                                'stdout and stderr are appended below.\n'
                                + stdout + '\n' + stderr)
        else:
            if stdout != '':
                logger.debug(stdout)

            # Get the parameters for the command from $ADAMDIR/commandname.sdf:
            result = hdsutils.get_hds_values(commandname, adamdir)

            # If the magic kewyrod 
            if returnStdOut:
                result = (result, stdout)

            return result

    # Catch errors relating to a non existent command name separately
    # and raise a useful error message.
    except OSError as err:
        if err.errno == 2:
            raise OSError('command %s does not exist; '
                          'perhaps you have mistyped it?'
                          % command)
        else:
            raise err



class StarError(StandardError):
    def __init__(self, command, arg, stderr):
        message = 'Starlink error occured during:\n %s %s\n ' % (commandh, arg)
        message += '\nThere should be an error message printed to stdout '
        message += '(check above this traceback in ipython)'+stderr
        StandardError.__init__(self, message)


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




#-------------

# Setup the adamdirectory:

# Get the starpath

relative_testfile = '../../bin/smurf/makemap'
testfile_to_starlink = '../../../'
default_starpath = None
starpath = None
env = None
substitution_dict = {}

if default_starpath:
    starpath = default_starpath
    logger.info('Using default Starlink path {}'.format(starpath))
else:
    try:
        starpath = os.path.join(os.environ['STARLINK_DIR'])
        logger.info('Using $STARLINK_DIR starlink at {}'.format(starpath))
    except KeyError:
        # See if we are installed inside a starlink system?  Very
        # crude. Assume that there will be a file 'relative_testfile' at that location.
        module_path = os.path.split(os.path.abspath(__file__))[0]
        if os.path.isfile(os.path.join(module_path, relative_testfile)):
            starpath = os.path.abspath(os.path.join(module_path, relative_testfile,
                                                    testfile_to_starlink))
            logger.info('Using Starlink at {}.'.format(starpath))

        else:
            logger.warning('Could not find Starlink: please run set_starpath("/path/to/star")')

# ADAM dir used will be a termporary file in the current directory,
# that should be automatically deleted when python closes.
adamdir = os.path.relpath(tempfile.mkdtemp(prefix='tmpADAM', dir=os.getcwd()))
atexit.register(shutil.rmtree, adamdir)


# Actually setup starlink environment
if starpath:
    env = setup_starlink_environ(starpath,  adamdir)
    
