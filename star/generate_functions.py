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


import logging
import os
import re

from collections import namedtuple
from keyword import iskeyword


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


# Get information from help system (gets a one line prompt string,
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
        if parameter_info and parameter_info.has_key(parname):
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

    iflpath is the location in which comand.ifl files can be found.

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
            nextcomindex = hlp.index(comnames[i+1])
        else:
            nextcomindex = -1
        commanddoc = hlp[comindex:nextcomindex]
        comdescrip = commanddoc[1].strip()

        try:
            parindex = commanddoc.index('2 Parameters\n')
            nextsec = [i for i in commanddoc[parindex+1:] if i.startswith('2')][0]
            nextindex = commanddoc.index(nextsec)
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
            #print('command %s has no parameters???' % comname)
            parameter_info = None

        moduledict[comname] = commandinfo(comname, comdescrip, parameter_info)
        #moduledict[comname] = commandinfo(comname, comdescrip, None)

        if os.path.isfile(os.path.join(iflpath, comname + '.ifl')):
            g = open(os.path.join(iflpath, comname + '.ifl'))
            ifl = g.readlines()
            g.close()

            parameter_info = _ifl_parser(ifl, parameter_info, comname=comname)

            moduledict[comname] = commandinfo(comname, comdescrip, parameter_info)
        else:
            logger.warning('no ifl file found for %s' % comname)

    return moduledict


