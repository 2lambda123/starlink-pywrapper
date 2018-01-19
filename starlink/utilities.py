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

try:
    from itertools import imap
except ImportError:
    imap = map


from starlink import hds

logger = logging.getLogger(__name__)



def get_ndf_fitshdr(datafile):
    """
    Return a astropy.io.fits header object.

    If an NDF is provided, it will look up the .more.FITS component of the NDF file.
    It will raise an error if that does not exist.


    Requires a astropy.io.fits to be installed.
    """

    from astropy.io import fits

    hdsobj = hds.open(datafile, 'READ')
    fitscomp = hdsobj.find('MORE').find('FITS')
    fitsheader = fitscomp.get()
    fitsheader = '\n'.join([i.decode()
                            if isinstance(i, bytes) and not isinstance(i, str)
                            else i
                            for i in fitsheader])
    hdr = fits.Header.fromstring(fitsheader, sep='\n')

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
    keys = list(summaries.keys())
    keys.sort()
    return '\n'.join( ['{:<{width}}: {}'.format(key, summaries[key], width=width+1) for key in keys])


import inspect
from types import FunctionType, ModuleType
from pkg_resources import resource_filename

def starhelp(myobj):
    """
    Get long help on a starlink module or command.
    """
    # For modules, return the summary of the module.
    if isinstance(myobj, ModuleType):
        doc = get_module_function_summary(myobj)

    elif isinstance(myobj, FunctionType):
        modulename = myobj.__module__.split('.')[1]
        dirname = modulename + '_help'
        functionname = myobj.__name__
        filename = resource_filename(myobj.__module__,
                                     os.path.join(dirname, functionname+'.rst')
                                     )
        if os.path.isfile(filename):
            f = open(filename, 'r')
            doc = f.readlines()
            f.close()
        else:
            raise Exception('starhelp could not find file {} on disk.'.format(filename))
    else:
        raise Exception('starhelp cannot evalute object {}.'.format(myobj))
    pydoc.pager(''.join(doc))







