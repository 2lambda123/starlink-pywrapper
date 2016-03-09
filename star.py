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

NOTE: the starlink starutil.py interface looks rather more thorough,
should check what it does before bothering to add things to this. If
anyone other than me is reading this, then they nmight want to use the
starutil interface rather than this.

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
import shutil
import signal
import subprocess
import sys
import tempfile
import time




from collections import namedtuple
from keyword import iskeyword

from astropy.io import fits
from starlink import hds

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
def star(module, com, *args, **kwargs):
    """Execute a Starlink application

    Carries out the starlink command, and returns a namedtuple of the
    starlink parameter values (taken from $ADAM_DIR/<com>.sdf

    Args:
        module (str): name of module, e.g. 'kappa' or 'smurf'
        com (str): name of command, e.g. 'stats' or 'makecube'

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


def _make_argument_string(*args, **kwargs):
    """
    Turn pythonic list of positional arguments and keyword arguments
    into a starlink string.

    TODO: this should really be more thoroughly checked...
    """
    output = ''

    # Go through each positional argument.
    for i in args:
        output += str(i)+' '
    for key, value in kwargs.items():
        # if key ends in _ strip it out (so that you can use
        # in_=... as in=... is not allowed as its a reserved work in
        # python)
        if key[-1] == '_':
            key = key[:-1]
        output += str(key)+'='+str(value)+' '

    #remove trailing space
    output = output.rstrip()

    # Return list of arguments (as a string).
    return output.rstrip()


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


def parget(applic, parname):

    """Get output from kappa parget using Popen.

    THIS IS DEPRECATED.

    NOTE: error checking is nonexistent as parget doesn't seem to
    easily return an error code to stderr or to return a non 0 status
    value. It is therefore important to check that the output is in an
    expected form.

    Example usage:
    > maxpos = star.parget('stats', 'maxpos')
    """

    arg = 'applic=' + applic + ' parname=' + parname
    compath = os.path.join(starpath, 'bin', 'kappa', 'parget')
    logger.debug([compath] + arg)
    output = subprocess.Popen([compath] +
                              arg, env=env, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE
                              )
    stdout, stderr = output.communicate()
    status = output.returncode
    if status != 0:
        raise PargetError(compath, arg, stdout, stderr)
    return stdout.strip()


class StarError(StandardError):
    def __init__(self, compath, arg, stderr):
        message = 'Starlink error occured during:\n %s %s\n ' % (compath, arg)
        message += '\nThere should be an error message printed to stdout '
        message += '(check above this traceback in ipython)'+stderr
        StandardError.__init__(self, message)


class PargetError(StarError):
    def __init__(self, compath, arg, stdout, stderr):
        message = 'Starlink error occured during:\n %s %s\n ' % (compath, arg)
        message += '\n The stdout and stderr from the command are:\n'
        message += '%s \n %s' % (stdout, stderr)
        StandardError.__init__(self, message)


def _get_vals(module, com, *args, **kwargs):

    """
    Get the output from a starlink command.

    """

    compath = os.path.join(starpath, 'bin', module, com)
    arg = _make_argument_list(*args, **kwargs)

    logger.debug([compath]+arg)

    output = subprocess.Popen([compath] +
                              arg, env=env, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE
                              )
    stdout, stderr = output.communicate()
    status = output.returncode
    if status != 0:
        raise PargetError(compath, arg, stdout, stderr)
    return stdout.strip()


def hdsread(ndf, compname):

    """
    Read information from and ndf using hdstrace.
    Example usage:
    > value = star.hdsread('myndf', 'mean')
    """

    ret = _get_vals('', 'hdstrace', ndf+'.'+compname,
                    newline=True, full=True, nlines='all',
                    widepage=True)
    return hdstrace_eval(ret)


def read_starval(applic, parname):

    """Read returned parameter values stored in the $ADAM_DIR/applicname.sdf'

    E.g. to get the values maxpos position calculated after running
    stats, do:

    >maxpos = star.read_starval('stats', 'maxpos')

    Values should be returned in a sensible format, but please check.

    """
    ndf = os.path.join(adamdir, applic+'.sdf')
    return hdsread(ndf, parname)


def hdstrace_eval(hdstracestring):

    """Get a sensible value out of the results of an hdstrace.

    This has not been entirely tested, so check that is has returned
    somehting sensible before relying on it in scripts.

    """

    # Split at new lines.
    strings = hdstracestring.split('\n')

    # This should find the type of value that is stored
    # e.g. CHAR, INTEGER etc.
    thetype = strings[0].split()[1][1:-1]

    # If its an ADAM_PARNAME, then the types is written somewhere else.
    if thetype == 'ADAM_PARNAME':
        thetype = strings[2].split()[1][1:-1]

    # Split on commas by default.
    splitval = ","

    # Go through the different types that I can cope with, set the
    # convert function and the character to split at if different
    # from commas.
    if thetype[1:5] == 'CHAR':
        convert = str
        splitval = "'"
    elif thetype == '_INTEGER':
        convert = int
    elif thetype == '_DOUBLE':
        convert = float
    elif thetype == '_LOGICAL':
        convert = bool
    else:
        convert = str

    # Join the correct list of strings back into one thing (some values
    # are multi line).
    values = ''.join(strings[3:-2])

    # split values by splitval and remove any that are empty
    result = filter(None, [i.strip() for i in values.split(splitval)])
    # convert each object in result to the sensible format

    if convert == float:
        result = [i.replace('D', 'E') for i in result]
    res2 = np.array([convert(i) for i in result])

    #filter out valaues that are just a comma...
    res3 = []
    for i in res2:
        if i != ',':
            res3.append(i)
    return res3


# get the fits header from a data file. If a fits header doesn't
# exist, then create it and use that
def get_fitshdr(datafile):
    """

    Get the fits header from a datafile (either fits or ndf).

    If it can't be read in, then assume its an ndf and try converting
    it to fits (note that the tempfile stuff is probably not
    entirely safe.

    """
    try:
        hdr = fits.getheader(datafile)
    except IOError:
        #can't read in with fits
        tfile = tempfile.NamedTemporaryFile()
        name = tfile.name
        #this is unsafe...
        tfile.close()
        convert('ndf2fits', datafile, name+'.fits')
        hdr = fits.getheader(name+'.fits')
        os.remove(name+'.fits')
    return hdr


############################
# HIGHER Level functions
############################


def oracdr_setup(instrument, ORAC_DIR=None, date=None,
                 ORAC_DATA_IN=None, ORAC_DATA_OUT=None,
                 ORAC_CAL_ROOT=None, ORAC_DATA_CAL=None,
                 ORAC_PERL5LIB=None):
    """
    Setup the various ORAC-DR environmental variables.

    """
    oracenv = {}
    if not date:
        date = time.strftime('%Y%M%d')
    instrument = instrument.lower()
    if instrument.split('_')[0] =='scuba-2':
        splits = instrument.split('_')
        splits[0] = 'scuba2'
        instrument = '_'.join(splits)

    instrument_short = instrument.split('_')[0]

    if not ORAC_DIR:
        ORAC_DIR = os.path.join(starpath, 'bin', 'oracdr', 'src')

    oracenv['ORAC_DIR'] = ORAC_DIR

    if not ORAC_CAL_ROOT:
        ORAC_CAL_ROOT = os.path.join(ORAC_DIR, '..', 'cal')
    oracenv['ORAC_CAL_ROOT'] = ORAC_CAL_ROOT

    if not ORAC_DATA_CAL:
        ORAC_DATA_CAL = os.path.join(ORAC_CAL_ROOT, instrument_short)
    oracenv['ORAC_DATA_CAL'] = ORAC_DATA_CAL

    if not ORAC_PERL5LIB:
        ORAC_PERL5LIB = os.path.join(ORAC_DIR, 'lib', 'perl5')
    oracenv['ORAC_PERL5LIB'] = ORAC_PERL5LIB

    ORAC_INSTRUMENT = instrument
    oracenv['ORAC_INSTRUMENT'] = ORAC_INSTRUMENT

    oracenv['ORAC_LOOP'] = "flag -skip"

    if not ORAC_DATA_IN:
        try:
            oracenv.pop('ORAC_DATA_IN')
        except KeyError:
            pass
            try:
                env.pop('ORAC_DATA_IN')
            except KeyError:
                pass
        # Now set orac_data_in correctly...
        if instrument == 'scuba2_850' or 'scuba2_450':
            ORAC_DATA_IN='/jcmtdata/raw/scuba2/ok/'+date
    oracenv['ORAC_DATA_IN'] = ORAC_DATA_IN


    if not ORAC_DATA_OUT:
        ORAC_DATA_OUT = '.'
    else:
        ORAC_DATA_OUT = os.path.relpath(ORAC_DATA_OUT)

    oracenv['ORAC_DATA_OUT'] = ORAC_DATA_OUT
    oracenv['STAR_LOGIN']='1'

    return oracenv



def oracdr(arglist, instrument='SCUBA2_850', ORAC_DIR=None, date=None,
                 ORAC_DATA_IN=None, ORAC_DATA_OUT=None,
                 ORAC_CAL_ROOT=None, ORAC_DATA_CAL=None,
                 ORAC_PERL5LIB=None) :
    """
    Currently just takes in a list of arguments
    REturns status, which may not be useful.
    """
    oracenv = oracdr_setup(instrument=instrument, ORAC_DIR=ORAC_DIR, date=date,
                 ORAC_DATA_IN=ORAC_DATA_IN, ORAC_DATA_OUT=ORAC_DATA_OUT,
                 ORAC_CAL_ROOT=ORAC_CAL_ROOT, ORAC_DATA_CAL=ORAC_DATA_CAL,
                           ORAC_PERL5LIB=ORAC_PERL5LIB)
    oenv = env.copy()
    oenv.update(oracenv)
    oracdr_perlcom = os.path.join(starpath, 'Perl', 'bin', 'perl')
    oracdr_com = os.path.join(oenv['ORAC_DIR'], 'bin', 'oracdr')
    oracdr_command_list = [oracdr_perlcom, oracdr_com]
    logger.info('ORAC_COMMAND is:'+' '.join(oracdr_command_list+arglist))

    output = subprocess.Popen(oracdr_command_list + arglist,
                              env=oenv, preexec_fn=subprocess_setup)
    status = output.communicate()
    return status, oracenv

def picard(*args):
    if 'ORAC_DIR' not in env:
        env['ORAC_DIR'] = os.path.join(starpath, 'bin', 'oracdr', 'src')

    env['ORAC_PERL5LIB'] = os.path.join(env['ORAC_DIR'], 'lib', 'perl5')
    env['PERL5LIB'] = os.path.join(starpath, 'Perl', 'lib', 'perl5') + os.pathsep + os.path.join(starpath, 'Perl', 'lib', 'perl5', 'site_perl')

    command = os.path.join(env['ORAC_DIR'], 'etc', 'picard_start.sh')

    comargs = command + ' '.join(args)

    proc = subprocess.Popen(comargs, env=env, shell=True)
    proc.communicate()


def findclumps(*args, **kwargs):

    """Convenience method for carrying out findclumps within python script.

    Uses fellwalker if you don't specify the method.

    config parameters are read in from the kwargs, ONLY USED IF config
    is not explicitly set in call.

    findclumps parameters:
    ----------------------
    backoff
    config
    deconv
    msg_filter
    in
    jsacat
    logfile
    method
    nclumps
    out
    outcat
    perspectrum
    qout
    repconf
    *rms* -- needs to be in regular
    shape
    wcspar

    config parameters for fellwalker:
    ---------------------------------
    allowedge
    cleaniter
    flatslope
    fwhmbeam
    maxbad
    mindip
    minheight
    minpix
    maxjump
    noise
    velores

    In addition, keepConfigFile=True will cause the temporary config
    file to not be deleted afterwards.

    """

    # Replace in_ with in:
    if 'in_' in kwargs:
        kwargs['in'] = kwargs.pop('in_')

    # Ensure using lowercase for all kwargs.
    kwargs = dict((k.lower(), v) for k, v in kwargs.items())

    # First see if keepConfigFile has been set, and remove from kwargs if so.
    if 'keepconfigfile' in kwargs:
        keepconfig = kwargs.pop('keepconfigfile')
    else:
        keepconfig = False

    # First separate out all the allowed cupid parameters:
    # assume any kwargs not in this list are calls to config.
    cupidpar = [
        'backoff',
        'config',
        'deconv',
        'msg_filter',
        'in',
        'jsacat',
        'logfile',
        'method',
        'out',
        'outcat',
        'perspectrum',
        'qout',
        'repconf',
        'shape',
        'wcspar',
        'rms',
        'maxvertices']

    #---------------------------------------------------------
    # Turn the findclumps and config options into dictionaries.

    # Get all kwargs that are listed in cupidpar into one dictionary.
    cupid_kwargs = dict([(i, kwargs[i])
                        for i in kwargs if i.lower() in cupidpar])

    # Now get all kwargs that are not in cupid par and assume they are
    # config options.
    config_kwargs = dict([(i, kwargs[i])
                         for i in kwargs if i.lower() not in cupidpar])

    #------------------------------------------------------------
    # Turn the config kwargs dictionary into a config file.

    # If config is not set in the call, produce an output file with the
    # requested config params set.
    if not 'config' in cupid_kwargs:

        # First check which method is being used for clumpfinding.
        if 'method' in cupid_kwargs:
            method = cupid_kwargs['method']
        elif len(args) == 4:
            method = args[3]
        else:
            # If not specified use fellwalker.
            method = 'fellwalker'
            cupid_kwargs['method'] = method

        # Now get the configkwargs as a string.
        method_kwargs = dict(
            [(method+'.'+i, config_kwargs[i]) for i in config_kwargs])

        configstrings = [str(key)+'='+str(method_kwargs[key])
                         + r',' for key in method_kwargs]

        configfile = tempfile.NamedTemporaryFile(delete=False)

        # Write out the config string to a tempfile.
        for i in configstrings:
            configfile.write(i+os.linesep)
        configfile.close()

        # Now set the cupid config argument to be the tempfile.
        cupid_kwargs['config'] = r'^'+configfile.name

    #-------------------------------------------------------------
    # Actually call cupid and run findclumps.
    cupid('findclumps', *args, **cupid_kwargs)

    #--------------------------------------------------------------
    # if set, remove the config file
    if configfile and not keepconfig:
        os.remove(configfile.name)

#---------------------------------------------------------------------


def get_hds_values(comname):

    """
    Return a namedtuple with all the values
    from the ADAMDIR/commname.sdf hds file.
    """

    hdsobj = hds.open(os.path.join(adamdir, comname), 'READ')
    logger.debug('Opened %s to get values' %hdsobj.name.strip())

    # Iterate through it to get all the results.
    results = _hds_iterate_components(hdsobj)

    # Remove the 'ADAM_DYNDEF' component as it never exits?
    if results.has_key('adam_dyndef'):
        results.pop('adam_dyndef')

    # Fix up the name ptrs (if they are the only thing in the dictionary)
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
    name = hdscomp.name.lower()
    if iskeyword(name):
        name += '_'
    value = hdscomp.get()
    if 'char' in hdscomp.type.lower():
        if hdscomp.shape:
            value = [i.strip() for i in value]
        else:
            value = value.strip()
    # if 'logical' in hdscomp.type.lower():
    #     if hdscomp.shape:
    #         value = [bool(i) for i in value]
    #     else:
    #         value = bool(value)
    type_ = hdscomp.type
    return name, value, type_

def _hds_iterate_components(hdscomp):
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