def make_docstrings(moduledict):

    docstringdict = {}
    # make a command for each smurf command
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
                # or with vpath=PROMPT is a positional argument
                if i.position and (
                        (i.vpath is None and i.default is None) or
                        (i.vpath is not None and i.vpath.strip().startswith('PROMPT'))):
                    positional.append(i)

                # Anything else labelled 'read', 'given' or 'update' is an input keyword.
                # Anything with 'write' is only a input value if:
                #    type_=NDF
                #  or type='LITERAL and association='CATAL'
                #  or type='LITERAL' and ppath contains CURRENT.

                elif (readwrite == 'read' or
                      readwrite == 'given' or
                      readwrite == 'update' or
                      (readwrite == 'write' and i.type_ is not None and 'NDF' in i.type_) or
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
                    unknownpar.append(i)
                    #print('Unknown par %s: ' %(name), i)

        if positional:
            doc += ['Args:']

            # sort positional
            positional = sorted(positional, key=lambda x: x.position)
            names = [i.name + '_' if iskeyword(i.name) else i.name for i in positional]
            for vals in positional:
                inp = vals.name
                if iskeyword(inp):
                    inp += '_'
                python_type = _get_python_type(vals.type_)

                if vals.list_:
                    python_type = 'List[' + python_type + ']'

                range_ = ''
                if vals.range_ is not None:
                    range_ = ', ' + '-'.join(vals.range_.split(','))
                parstring = ' '*4 + inp.lower() + ' (' + python_type + range_ +'): '
                if vals.prompt:
                    parstring += vals.prompt
                if vals.default:
                    parstring += ' [' + vals.default + ']'
                doc +=[parstring]
            doc +=['']

            callsignature = ', '.join(names) + ', **kwargs'
        else:
            callsignature = '*args, **kwargs'

        if inputpar:
            # sort based on position then alphabet
            inputpar = sorted(inputpar, key=lambda x: x.name)
            inputpar = sorted(inputpar, key=lambda x: int(x.position) if
                              x.position is not None else 1000, reverse=False)

            doc += ['kwargs:']
            for vals in inputpar:
                inp = vals.name
                if iskeyword(inp):
                    inp += '_'
                python_type = _get_python_type(vals.type_)

                if vals.list_:
                    python_type = 'List[' + python_type + ']'
                range_ = ''
                if vals.range_:
                    range_ = ', '+'-'.join(vals.range_.split(','))
                parstring = ' '*4 + inp.lower() +' (' + python_type + range_ + ')'
                if vals.prompt:
                    parstring += ': ' + vals.prompt
                if vals.position:
                    parstring += ' (posit: %i)'% int(vals.position)
                if vals.default:
                    parstring += ' [' + vals.default + ']'
                doc += [parstring]
            doc += ['']

        if unknownpar:
            doc +=['other args:']
            for vals in unknownpar:
                inp = vals.name
                if iskeyword(inp):
                    inp = inp + '_'
                python_type = _get_python_type(vals.type_)

                if vals.list_:
                    python_type = 'List[' + python_type + ']'

                parstring = ' '*4 + inp.lower() +' (' + python_type + ')'
                if vals.prompt:
                    parstring += ': ' + vals.prompt
                if vals.default:
                    parstring += ' [' + vals.default + ']'
                doc += [parstring]
            doc += ['']

        if outputpar:
            doc +=['output:']
            outputpar = sorted(outputpar, key=lambda x: x.name)
            for vals in outputpar:
                outp = vals.name
                if iskeyword(outp):
                    inp = outp + '_'
                python_type = _get_python_type(vals.type_)

                if vals.list_:
                    python_type = 'List[' + python_type + ']'

                parstring = ' '*4 + outp.lower() +' (' + python_type + ')'
                if vals.prompt:
                    parstring += ': ' + vals.prompt
                doc += [parstring]
            doc +=['']

        # ACtually, all callsignatures should be '*args, **kwargs'
        docstringdict[name] = ('\n'.join(doc), callsignature)
    return docstringdict



classheaders = """
\"\"\" Autogenerated from the starlink .hlp and .ifl files,
by python-starscripts/generate_functions.py.
\"\"\"

import utils
"""

def create_class(module, names, docstrings, commanddict):
    #classcode = ['class {}(object):'.format(module),
    #             ' '*4 +'"""Run commands from the {} module"""'.format(module.upper()),
    #             '\n',]

    classcode = []

    for name in names:

        methodcode = [
             #' '*4 + '@staticmethod',
             ' '*0 + 'def {}({}):'.format(name, docstrings[name][1]),
             ' '*4 + '"""',
             '\n'.join([i if not i else ' '*4 + i  for i in docstrings[name][0].split('\n')]),
             '        """',
             ' '*4 + 'return utils.starcomm("{}", "{}", {})'.format(commanddict[name],
                                                              name,
                                                              docstrings[name][1]),
             '\n',
        ]

        methodcode = ['\n' if i.isspace() else i for i in methodcode]
        classcode += methodcode

    f = open(module + '.py', 'w')
    f.writelines('\n'.join([classheaders] + classcode))
    f.close()


def get_command_paths(shfile, comnames, modulename, shortname):
    commanddict = {}
    for c in comnames:
        # find the line in the shfile
        lines = [i for i in shfile if (c in i and shortname+'_'+c not in i)]
        if lines:
            commandline = lines[0]

            # Find everything before the argument passing (${1+"$@"}, and after the
            # initial curly brace. Strip off the trailing and leading white space.
            command = commandline.split('${1+"$@"}')[0].split('{')[1].strip()
            commanddict[c] = command
            print command
    return commanddict


# Get info from .hlp files: best way to find out if parameter is read or write.
starbuildpath='/export/data/sgraves/StarSoft/starlink'
for modulename in ['kappa', 'cupid', 'convert', 'smurf']:
    #for modulename in ['convert']:
    print 'Creating {} module '.format(modulename)
    hlppath = os.path.join(starbuildpath, 'applications', modulename, modulename + '.hlp')
    if not os.path.isfile(hlppath):
        raise StandardError('Could not find hlp file at %s' % hlppath)
    f = open(hlppath, 'r')
    helpfile = f.readlines()
    f.close()
    shpath = os.path.join(starbuildpath, 'applications', modulename, modulename + '.sh')
    f = open(shpath, 'r')
    shfile = f.readlines()
    f.close()
    moduledict = get_module_info(helpfile, os.path.join(starbuildpath, 'applications',modulename))

    shortname = modulename
    if modulename == 'convert':
        shortname = 'con'
    if moduledict.has_key(modulename):
        moduledict.pop(modulename)
    if moduledict.has_key(shortname + '_help'):
        moduledict.pop(shortname + '_help')
    commanddict = get_command_paths(shfile, moduledict.keys(), modulename, shortname)
    docstrings = make_docstrings(moduledict)


    create_class(modulename, commanddict.keys(), docstrings, commanddict)

