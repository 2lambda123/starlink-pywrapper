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
# Author: SF Graves



"""Generate Starlink module functions.

This script generates python modules to call all the commands in a
Starlink package, given a Starlink build tree.

Usage: generate_functions.py [-q | -v] <buildtree> [<package>...]
       generate_functions.py --help

Options:
       -h, --help     show help
       -v, --verbose  show more output info
       -q, --quiet    show less output info

If no packages are specified, it will generate python modules for:
KAPPA, cupid, convert, smurf, figaro, surf, and ccdpack.

Any number of modules can be specified.

It will look under <buildtree>/applications/modulename.lower() for:
<modulename>.hlp and <commandname>.ifl files.
"""

import logging
import os
import re

from collections import namedtuple
from keyword import iskeyword

from docopt import docopt

# Set up normal logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Namedtuples to hold parameter and command information.
parinfo = namedtuple('parinfo',
                     'name type_ prompt default position range_ ' \
                     'in_ access association ppath vpath list_ readwrite')
commandinfo = namedtuple('commandinfo', 'name description pardict')



def _get_python_type(startype):
    """
    Get name of normal python type from STARLINK type.
    """
    # remove quotes
    if startype:
        startype = startype.replace('"','').replace("'",'')

    if startype == '_LOGICAL':
        return 'bool'
    elif startype == '_INTEGER' or startype == '_integer':
        return 'int'
    elif startype == '_REAL' or startype == '_DOUBLE':
        return 'float'
    elif startype == 'NDF' or startype == 'FILENAME':
        return 'str,filename'
    elif startype == '_CHAR' or startype == 'LITERAL':
        return 'str'
    elif not startype:
        return ''
    else:
        logger.warning('Unknown startype (%s)' % (startype))
        return startype


# Get information from an IFL file. (gets a one line prompt string,
# which is handy for short help).
def _ifl_parser(ifllines, parameter_info, comname=''):

    """Get parameter info from an ifl file for a command.

    iflines should be the results of a readlines() command
      on a command.ifl file.

    parameter_info is a parameter_info dict of parinfo tuples, holding
      the readwrite info if already gotten about that parameter.

    returns a dict, with commandnames as keys and parinfo objects as
    values.

    """

    ifl=''.join(ifllines)

    # Parse IFL file to find start and end of each parameter.
    parindices = [m.start() for m in re.finditer('\n[\s]*parameter', ifl)]
    endindices = [m.start() for m in re.finditer('\n[\s]*endparameter', ifl)]
    pardict={}

    # Go through each parameter
    for i, j in zip(parindices, endindices):

        # Get the strings for the parameter information.
        res = ifl[i:j].strip()
        reslist = res.split('\n')

        # Find the parname
        parname = reslist[0].split()[1].strip().lower()

        # Get each field from the ifl string (if present).
        fields = ['type', 'prompt', 'default', 'position', 'range',
                  'in', 'access', 'association', 'ppath', 'vpath']
        values = []

        for a in fields:
            val = _ifl_get_parameter_value(reslist, a)
            if a == 'prompt' and isinstance(val, str):
                val = val.strip("'")
            elif isinstance(val, str):
                val = val.replace("'",'').replace('"','')
            values.append(val)

        # Assign output values from input information
        if parameter_info and parname in parameter_info:
            pinfo = parameter_info[parname]
            values.append(pinfo.list_)
            values.append(pinfo.readwrite)
        else:
            values.append(None)
            values.append(None)
            logger.debug('%s: parname %s found in ifl but was not in .hlp' % (comname, parname))

        pardict[parname] =  parinfo(parname, *values)

    return pardict


def _ifl_get_parameter_value(paramlist, value):

    """
    Get the value of a parameter (as a string).
    """
    findvalues = [s for s in paramlist if s.strip().startswith(value)]
    if findvalues:
        result = findvalues[0].split(value)[1].strip()
    else:
        result = None

    return result


