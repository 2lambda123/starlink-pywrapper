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



# Default starpath to use (if installing outside of Starlink, you may
# wish to set this to the location of your $STARLINK_DIR).
default_starpath = None



# Subprocess fix for sig pipe? Attempt to solve zombie monolith problem.
# TODO check if this should be used?
# Graham thinks it should be given to preexec_fn.
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

# Starlink environ variables that are relative to STARLINK_DIR
starlink_environdict_substitute = {
    "ATOOLS_DIR": "bin/atools",
    "AUTOASTROM_DIR": "Perl/bin",
    "CCDPACK_DIR": "bin/ccdpack",
    "CONVERT_DIR": "bin/convert",
    "CUPID_DIR": "bin/cupid",
    "CURSA_DIR": "bin/cursa",
    "DAOPHOT_DIR": "bin/daophot",
    "DATACUBE_DIR": "bin/datacube",
    "DIPSO_DIR": "bin/dipso",
    "ECHOMOP_DIR": "bin/echomop",
    "ESP_DIR": "bin/esp",
    "EXTRACTOR_DIR": "bin/extractor",
    "FIG_DIR": "bin/figaro",
    "FLUXES_DIR": "bin/fluxes",
    "FROG_DIR": "starjava/bin/frog",
    "GAIA_DIR": "bin/gaia",
    "HDSTOOLS_DIR": "bin/hdstools",
    "HDSTRACE_DIR": "bin",
    "KAPPA_DIR": "bin/kappa",
    "ORAC_DIR": "bin/oracdr/src",
    "PAMELA_DIR": "bin/pamela",
    "PERIOD_DIR": "bin/period",
    "PGPLOT_DIR": "bin/",
    "PHOTOM_DIR": "bin/photom",
    "PISA_DIR": "bin/pisa",
    "POLPACK_DIR": "bin/polpack",
    "SMURF_DIR": "bin/smurf",
    "SPLAT_DIR": "starjava/bin/splat",
    "SST_DIR": "bin/sst",
    "STILTS_DIR": "starjava/bin/stilts",
    "SURF_DIR": "bin/surf",
    "TSP_DIR": "bin/tsp",
    "STARLINK_DIR": "",
}


# Not setting up the _HELP directories.
# Also not setting up: ADAM_PACKAGES, ICL_LOGIN_SYS, FIG_HTML, PONGO_EXAMPLES,
# Miscellaneous other ones, probably not useful (all relative to STARLINK_DIR)
starlink_other_variables = {
    "FIGARO_PROG_N": "bin/figaro",
    "FIGARO_PROG_S": "etc/figaro",
    "ORAC_CAL_ROOT": "bin/oracdr/cal",
    "ORAC_PERL5LIB": "bin/oracdr/src/lib/perl5/",
    "PONGO_BIN": "bin/pongo",
    "SYS_SPECX": "share/specx",
    }


def setup_starlink_environ(starpath, adamdir,
                           noprompt=True):

    """
    Create a suitable ENV dict to pass to subprocess.Popen
    """

    env = {}
    env['STARLINK_DIR'] = starpath
    env['AGI_USER'] = os.path.join(adamdir)

    # Add on the STARLINK libraries to the environmental path
    # Skip if on Mac, where we shouldn't need DYLD_LIBRARY_PATH?
    #if sys.platform == 'darwin':
    #    ld_environ = 'DYLD_LIBRARY_PATH'
    #    javapaths = [os.path.join(starpath,'starjava', 'lib','i386'),
    #                 os.path.join(starpath, 'starjava', 'lib', 'x86_64')]
    if sys.platform != 'darwin':
        ld_environ = 'LD_LIBRARY_PATH'
        javapaths = [os.path.join(starpath, 'starjava', 'lib', 'amd64')]

        starlib = os.path.join(starpath, 'lib')
        starldlibpath = os.path.pathsep.join([starlib] + javapaths)
        env[ld_environ] = starldlibpath

    # Don't ever prompt user for input.
    if noprompt:
        env["ADAM_NOPROMPT"] = "1"
        env["STARUTIL_NOPROMPT"] = "1"

    # Produce error codes if starlink command fails.
    # Note that this will still only write error messages to stdin,
    # not to stderr.
    env['ADAM_EXIT'] = '1'

    # Set this ADAM_USER to be used
    env['ADAM_USER'] = adamdir

    # Add the CONVERT environ variables to the env.
    env.update(condict)

    # Set up various starlink variables
    # Package directories -- e.g. KAPPA_DIR etc names
    for module_env, modulepath in starlink_environdict_substitute.items():
        env[module_env] = os.path.join(starpath, modulepath)

    for environvar, relvalue in starlink_other_variables.items():
        env[environvar] = os.path.join(starpath, relvalue)

    # Perl 5 libraries:
    env['PERL5LIB'] = os.path.join(starpath, 'Perl', 'lib', 'perl5', 'site_perl') + \
                      os.path.pathsep + os.path.join(starpath, 'Perl', 'lib', 'perl5')

    # Setting up the Path (note that we are using shell=False)
    originalpath = os.environ['PATH']
    env['PATH'] = os.path.pathsep.join([os.path.join(starpath, 'bin'),
                                    os.path.join(starpath, 'starjava', 'bin'),
                                    originalpath])

    # Add DISPLAY, for X stuff
    if 'DISPLAY' in os.environ:
        env['DISPLAY'] = os.environ['DISPLAY']

    return env

