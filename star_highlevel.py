

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
