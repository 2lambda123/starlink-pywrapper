# Copyright (C) 2013-2014 Science and Technology Facilities Council.
# Copyright (C) 2015-2018 East Asian Observatory
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
starlink.wrapper: Module for running starlink commands from python.

This uses subprocess.Popen to run Starlink commands, and requires a
separate installation of the Starlink Software Suite.

It allows you to use a standard formatted keyword arguments
to call the starlink commands. Shell escapes do not need to be used.

By default, when you run commands using this module it will create a
new temporary ADAM directory in the current folder, and use that as
the ADAM directory for the starlink processes. In order to avoid
returning values from a previous run, it will delete the
<commandname>.sdf files from the ADAM directory after reading them
back in.

This code was written to allow quick calling of kappa, smurf and cupid
in the way I usually think about them from python scripts, with
regular keyword variables.

Its recommended to set STARLINK_DIR in your environment before opening
python to run this software.
"""

import atexit
import glob
import logging
import os
import shutil
import signal
import subprocess
import sys
import time
import tempfile

try:
    basestring=basestring
except NameError:
    basestring=(str, bytes)

from collections import namedtuple


from . import hdsutils

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

xwindow_names = {
    "xw" : "xwindows",
    "x2w" : "xwindows2",
    "x3w" : "xwindows3",
    "x4w" : "xwindows4",
    "xwindows" : "xwindows",
    "x2windows" : "xwindows2",
    "x3windows" : "xwindows3",
    "x4windows" : "xwindows4"
}

# Return type for PICARD and ORAC-DR
oracoutput = namedtuple('oracoutput', 'runlog outdir datafiles imagefiles logfiles status pid')

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

    # don't let the MERS library split long lines?
    env['MSG_SZOUT'] = "0"

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
    env['PATH'] = os.path.pathsep.join([
                                    os.path.join(starpath, 'bin', 'startcl'),
                                    os.path.join(starpath, 'bin'),
                                    os.path.join(starpath, 'starjava', 'bin'),
                                    originalpath])

    # Add DISPLAY, for X stuff
    if 'DISPLAY' in os.environ:
        env['DISPLAY'] = os.environ['DISPLAY']

    return env

def change_starpath(starlinkdir):
    """
    Change the $STARLINK_DIR used by this module.

    Note that this changes the module level env and starpath
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

    Arguments
    ---------
    command: str
       The path of a command to run, e.g. '$SMURFDIR/makecube'

    commandname: str
       The name of command (used for getting output values).

    Keyword arguments
    -----------------
    returnstdout: bool

        Have the string that would have been written to stdout in a
        normal starlink session be returned from this function as a
        string.


    Other arguments and keyword arguments are evaluated by the command
    being called. Please see the Starlink documentation for the command.
    The standard Starlink package environmental variables (e.g. KAPPA_DIR,
    SMURF_DIR etc.) can be used inside the command name.

    Returns
    -------

       namedtuple: Containing all the input and output params for this command as attributes.
       stdout: the stdout as a string (only returned if returnStdOut=True)

    Example
    -------

    >>> res = starcomm('$KAPPA_DIR/stats', 'stats', ndf='myndf.sdf')

    Notes
    -----

    Starlink parameters or functions that are reserved python names
    (e.g. 'in') can be called by appending an underscore. E.g.

    >>> in_='myndf.sdf'

    """

    # Ensure using lowercase for all kwargs.
    kwargs = dict((k.lower(), v) for k, v in kwargs.items())


    # If quiet not set in kwargs, then default to current module
    # default (variable QUIET).
    #if not 'quiet' in kwargs and com not in {'jsasplit.py', 'picard_start.sh'}:
    #    kwargs['quiet'] = QUIET

    if 'returnstdout' in kwargs:
        returnStdOut = kwargs.pop('returnstdout')
    else:
        returnStdOut = False

    # Turn args and kwargs into a single list appropriate for sending to
    # subprocess.Popen.
    arg = _make_argument_list(*args, **kwargs)

    ## Append 'RESET' to args list?
    # This doesn't work with starutil python scripts, e.g. jsasplit...
    #arg += ['RESET']

    try:
        # Replace things like ${KAPPA_DIR} and $KAPPA_DIR with the
        # KAPPA_DIR value.
        for i, j in starlink_environdict_substitute.items():
            command = command.replace('$' + i, env[i])
            command = command.replace('${' + i + '}', env[i])


        # Check if there is a 'device' keyword? NB this won't work if
        # it is an argument...
        xmake = False
        if 'device' in kwargs:
            if kwargs['device'].endswith('/GWM'):
                xmake = True
                gdname = kwargs['device'].split('/GWM')[0]
            elif kwargs['device'] in xwindow_names:
                xmake = True
                gdname = xwindow_names[kwargs['device']]

        if xmake:
            logger.info('Creating xwindow named {}'.format(gdname))
            xmakecomm = os.path.join(env['STARLINK_DIR'], 'bin', 'xmake')
            logger.debug('{} {}'.format(xmakecomm, gdname))
            p=subprocess.Popen([xmakecomm, gdname], env=env)
            p.wait()

        logger.debug([command] + arg)
        proc = subprocess.Popen([command] + arg, env=env, shell=False,
                                stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        status = proc.returncode
        if stderr:
            logger.info(stderr)

        # If there was an error, raise a python error and print the
        # starlink output to screen.
        if status != 0:
            message = ('Starlink error occured during command:\n'
                       '{} {}\n '
                       'stdout and stderr are appended below.\n{}\n{}')
            message = message.format(command, args, stdout.decode(), stderr.decode())

            # Also delete the adam output file, as it may be corrupt
            # or contain something we don't want propogating.
            adamfile = os.path.join(adamdir, commandname + '.sdf')
            if os.path.isfile(adamfile):
                os.remove(adamfile)
            else:
                logger.debug('{} does not exist'.format(adamfile))

            raise Exception(message)

        else:

            # Show stdout as a debug log.
            if stdout:
                logger.debug(stdout.decode())

            # Get the parameters for the command from $ADAMDIR/commandname.sdf:
            result = hdsutils.get_adam_hds_values(commandname, adamdir)

            # Delete the $ADAMDIR/commandname.sdf file if it
            # exists. This is to prevent issues where an output
            # parameter is created in one call of a command, but
            # doesn't get created in another call. As starlink won't
            # delete the redundant information from the HDS file, the
            # whole file must be manually deleted. E.g. if you call
            # 'stats myndf.sdf order=True' you will have a median in
            # the output values. If you then call 'stats
            # myotherndf.sdf order=False' you will still get a median
            # returned, but it will have been returned from the
            # previous call. Using RESET does not clean out the output
            # parameters from a previous call.
            adamfile = os.path.join(adamdir, commandname + '.sdf')
            if os.path.isfile(adamfile):
                os.remove(adamfile)
            else:
                logger.debug('{} does not exist'.format(adamfile))

            # If the magic keyword returnStdOut was set:
            if returnStdOut:
                result = (result, stdout.decode())

            return result

    # Catch errors relating to a non existent command name separately
    # and raise a useful error message.
    except OSError as err:
        if err.errno == 2:
            logger.error('command %s does not exist; '
                          'perhaps you have mistyped it?'
                          % command)
            raise err
        else:
            raise err



class StarError(Exception):
    def __init__(self, command, arg, stderr):
        message = 'Starlink error occured during:\n %s %s\n ' % (commandh, arg)
        message += '\nThere should be an error message printed to stdout '
        message += '(check above this traceback)'+stderr
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


JCMTINST = ['ACSIS', 'SCUBA2_850', 'SCUBA2_450', 'SCUBA', 'JCMTDAS', ]
UKIRTINST = ['CGS4', 'CLASSICCAM', 'GMOS', 'INGRID', 'IRCAM2', 'IRCAM',
             'IRIS2', 'ISAAC', 'MICHELLE', 'NACO', 'OCGS4', 'SOFI', 'SPEX', 'START', 'UFTI', 'UFTI_OLD']

ORACDR_DATA_IN_PATHS = {
    'ACSIS': '/jcmtdata/raw/acsis/spectra',
    'SCUBA2': '/jcmtdata/raw/scuba2/ok',
}


def oracdr_envsetup(instrument, utdate=None, ORAC_DIR=None,
                    ORAC_DATA_IN=None, ORAC_DATA_OUT=None,
                    ORAC_CAL_ROOT=None, ORAC_DATA_CAL=None,
                    ORAC_PERL5LIB=None):
    """
    Setup the various ORAC-DR environmental variables.

    Uses the modules 'env' variable as a starting point (via a copy).

    Returns an updated environment dictionary.

    """
    oracenv = env.copy()
    if not utdate:
        utdate = time.strftime('%Y%M%d')
    else:
        utdate = str(utdate)

    instrument = instrument.upper()
    logger.debug('Setting $INSTRUMENT to {}.'.format(instrument))
    oracenv['ORAC_INSTRUMENT'] = instrument

    # Data & cal directories (see orac_calc_instrument settings?)
    if not ORAC_DATA_IN:
        if ('SCUBA2' in instrument) or ('SCUBA-2'  in instrument):
            ORAC_DATA_IN = os.path.join(ORACDR_DATA_IN_PATHS['SCUBA2'], utdate)
        elif instrument.upper() in ORACDR_DATA_IN_PATHS:
            ORAC_DATA_IN = os.path.join(ORACDR_DATA_IN_PATHS[instrument.upper()], utdate)
        else:
            if instrument in JCMTINST:
                ORAC_DATA_IN = os.path.join('/jcmtdata/raw/', instrument.lower(), utdate)
            elif instrument in UKIRTINST:
                ORAC_DATA_IN = os.path.join('/ukirtdata/raw/', instrument.lower(), utdate)
            else:
                logger.warning('Setting ORAC_DATA_IN to "/"')
                ORAC_DATA_IN = '/'

    oracenv['ORAC_DATA_IN'] = ORAC_DATA_IN
    logger.info('Setting ORAC_DATA_IN to {}'.format(ORAC_DATA_IN))
    if not ORAC_DATA_OUT:
        ORAC_DATA_OUT = os.getcwd()
        logger.info('Automatically setting ORAC_DATA_OUT to {}.'.format(ORAC_DATA_OUT))
    oracenv['ORAC_DATA_OUT'] = ORAC_DATA_OUT

    if not ORAC_DIR:
        ORAC_DIR = os.path.join(env['STARLINK_DIR'], 'bin', 'oracdr', 'src')
    oracenv['ORAC_DIR'] = ORAC_DIR

    if not ORAC_PERL5LIB:
        ORAC_PERL5LIB = os.path.join(ORAC_DIR, 'lib', 'perl5')
    oracenv['ORAC_PERL5LIB'] = ORAC_PERL5LIB

    if not ORAC_CAL_ROOT:
        ORAC_CAL_ROOT = os.path.join(ORAC_DIR, os.path.pardir, 'cal')
    oracenv['ORAC_CAL_ROOT'] = ORAC_CAL_ROOT

    if not ORAC_DATA_CAL:
        if 'SCUBA2' in instrument:
            ORAC_DATA_CAL = os.path.join(ORAC_CAL_ROOT, 'scuba2')
        else:
            ORAC_DATA_CAL = os.path.join(ORAC_CAL_ROOT, instrument.lower())
    oracenv['ORAC_DATA_CAL'] = ORAC_DATA_CAL
    oracenv['ORAC_LOOP'] = "flag -skip"


    # Used by oracdr to see if everything is setup right:
    oracenv['STAR_LOGIN'] = '1'

    return oracenv





def oracdr(instrument, loop='file', dataout=None,
           datain=None, recipe=None, recpars=None, onegroup=False,
           rawfiles=None, utdate=None, obslist=None,
           headeroverride=None, calib=None,
           verbose=False, debug=False, warn=False):
    """
    Run oracdr on a batch of files.

    Arguments
    ---------
    instrument: str
        Name of instrument

    Keyword Arguments
    -----------------

    loop: str
      'file' or 'list'. determine if input obs are specified as
      raw file names/paths or as a list of observation numbers and a
      utdate. ['file']

    dataout: str
       Location of output data directory; defaults to current dir.

    datain: str
       Location of input data; defaults to current dir.

    recipe str:
       Name of recipe to run. If None, use recipe from headers.

    recpars str:
       Value to pass as a recipe parameter option -- either a filename
       or the recpars themselves.

    onegroup: Bool
       Force all observations into one processing group.

    rawfiles:  str or list of filenames/paths
      If a string, this is a text file giving names of all input
      files. If list, then list of all input files as python
      list. Files are taken relative to datain, or can be given as
      absolute path. Only used if loop='file'

    utdate: int, YYYYMMDD
       The utdate of the input data. Only used if loop='list'

    obslist: List(int)
      List of input scan numbers. Input file names will be generated
      assuming JCMT/UKIRT directory structure, similar to
      <datain>/<utdate>/<scannumber>/rawfiles .

    headeroverride: str, filename
       File with optional header overrides.

    calib: str
       Calibration overrides. Accepts comma separated key=value pairs.

    verbose: bool
       Include output from Starlink commands in log/stdout.

    debug: bool
       Include debug output in log/stdout.

    warn: bool
       Show Perl warning messages.

    Returns
    -------

    Return value is a named tuple with the following attributes:

     - runlog: name of output logfile.
     - outputdir: path of output directory
     - datafiles: list of output data files.
     - imagefiles: list of output image files.
     - logfiles: list of log.* files
     - status: int, return code from suprocess.Popen
     - pid (int): pid of perl parent process.


    Notes
    -----
    This will *not* raise an exception if ORAC-DR ended with an error;
    it is up to the calling code to check the status if required.
    """

    instrument = instrument.upper()

    # Complain and exit about various impossible options:
    if loop not in ['file', 'list']:
        logger.error('Unrecognised option loop={},  should be "file" or "list"'.format(loop))
        raise Exception('Unrecognised option loop={}, should be loop="file" or loop="list"'.format(loop))

    elif loop == 'list' and (not utdate or not obslist):
        logger.error('When using loop="list" then utdate AND obslist must be given.')
        raise Exception('When using loop="list" then utdate AND obslist must be given.')

    elif loop == 'file' and not rawfiles:
        logger.error('When using loop="file" then rawfiles must be given.')
        raise Exception('When using loop="file" then rawfiles must be given.')


    if dataout:
        dataout = os.path.abspath(dataout)
        if not os.path.isdir(dataout):
            logger.error('Requested ORAC_DATA_OUT {} does not exist'.format(dataout))
            raise Exception('Requested ORAC_DATA_OUT {} does not exist'.format(dataout))
    else:
        dataout = os.getcwd()

    # Actually run in a temporary working directory in data out. Make that now.
    outputdir = os.path.abspath(tempfile.mkdtemp(prefix='ORACworking', dir=dataout))
    logger.debug('Working output directory for ORAC-DR is {}.'.format(outputdir))

    # Set up ORAC data in.
    if datain:
        datain = os.path.abspath(datain)
        if not os.path.isdir(datain):
            logger.warning('Requested DATA_IN directory {} does not exist'.format(
                datain))


    # If ORAC_DATA_IN is not set and using a provided set of files, assume it is the current directory, but warn the user about this.
    if not datain and not loop=="list":
        datain = os.path.curdir
        logger.info('Keyword Argument datain was not given, so defaulting to %s', datain)

    # Set up environmental variables to run ORAC succesfully.
    oracenv = oracdr_envsetup(instrument, utdate=utdate, ORAC_DIR=None,
                    ORAC_DATA_IN=datain, ORAC_DATA_OUT=outputdir,
                    ORAC_CAL_ROOT=None, ORAC_DATA_CAL=None,
                    ORAC_PERL5LIB=None)

    # If using loop=file get rawfiles into correct format.
    if loop=="file":


        if isinstance(rawfiles, basestring):
            if not os.path.isfile(rawfiles):
                logger.error('Could not find raw file list {}!'.format(rawfiles))
            else:
                rawobsfilename = rawfiles
        else:
            # Assume it is an iterable list of strings.
            outputfiles = []
            try:
                for r in rawfiles:
                    if os.path.isabs(r):
                        if os.path.isfile(r):
                            outputfiles.append(r)
                        else:
                            logger.warning('Raw absolute filepath {} could not be found on disk.'.format(r))
                    else:
                        odatain = oracenv['ORAC_DATA_IN']
                        abspath = os.path.join(odatain, r)
                        if os.path.isfile(abspath):
                            outputfiles.append(abspath)
                        else:
                            logger.warning('Raw relative filepath {} could not be found in ORAC_DATA_IN {}.'.format(
                                r, odatain))
                if not outputfiles:
                    logger.error('No valid input raw files were found!')
                    raise Exception('No valid input raw files were found!')
                else:
                    # Write output files into a temp file.
                    fh = tempfile.NamedTemporaryFile(mode='w', prefix='tmpORACInputList.lis', delete=False)
                    rawobsfilename = fh.name
                    fh.writelines('\n'.join(outputfiles))
                    fh.close()
                    logger.debug('Using temporary list of raw observations in %s.', rawobsfilename)
            except:
                logger.error('Could turn provided list of raw observation files into correct format')
                raise


    # Orac dr perl command
    starperl = os.path.join(oracenv['STARLINK_DIR'], 'Perl', 'bin', 'perl')
    oracdr_script = os.path.join(oracenv['ORAC_DIR'], 'bin', 'oracdr')
    # Set up commands:
    commandlist = [starperl, oracdr_script, '-log=sf', '-nodisplay', '-batch']

    commandlist += ['-loop={}'.format(loop)]
    if loop == 'list':
        commandlist += ['-ut={}'.format(str(utdate))]
        if isinstance(obslist, basestring):
            commandlist += ['-list={}'.format(obslist)]
        else:
            commandlist += ['-list={}'.format(','.join([str(int(i)) for i in obslist]))]
    if loop == 'file':
        commandlist += ['-files={}'.format(rawobsfilename)]

    if recpars:
        commandlist += ['-recpars={}'.format(recpars)]
    if onegroup:
        commandlist += ['-onegroup']
    if headeroverride:
        commandlist += ['-headeroverride={}'.format(headeroverride)]
    if calib:
        commandlist += ['-calib {}'.format(calib)]
    if verbose:
        commandlist += ['-verbose']
    if warn:
        commandlist += ['-warn']
    if debug:
        commandlist += ['-debug']
    if recipe:
        commandlist += [recipe]

    # Run the command.
    logger.info('Running {}.'.format(' '.join(commandlist)))
    proc = subprocess.Popen(commandlist, env=oracenv, shell=False)
    pid = proc.pid
    proc.communicate()
    status = proc.returncode

    # Wait one second so that list of iles on disk doesn't contain the temporary files.
    time.sleep(1)
    # Get the .orac log file:
    logname = os.path.join(outputdir, '.oracdr_{}.log'.format(str(int(pid))))
    outputlog = os.path.join(outputdir, 'oracdr_{}.log'.format(str(int(pid))))
    if os.path.isfile(logname):
        shutil.move(logname, outputlog)
    else:
        logger.warning('Could not find logfile in outputdir.')
        outputlog = None

    # Get the list of created data files (.sdf or .fits)
    datafiles = glob.glob(os.path.join(outputdir, '*.sdf'))
    datafiles += glob.glob(os.path.join(outputdir, '*.fits'))
    datafiles += glob.glob(os.path.join(outputdir, '*.fit'))
    datafiles += glob.glob(os.path.join(outputdir, '*.FIT'))
    datafiles += glob.glob(os.path.join(outputdir, '*.FITS'))

    # Remove input files (assume that all symlinks are the input files)
    outputdatafiles = []

    for i in datafiles:
        if not os.path.islink(i):
            outputdatafiles.append(i)

    if not outputdatafiles:
        logger.warning('No SDF/FITS datafiles were found in outputdir {}'.format(outputdir))

    # Get log files
    logfiles = glob.glob(os.path.join(outputdir, 'log.*'))

    # Get preview images.
    pngfiles = glob.glob(os.path.join(outputdir, '*.png'))


    returnvals = oracoutput(outputlog, outputdir, outputdatafiles, pngfiles, logfiles, status, pid)

    if status != 0:
        logger.error('ORAC-DR ended with an error! You may or may not care about this.')

    return returnvals



def picard(recipe, files, dataout=None,
           recpars=None, oracdir=None,
           verbose=False, debug=False, warn=False):

    """
    Run a picard recipe on a group of files.

    Arguments
    ----------
    recipe: str
        Name of instrument

    files: str or list of str
        If str: name of textfile containing list of files. If list: list
        of input files. All paths interpreted relative to current
        directory.

    Keyword Arguments
    ------------------
    dataout: str
        Location of output data directory; defaults to curr dir.

    recpars: str
         Passed to the picard --recpars option.

    oracdir: str
       Specify a custom ORAC src tree directory; by default
       <starpath>/bin/oracdr/src will be used.

    verbose: bool
        provide output from Starlink commands in log/stdout

    debug: bool
        Provide debug output.

    warn: bool
        Show Perl warning messages in stdout.

    Returns
    --------
    Return value is a named tuple with the following attributes:

     - runlog: name of output logfile.
     - outputdir: path of output directory
     - datafiles: list of output data files.
     - imagefiles: list of output image files.
     - logfiles: list of log.* files
     - status: int, return code from suprocess.Popen
     - pid (int): pid of perl parent process.

    """
    picardenv = env.copy()
    if not oracdir:
        picardenv['ORAC_DIR'] = os.path.join(starpath, 'bin', 'oracdr', 'src')
    else:
        picardenv['ORAC_DIR'] = oracdir
    picardenv['ORAC_PERL5LIB'] = os.path.join(picardenv['ORAC_DIR'], 'lib', 'perl5')
    picardenv['STAR_LOGIN'] = '1'

    if dataout:
        dataout = os.path.abspath(dataout)
        if not os.path.isdir(dataout):
            logger.error('Requested ORAC_DATA_OUT {} does not exist'.format(dataout))
            raise Exception('Requested ORAC_DATA_OUT {} does not exist'.format(dataout))
    else:
        dataout = os.getcwd()

    # Actually run in a temporary working directory in data out. Make that now.
    outputdir = os.path.abspath(tempfile.mkdtemp(prefix='PICARDworking', dir=dataout))
    picardenv['ORAC_DATA_OUT'] = outputdir
    logger.debug('Working output directory for ORAC-DR is {}.'.format(outputdir))

    # Get files:
    if isinstance(files, basestring):
        # Assume its a text file containing input files.
        if not os.path.isfile(files):
            logger.error('List of inputfiles {} not found.'.format(files))
            raise Exception('List of inputfiles {} not found.'.format(files))
        fileargument = ['`cat {}`'.format(files)]
    else:
        # Assume its a list of strings.
        inputfiles = []
        for f in files:
            if not os.path.isfile(f):
                logger.warning('Input file {} not found.'.format(files))
            else:
                inputfiles.append(f)
        if not inputfiles:
            logger.error('No input files found')
            raise Exception('No input files found')
        else:
            fileargument = inputfiles


    # Orac dr perl command
    starperl = os.path.join(picardenv['STARLINK_DIR'], 'Perl', 'bin', 'perl')
    script = os.path.join(picardenv['ORAC_DIR'], 'bin', 'picard')
    # Set up commands:
    commandlist = [starperl, script, '-log=sf', '-nodisplay']

    if recpars:
        commandlist += ['-recpars={}'.format(recpars)]

    if verbose:
        commandlist += ['-verbose']
    if warn:
        commandlist += ['-warn']
    if debug:
        commandlist += ['-debug']


    commandlist += [recipe]

    commandlist += fileargument

    # Run the command.
    logger.info('Running {}.'.format(' '.join(commandlist)))
    proc = subprocess.Popen(commandlist, env=picardenv, shell=False)
    pid = proc.pid
    proc.communicate()
    status = proc.returncode

    # Wait one second so that list of files on disk doesn't contain the temporary files.
    time.sleep(1)
    # Get the .picard log file:
    logname = os.path.join(outputdir, '.picard_{}.log'.format(str(int(pid))))
    outputlog = os.path.join(outputdir, 'picard_{}.log'.format(str(int(pid))))
    if os.path.isfile(logname):
        shutil.move(logname, outputlog)
    else:
        logger.warning('Could not find logfile in outputdir.')
        outputlog = None

    # Get the list of created data files (.sdf or .fits)
    datafiles = glob.glob(os.path.join(outputdir, '*.sdf'))
    datafiles += glob.glob(os.path.join(outputdir, '*.fits'))
    datafiles += glob.glob(os.path.join(outputdir, '*.fit'))
    datafiles += glob.glob(os.path.join(outputdir, '*.FIT'))
    datafiles += glob.glob(os.path.join(outputdir, '*.FITS'))

    # Remove input files (assume that all symlinks are the input files)
    outputdatafiles = []

    for i in datafiles:
        if not os.path.islink(i):
            outputdatafiles.append(i)

    if not outputdatafiles:
        logger.warning('No SDF/FITS datafiles were found in outputdir {}'.format(outputdir))

    # Get log files
    logfiles = glob.glob(os.path.join(outputdir, 'log.*'))

    # Get preview images.
    pngfiles = glob.glob(os.path.join(outputdir, '*.png'))

    returnvals = oracoutput(outputlog, outputdir, outputdatafiles, pngfiles, logfiles, status, pid)

    if status != 0:
        logger.error('PICARD ended with an error! You may or may not care about this.')

    return returnvals


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
