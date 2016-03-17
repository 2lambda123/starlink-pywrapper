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




import logging
import tempfile

from astropy.io import fits
from starlink import ndfpack

from . import utils


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Utils brings in the defualt environment:
# basefunction.env
# The starpath as utils.starpath
# The basic command to run things  utils.starcomm


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

    prompt = choice
    utils.env["ADAM_NOPROMPT"] = str(int(not bool(choice)))

def change_starpath(starpath):
    """
    Change the STARLINK_DIR used by this module.
    """
    if utils.env:
        noprompt = utils.env.get('ADAM_NOPROMPT', True)
    else:
        noprompt = True
        
    utils.env = utils.setup_starlink_environ(starpath,
                                             utils.adamdir,
                                             noprompt=noprompt)
    
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










