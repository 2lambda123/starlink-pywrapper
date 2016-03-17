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







import logging

from astropy.io import fits
from starlink import ndfpack




logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



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