def get_module_info(hlp, iflpath):

    """
    Get info on the commands in a Starlink module.

    hlp is the result of readlines() on a module.hlp file.

    iflpath is the location in which command.ifl files can be found.

    Returns a dictionary with commandnames as keys, and a dictionary
    of parinfo tuples (keyed by parameter name).
    """
    matchcommandname = re.compile('^1 [A-Z0-9]+$')
    comnames = [i for i in hlp if matchcommandname.search(i)]
    moduledict={}

    for i in range(len(comnames)):
        comname = comnames[i].split()[1].strip().lower()
        comindex = hlp.index(comnames[i])
        if i < (len(comnames) - 1):
            # Deal with repeated command names.
            repeats = comnames.count(comnames[i])
            if repeats != 1:
                logger.warning('Command %s appears %i times in the .hlp file' %(comname, repeats))

                # Find real end of command.
                nextcomindex = comindex + hlp[comindex+1:].index(comnames[i+1])
            else:
                nextcomindex = hlp.index(comnames[i+1])
        else:
            nextcomindex = -1

        commanddoc = hlp[comindex:nextcomindex]
        comdescrip = commanddoc[1].strip()

        try:
            parindex = commanddoc.index('2 Parameters\n')
            try:
                nextsec = [i for i in commanddoc[parindex+1:] if i.startswith('2')][0]
                nextindex = commanddoc.index(nextsec)
            except IndexError:
                nextindex = -1
            parameter_introlines = [i for i in commanddoc[parindex+1:nextindex] if i[0] == '3']
            parameters = [commanddoc[commanddoc.index(i)+1] for i in parameter_introlines]

            # Get lowercase parameter names without array stuff (e.g. 'lbnd'
            # instead of 'LBND( 2 )' )
            parnames = [i.split('=')[0].split('(')[0].strip().lower() for i in parameters]

            # Get array stuff
            array = None
            parlist = [True if '(' in  i.split('=')[0] else False for i in parameters]


            # Get types (e.g. is it write or read variable)
            par_type = [i.split('(')[-1].strip(')\n').lower() if '(' in i else None for i in parameters ]

            # Create output variables.
            parameter_info = dict()
            for pname, ptype, plist in zip(parnames, par_type, parlist):
                # So far we only have the readwrite information.
                parameter_info[pname] = parinfo(pname, *([None]*10 + [plist] + [ptype]))

        except ValueError:
            parameter_info = None

        moduledict[comname] = commandinfo(comname, comdescrip, parameter_info)

        # find ifl file
        try:
            ifl = find_starlink_file(iflpath, comname + '.ifl')
            parameter_info = _ifl_parser(ifl, parameter_info, comname=comname)

            moduledict[comname] = commandinfo(comname, comdescrip, parameter_info)
        except Exception:
            logger.warning('no ifl file found for %s' % comname)

    return moduledict

def formatkeyword(vals, style='numpy', default=True):

    """
    format keyword for numpy docstring.

    vals should be a parinfo object
    style should be 'numpy' or 'google'

    if default is False, then default
    values won't be included.

    Returns a list of strings.
    """
    name = vals.name

    if iskeyword(name):
        name += '_'
    if name[-1] == '_':
        name = '`{}`'.format(name)

    # Format the first line (varanme : type, min-max)
    typestring = _get_python_type(vals.type_)
    if vals.list_:
        typestring = 'List[{}]'.format(typestring)
    if vals.range_:
        typestring = ', {}'.format('-'.join(vals.range_.split(',')))
    if style == 'numpy':
        parstring = '{} : {}'.format(name.lower(), typestring)
    elif style == 'google':
        parstring = '{} ({})'.format(name.lower(), typestring)
    doc = [parstring]
    # Format the prompt (if it exists)
    promptstring = ''
    if vals.prompt:
        promptstring = vals.prompt
    if vals.default and default:
        promptstring = '{} [{}]'.format(promptstring, vals.default)

    if promptstring:
        if style=='numpy':
            doc += [' '*4  + promptstring]
        elif style=='google':
            doc[0] += ': {}'.format(promptstring)
    return doc

