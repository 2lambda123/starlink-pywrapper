"""Module to run the Starlink FLUXES package.

Unlike other similar modules for e.g. KAPPA, SMURF, this module is
written by hand as the auto generated scripts don't work, and there is
effectively only one fluxes command and we don't change it very often.

"""

from collections import namedtuple
import datetime

from starlink import wrapper
from starlink.hdsutils import _hdstrace_print


def get_flux(planet, date, filter_=850):
    """
    Return the FLUXES calculated flux/T for a planet, the sun or the
    moon.

    Arguments
    ---------
    planet: str
      Name of planet for calculation. Must be one of: SUN, MERCURY,
      VENUS, MARS, JUPITER, SATURN, URANUS, NEPTUNE, PLUTO, MOON.

    date: str or datetime or date

      Datetime to perform calculation for. If string, should be in
      format 'YYYY-MM-DDTHH:MM:SS.S'. Optionally, only the YYYY-MM-DD
      part can be supplied, and it will assume '00:00:00' for the
      time. Otherwise a standard date or datetime object can be supplied.


    filter: int, optional
      The filter wavelength (in microns). Must be one of: 850, 450,
      1300, 868, 434. [850]


    Returns
    -------

    A named tuple containing:

    hpbw: float
        The half power beam width used to calaculate F_BEAM (arcseconds).

    f_centre: float
       The centre frequency of the selected filter (GHz).

    f_width: float
       The filter width (GHz).

    f_total: float
       The total flux (Jy).

    f_beam: float
       The total flux in the beam (Jy).

    t_bright: float
       The brightness temperature of the planet (K).

    t_error: float
       The error in the brightness temperature (K).

    semi_diam: float
       Semi-diameter of the selected planet (arcsec).

    solid_ang: float
       Solid angle of the selected planet (steradians).

    time: string
       Time used for calculation as 'HH MM SS'.

    date: string
       Date used for calculation, as 'DD MM YY'.

    filter: string
       Filter used for caclulation.

    Notes:
    ------
    If you want to run fluxes more directly, please use the
    starlink.wrapper.starcomm command directly. This will support all
    the fluxes options.

    For more information on fluxes, please see SUN/213 in your
    Starlink distribution (or visit
    http://www.starlink.ac.uk/docs/sun213.htx/sun213.html to see the
    documentation from the latest release).

    """

    try:
        fluxdate = date.strftime('"%d %m %y"')
        fluxtime = date.strftime('"%H %M %S"')
    except AttributeError:
        # Assume it is a string.
        if 'T' in date:
            fluxdatetime = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%f')
        else:
            fluxdatetime = datetime.datetime.strptime(date, '%Y-%m-%d')

        fluxdate = fluxdatetime.strftime('"%d %m %y"')
        fluxtime = fluxdatetime.strftime('"%H %M %S"')

    except:
        raise("Could not parse date and/or time string {}".format(date))

    # Run fluxes.
    fluxresult = wrapper.starcomm('$FLUXES_DIR/fluxes',
                                    'fluxes',
                                    pos='n', flu='y', screen='n', ofl='n', now='n', apass='n',
                                    planet=planet, date=fluxdate, time=fluxtime,
                                    filter_=filter_)

    # Remove unnecessary values from output.
    fluxdict = fluxresult._asdict()
    fluxdict.pop('flu')
    fluxdict.pop('apass')
    fluxdict.pop('now')
    fluxdict.pop('ofl')
    fluxdict.pop('pos')

    # Create fluxes named tuple type again from dict.
    class starresults( namedtuple('fluxes', fluxdict.keys()) ):
            def __repr__(self):
                return _hdstrace_print(self)
    fluxresult = starresults(**fluxdict)

    return fluxresult



#TODO: create version for when you want all planets -- create output
#file and read it into an appropriate object?
