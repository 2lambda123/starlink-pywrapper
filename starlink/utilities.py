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
Convenience utilities when using Starlink in python.

"""

import logging
import os
import pydoc
from inspect import getmembers, isfunction
from itertools import imap

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
        raise Exception('Unknown file format %s: form must be "sdf" or "fits"' %  form)

    return hdr


def get_module_function_summary(module):
    """
    Return a summary of module functions
    """
    functionslist = getmembers(module, isfunction)
    summaries = {}
    for f in functionslist:
        summaries[f[0]] = next(s for s in f[1].__doc__.split('\n') if s)
    width = max(imap(len, summaries))
    keys = summaries.keys()
    keys.sort()
    return '\n'.join( ['{:<{width}}: {}'.format(key, summaries[key], width=width+1) for key in keys])


import inspect
from types import FunctionType, ModuleType

def starhelp(myobj):
    """
    Get long help on a starlink module or command.
    """
    # For modules, return the summary of the module.
    if isinstance(myobj, ModuleType):
        doc = get_module_function_summary(myobj)

    elif isinstance(myobj, FunctionType):
        modulename = myobj.__module__
        functionname = myobj.__name__
        dirname = os.path.dirname(inspect.getmodule(myobj).__file__)
        filename = os.path.join(dirname, 'helpfiles', modulename + '_' + functionname + '_longhelp.txt')
        if os.path.isfile(filename):
            f = open(filename, 'r')
            doc = f.readlines()
            f.close()
        else:
            raise Exception('starhelp could not find file {} on disk.'.format(filename))
    else:
        raise Exception('starhelp cannot evalute object {}.'.format(myobj))
    pydoc.pager(''.join(doc))







