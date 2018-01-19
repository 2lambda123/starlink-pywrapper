import os
from collections import namedtuple
from keyword import iskeyword

from starlink import hds

def get_hds_values(comname, adamdir):

    """
    Return a namedtuple with all the values
    from the ADAMDIR/commname.sdf hds file.
    """

    filename = os.path.join(adamdir, comname)
    try:
        hdsobj = hds.open(filename, 'READ')
        # Iterate through it to get all the results.
        results = _hds_iterate_components(hdsobj)

        # Remove the 'ADAM_DYNDEF' component as it never exits?
        if 'adam_dyndef' in  results:
            results.pop('adam_dyndef')

        # Fix up the nameptr values (if they are the only thing in the
        # dictionary)
        fixuplist = [i for i in results.keys()
                     if (isinstance(results[i], dict)
                         and list(results[i].keys())==['nameptr'])]

        for i in fixuplist:
            results[i] = results[i]['nameptr']

        for key in results:
            value = results[key]

            #This code is to ensure that on python3 we call 'decode'
            #so as to return byte strings. Currently this is calling
            #with 'ascii', as I believe HDS only has ascii?

            if (isinstance(value, bytes) and not isinstance(value, str)):
                results[key] = value.decode(encoding='ascii')
            elif (isinstance(value, bytes) and isinstance(value, str)):
                pass
            else:
                try:
                    results[key] = [j.decode(encoding='ascii') if isinstance(j, bytes) and not isinstance(j, str) else j for j in value]
                except (TypeError, AttributeError):
                    pass

        class starresults( namedtuple(comname, results.keys()) ):
            def __repr__(self):
                return _hdstrace_print(self)

        result = starresults(**results)
    except IOError:
        result = None

    return result



def _hds_value_get(hdscomp):
    """
    Get a value from an HDS component.

     - adds an '_' to any python reserved keywords.
     - strip white space from strings.

    Return tuple of name, value and type.
    """
    name = hdscomp.name.lower()
    if iskeyword(name):
        name += '_'
    value = hdscomp.get()

    # Remove white space from string objects.
    if 'char' in hdscomp.type.lower():
        if hdscomp.shape:
            value = [i.strip() for i in value]
        else:
            value = value.strip()

    type_ = hdscomp.type
    return name, value, type_



def _hds_iterate_components(hdscomp):

    """Iterate through HDS structure.

    Return nested dictionaries representing the object.

    """
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


def _hdstrace_print(results):

    """
    Print the results of get_hds_values prettily.
    """
    output = []
    if results:
        maxlength = len(max(results._fields, key=len))
        space = 4

        for i in results._asdict().items():

            if isinstance(i[1], list) and len(str(i[1])) > 79 - maxlength - space:
                j = ['['+' ' + str(i[1][0])] +  \
                    [' '*(maxlength+space+2) + str(n) for n in i[1][1:]] + \
                    [' '*(maxlength+space) + ']']
                value = '\n'.join(j)
            else:
                value = i[1]
            output.append('{:>{width}}'.format(str(i[0]), width=maxlength) + ' '*space + str(value))
        return '\n'.join(output)
    else:
        return ''