def make_docstrings(moduledict, sunname=None):

    """
    Create the docstrings for a command.
    """

    docstringdict = {}
    # make a command for each command
    for command, info in moduledict.items():
        name = command
        doc = [info.description + '\n']
        param = info.pardict

        positional = []
        inputpar = []
        outputpar = []
        unknownpar = []

        # Get positional args, input kwargs, output args, unknown parameters
        if param:
            for i in param.values():

                # If access is None, fallback onto readwrite (if it exists)?
                readwrite = i.access
                if readwrite:
                    readwrite = readwrite.lower().replace("'",'').replace('"','')
                elif not readwrite and i.readwrite:
                    readwrite = i.readwrite

                # If dynamic is start of vpath, and there is no
                # default, replace the default with 'dyn.'
                if i.vpath and i.vpath.startswith('DYNAMIC'):
                    default = 'dyn.'
                    temp = list(i)
                    temp[3] = default
                    i = parinfo(*temp)


                # Anything with a position and no default and vapth,
                # or with vpath starting with PROMPT is a positional
                # argument.
                if i.position and (
                        (i.vpath is None and i.default is None) or
                        (i.vpath is not None and i.vpath.strip().startswith('PROMPT'))):
                    positional.append(i)

                # Anything else labelled 'read', 'given' or 'update' is an input keyword.
                # Anything with 'write' is only a input value if:
                #    type_=NDF or type_=FILENAME
                #  or type='LITERAL and association contains 'CATAL'
                #  or type='LITERAL' and ppath contains CURRENT.
                elif (readwrite == 'read' or
                      readwrite == 'given' or
                      readwrite == 'update' or
                      (readwrite == 'write' and i.type_ is not None and 'NDF' in i.type_) or
                      (readwrite == 'write' and i.type_ is not None and 'FILENAME' in i.type_) or
                      (readwrite == 'write' and i.type_ is not None and 'LITERAL' in i.type_ and
                       i.association is not None and 'CATAL' in i.association) or
                      (readwrite == 'write' and i.type_ is not None and 'LITERAL' in i.type_ and
                       (i.vpath is not None and 'CURRENT' in i.vpath) or
                       (i.ppath is not None and 'CURRENT' in i.ppath))):
                    inputpar.append(i)

                # Anything else labelled 'write' is an output parameter
                elif readwrite == 'write':
                    outputpar.append(i)
                else:
                    # Assume anything else is an input keyword parameter
                    inputpar.append(i)
                    #unknownpar.append(i)


        if  positional:

            # Positional kwargs must have list of indexes without gap.
            positions = [int(i.position) for i in positional]
            positions.sort()
            if max(positions) != len(positions):
                logger.debug('command {} has improbably positional arguments'.format(name))
                logger.debug([(i.name, i.position) for i in positional])
                logger.debug('Moving impossible positional arguments to keyword args.'.format(name))
                # find positional parameters that need to be moved:
                missing_index = min([i for i in range(1,len(positions)+1) if i not in positions])
                parameters_to_move = [i for i in positional if int(i.position) >= missing_index]
                for p in parameters_to_move:
                    positional.remove(p)
                    inputpar.append(p)


        if positional:
            heading = 'Arguments'
            heading = [heading, '-'*len(heading)]
            doc += heading

            # sort positional
            positional = sorted(positional, key=lambda x: x.position)
            names = [i.name + '_' if iskeyword(i.name) else i.name for i in positional]
            for val in positional:
                valdoc = formatkeyword(val)
                doc += valdoc
            doc +=['']

            callsignature = ', '.join(names) + ', **kwargs'
        else:
            callsignature = '*args, **kwargs'

        if inputpar:
            # sort based on position then alphabet
            inputpar = sorted(inputpar, key=lambda x: x.name)
            inputpar = sorted(inputpar, key=lambda x: int(x.position) if
                              x.position is not None else 1000, reverse=False)

            heading = 'Keyword Arguments'
            heading = [heading, '-'*len(heading)]
            doc += heading

            for val in inputpar:
                valdoc = formatkeyword(val)
                doc += valdoc
            doc += ['']


        if outputpar:
            heading = 'Returns'
            heading = [heading, '-'*len(heading)]
            doc += heading

            outputpar = sorted(outputpar, key=lambda x: x.name)

            for val in outputpar:
                valdoc = formatkeyword(val, default=False)
                doc += valdoc
            doc += ['']


        if sunname:
            # Add Note section with SUN documentation.
            heading = 'Notes'
            heading = [heading, '-'*len(heading)]
            doc += heading
            sunurl = 'http://www.starlink.ac.uk/cgi-bin/htxserver/{}.htx/{}.html?xref_{}'.format(
                sunname, sunname, name.upper())
            doc += ['See:\n  {}\n  for full documentation of this command in the latest Starlink release'.format(
                sunurl)]
            doc += ['']

        # Return a dictionary for each command, with the docstrings
        # and the call signature.
        docstringdict[name] = ('\n'.join(doc), callsignature)
    return docstringdict



moduleline = "Runs commands from the Starlink {} package.\n\n"\
             "Autogenerated from the starlink .hlp and .ifl files," \
             "\nby python-starscripts/generate_functions.py."

docrunline = 'Runs the command: {} .'

def create_module(module, names, docstrings, commanddict):

    modulecode = []
    moduleheader = '\n'.join(['"""', moduleline.format(module), '"""', '',
                              'from . import wrapper', '', ''])

    for name in names:
        commandline = commanddict[name]
        callsignature = docstrings[name][1]
        docstring = docstrings[name][0]

        # Add a line indicating which binary/script it is trying to run to docstring.
        docstring = docstring.split('\n')
        docstring = [docstring[0], '', docrunline.format(commandline)] + docstring[1:]

        # Append _ to the end of reserved python keywords.
        if iskeyword(name):
            name = name + '_'

        methodcode = [
             ' '*0 + 'def {}({}):'.format(name, callsignature),
             ' '*4 + '"""',
             '\n'.join([i if not i else ' '*4 + i  for i in docstring]),
             ' '*4 + '"""',
             ' '*4 + 'return wrapper.starcomm("{}", "{}", {})'.format(commandline,
                                                              name,
                                                                    callsignature),
             '\n',
        ]

        methodcode = ['\n' if i.isspace() else i for i in methodcode]
        modulecode += methodcode

    f = open(module.lower() + '.py', 'w')
    f.writelines('\n'.join([moduleheader] + modulecode))
    f.close()