def change_starpath(starlinkdir):
    """
    Change the $STARLINK_DIR used by this module.

    Note that this needs to change the module level env and starpath
    variables.

    """

    global env
    global starpath
    env = setup_starlink_environ(starlinkdir,
                                 adamdir,
                                 noprompt=True)
    starpath = starlinkdir



# Basic command to execute a starlink application
def starcomm(command, commandname, *args, **kwargs):
    """Execute a Starlink application

    Carries out the starlink command, and returns a namedtuple of the
    starlink parameter values (taken from $ADAM_DIR/<com>.sdf

    Args:
        command (str): path of command to run, e.g. '$SMURFDIR/makecube'
        commandname (str): name of command (used for getting output values)

    Keyword arguments:
        returnStdOut (bool): return the commands std out as string

    Other arguments and keyword arguments are evaluated by the command
    being called. Please see the Starlink documentation for the command.
    The standard Starlink package environmental varaibles (e.g. KAPPA_DIR,
    SMURF_DIR etc.) can be used inside the command name.

    Returns:
       namedtuple: all the input and output params for this command.
       stdout: the stdout as a string (only returned if returnStdOut=True)

    Example:
        res = starcomm('$KAPPA_DIR/stats', 'stats', ndf='myndf.sdf')

    Notes:
       Starlink parameters or functions that are reserved python names
       (e.g. 'in') can be called by appending an underscore. E.g.:
       in_='myndf.sdf'.

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

    ## Append 'RESET' to args list?
    # This doesn't work with starutil python scripts, e.g. jsasplit...
    #arg += ['RESET']

    try:
        logger.debug([command]+arg)

        # Replace things like ${KAPPA_DIR} and $KAPPA_DIR with the
        # KAPPA_DIR value.
        for i, j in starlink_environdict_substitute.items():
            command = command.replace('$' + i, env[i])
            command = command.replace('${' + i + '}', env[i])

            # Call the process: note errors are written to stdout rather
        # than stderr, so we have to redirect that as well.
        proc = subprocess.Popen([command] + arg, env=env, shell=False,
                                stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        status = proc.returncode
        if stderr:
            logger.info(stderr)

        # If there was an error, raise a python error and print the
        # starlink output to screen.
        if status != 0:
            raise Exception('Starlink error occured during command:\n'
                                '%s %s\n ' % (command, arg) +
                                'stdout and stderr are appended below.\n'
                                + stdout + '\n' + stderr)
        else:

            # Show stdout as a debug log.
            if stdout:
                logger.debug(stdout)

            # Get the parameters for the command from $ADAMDIR/commandname.sdf:
            result = hdsutils.get_hds_values(commandname, adamdir)

            # If the magic keyword returnStdOut was set:
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



class StarError(Exception):
    def __init__(self, command, arg, stderr):
        message = 'Starlink error occured during:\n %s %s\n ' % (commandh, arg)
        message += '\nThere should be an error message printed to stdout '
        message += '(check above this traceback in ipython)'+stderr
        Exception.__init__(self, message)


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

# Values for finding out if the package is inside a Starlink installation.
relative_testfile = '../../bin/smurf/makemap'
testfile_to_starlink = '../../../'

starpath = None
env = None


# Find STARLINK_DIR, or warn user to check.
if default_starpath:
    starpath = default_starpath
    logger.info('Using default Starlink path {}'.format(starpath))
else:
    try:
        starpath = os.path.abspath(os.environ['STARLINK_DIR'])
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
            logger.warning('Could not find Starlink: please run change_starpath("/path/to/star")')

# ADAM_USER: set this to temporary directory in the current directory,
# that should be automatically deleted when python closes.
adamdir = os.path.relpath(tempfile.mkdtemp(prefix='tmpADAM', dir=os.getcwd()))
atexit.register(shutil.rmtree, adamdir)

# If we found a starpath, set it up
if starpath:
    env = setup_starlink_environ(starpath,  adamdir)