def get_command_paths(shfile, comnames, modulename):
    commanddict = {}
    for c in comnames:
        # find the line in the shfile
        lines = [i for i in shfile if i.startswith(c)]
        lines = [i for i in lines if i.split('()')[0].strip() == c]
        if lines:
            if len(lines) > 1:
                logger.warning('Found multiple commandlines  for %s: , %s' %(c, str(lines)))
            commandline = lines[0]

            # Find everything before the argument passing (${1+"$@"}, and after the
            # initial curly brace. Strip off the trailing and leading white space.
            command = commandline.split('${1+"$@"}')[0]
            command = '{'.join(command.split('{')[1:])
            command = command.strip()

            # If command starts with 'python ', strip off 'python '
            if command.startswith('python '):
                command = command.lstrip('python ')

            # if command starts with 'starperl ', replace with $STARLINK_DIR/bin/starperl
            elif command.startswith('starperl '):
                command = command.replace('starperl ', '${STARLINK_DIR}/bin/starperl ')
            elif not command.startswith('$'):
                logger.warning("Com %s has an unknown command path %s" %(c, command))
            commanddict[c] = command
    return commanddict



def find_starlink_file(rootpath, filename):
    walk = os.walk(rootpath)
    files = [os.path.join(root, filename) for root, dirs, files in walk if filename in files]

    # Just take the first one if there are multiples.
    if len(files) > 1:
        logger.warning('Found multiple {} files under directory {}'.format(
                filename, rootpath))
    elif not files:
        raise Exception('Could not find {} file under directory {}'.format(
            filename, rootpath))

    path = files[0]
    logger.debug('Using {} file.'.format(path))
    f = open(path, 'r')
    filecontents = f.readlines()
    f.close()
    return filecontents

# Information for module.
sunnames = {
    'kappa': 'sun95',
    'cupid': 'sun255',
    'convert': 'sun55',
    'smurf': 'sun258',
    'figaro': 'sun86',
    'surf': 'sun216',
    'ccdpack': 'sun139',
}



DEFAULTPACKAGES = [
    'KAPPA',
    'CUPID',
    'Figaro',
    'CONVERT',
    'SMURF',
    'SURF',
    'CCDPACK',
]
if __name__ == '__main__':

    # Parse command line options and set defaults.
    args = docopt(__doc__)

    buildpath = args['<buildtree>']
    packages = args['<package>']

    if not packages:
        packages = DEFAULTPACKAGES

    if args['--quiet']:
        logger.setLevel(logging.WARNING)
    elif args['--verbose']:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    logger.info('Using Starlink build from {}.'.format(buildpath))
    logger.info('Building python modules {}.'.format(', '.join(packages)))


    # Create a function for each package
    for modulename in packages:

        logger.info('Creating {} module '.format(modulename))

        # Get the name of the SUN:
        sunname = sunnames.get(modulename.lower(), None)
        if not sunname:
            logger.warning('No SUN found for {}.'.format(modulename))

        # Find the <package>.hlp, <package>.sh and path for ifl files:
        rootpath = os.path.join(buildpath, 'applications', modulename.lower())

        helpfile = find_starlink_file(rootpath, modulename.lower() + '.hlp')
        shfile = find_starlink_file(rootpath, modulename.lower() + '.sh')

        # Parse the .hlp and .ifl files to get a dictionary of commands
        # and parameters (with parinfo namedtuples to describe parameter).
        moduledict = get_module_info(helpfile, rootpath)


        # Clean up a few commands we don't want.  Specifically the
        # modulename itself, and any interactive _help.
        if modulename.lower() in  moduledict:
            moduledict.pop(modulename.lower())
        helpname = modulename.lower() + 'help'
        if helpname in moduledict:
            moduledict.pop(helpname)
        if len(modulename) > 3:
            helpname = modulename[0:3].lower() + 'help'
            if helpname in moduledict:
                moduledict.pop(helpname)

        # Parse the shfile to get the actual commands that are being run.
        commanddict = get_command_paths(shfile, moduledict.keys(), modulename)

        # Create the docstrings for every command.
        docstrings = make_docstrings(moduledict, sunnames.get(modulename.lower(), None))

        commandnames = list(commanddict.keys())
        commandnames.sort()

        # Create the <modulename>.py file.
        create_module(modulename, commandnames, docstrings, commanddict)

