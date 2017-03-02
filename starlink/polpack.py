"""
Runs commands from the Starlink POLPACK package.

Autogenerated from the starlink .hlp and .ifl files,
by python-starscripts/generate_functions.py.
"""

from . import wrapper


def polbin(in_, out, **kwargs):
    """
    Bins a catalogue containing Stokes parameters.

    Runs the command: $POLPACK_DIR/polbin .

    Arguments
    ---------
    `in_` : str
        Input catalogue

    out : str
        Output catalogue


    Keyword Arguments
    -----------------
    box : List[float]
        Spatial bin size (pixels)

    debias : bool
        Remove statistical bias? [!]

    integrate : bool
        Integrate all input vectors into a single vector? [FALSE]

    method : str
        Binning method [MEDIAN]

    minval : int
        Min. number of good input values per bin [1]

    radec : bool
        Produce RA & DEC columns, if possible? [current value]

    sigmas : float
        Clipping limit (standard deviations) [4.0]

    zbox : float
        Spectral bin size (pixels)


    Notes
    -----
    See http://www.starlink.ac.uk/cgi-bin/htxserver/sun223.htx/sun223.html?xref_POLBIN
    for full documentation of this command in the latest Starlink release

    """
    return wrapper.starcomm("$POLPACK_DIR/polbin", "polbin", in_, out, **kwargs)


def polcal(in_, out, **kwargs):
    """
    Converts a set of analysed intensity images into a cube holding Stokes

    Runs the command: $POLPACK_DIR/polcal .

    Arguments
    ---------
    `in_` : str,filename
        Input intensity images

    out : str,filename
        Output Stokes cube


    Keyword Arguments
    -----------------
    dezero : bool
        Calculate zero-point corrections for the input data? [FALSE]

    dualbeam : bool
        Is the dual-beam algorithm to be used? [!]

    etol : float
        Tolerence for E factor convergence [0.01]

    ilevel : int
        Level of information to display [1]

    maxit : int
        Maximum number of iterations [dyn.]

    minfrac : float
        Minimum fraction of good input pixels required [0.0]

    nsigma : float
        Rejection threshold in single-beam mode [3.0]

    pmode : str
        Polarimetric mode (LINEAR or CIRCULAR) [LINEAR]

    setvar : bool
        Store estimated variances in input images? [FALSE]

    skysup : float
        Sky supression factor [10]

    smbox : int
        Size of Stokes vector smoothing box, in pixels [3]

    step : int
        Correlation length of the noise, in pixels [1]

    title : str
        Title for output NDF [dyn.]

    tolr : int
        Iterative convergence criterion in single-beam mode [0]

    tols : float
        Scale factor tolerance for image inter-comparisons [0.001]

    tolz : float
        Zero point tolerance for image inter-comparisons [0.05]

    trimbad : bool
        Trim the output cube to exclude any bad borders? [FALSE]

    variance : bool
        Are output variance values to be generated? [!]

    weights : int
        Scheme for choosing weights for input intensity values [1]


    Notes
    -----
    See http://www.starlink.ac.uk/cgi-bin/htxserver/sun223.htx/sun223.html?xref_POLCAL
    for full documentation of this command in the latest Starlink release

    """
    return wrapper.starcomm("$POLPACK_DIR/polcal", "polcal", in_, out, **kwargs)


def polcent(ndf, infile, outfile, **kwargs):
    """
    Find the centroid of a set of positions in an image.

    Runs the command: $POLPACK_DIR/polcent .

    Arguments
    ---------
    ndf : str,filename
        Input image

    infile : str
        Text file containing initial positions

    outfile : str
        Text file to receive accurate positions


    Keyword Arguments
    -----------------
    isize : int
        Size of search box [9]

    maxiter : int
        Maximum number of refining iterations [3]

    maxshift : float
        Maximum shift in position [5.5]

    positive : bool
        Features have positive signal [TRUE]

    toler : float
        Positional tolerance in centroid [0.05]


    Returns
    -------
    xyout : str
        Object to contain the x an y centroid positions


    Notes
    -----
    See http://www.starlink.ac.uk/cgi-bin/htxserver/sun223.htx/sun223.html?xref_POLCENT
    for full documentation of this command in the latest Starlink release

    """
    return wrapper.starcomm("$POLPACK_DIR/polcent", "polcent", ndf, infile, outfile, **kwargs)


def polexp(in_, **kwargs):
    """
    Copies information from the POLPACK extension to named FITS keywords.

    Runs the command: $POLPACK_DIR/polexp .

    Arguments
    ---------
    `in_` : str
        Input images


    Keyword Arguments
    -----------------
    namelist : str
        File to contain a list of the NDFs [!]


    Notes
    -----
    See http://www.starlink.ac.uk/cgi-bin/htxserver/sun223.htx/sun223.html?xref_POLEXP
    for full documentation of this command in the latest Starlink release

    """
    return wrapper.starcomm("$POLPACK_DIR/polexp", "polexp", in_, **kwargs)


def polexpx(in_, **kwargs):
    """
    Copies information from the POLPACK extension to named FITS keywords.

    Runs the command: $POLPACK_DIR/polexpx .

    Arguments
    ---------
    `in_` : str,filename
        Input NDF


    Notes
    -----
    See http://www.starlink.ac.uk/cgi-bin/htxserver/sun223.htx/sun223.html?xref_POLEXPX
    for full documentation of this command in the latest Starlink release

    """
    return wrapper.starcomm("$POLPACK_DIR/polexpx", "polexpx", in_, **kwargs)


def polext(in_, **kwargs):
    """
    Sets explicit values in the POLPACK extension.

    Runs the command: $POLPACK_DIR/polext .

    Arguments
    ---------
    `in_` : str
        Input images


    Keyword Arguments
    -----------------
    angrot : float
        A new ANGROT value [!]

    anlang : float
        A new ANLANG value [!]

    eps : float
        A new EPS value [!]

    filter : str
        A new FILTER value [!]

    imgid : str
        New IMGID value(s) [!]

    namelist : str
        File to contain a list of the NDFs [!]

    ray : str
        A new RAY value [!]

    stokes : str
        A new STOKES value [!]

    t : float
        A new T value [!]

    wplate : str
        A new WPLATE value [!]


    Returns
    -------
    vangrot : float

    vanlang : float

    veps : float

    vfilter : str

    vimgid : str

    vray : str

    vstokes : str

    vt : float

    vversion : str

    vwplate : float


    Notes
    -----
    See http://www.starlink.ac.uk/cgi-bin/htxserver/sun223.htx/sun223.html?xref_POLEXT
    for full documentation of this command in the latest Starlink release

    """
    return wrapper.starcomm("$POLPACK_DIR/polext", "polext", in_, **kwargs)


def polimage(in_, out, coldat, **kwargs):
    """
    Converts a catalogue into an NDF.

    Runs the command: $POLPACK_DIR/polimage .

    Arguments
    ---------
    `in_` : str
        Input catalogue

    out : str,filename
        Output image

    coldat : str
        Name of catalogue column holding data values


    Keyword Arguments
    -----------------
    colvar : str
        Name of catalogue column holding variances [!]

    colx : str
        Name of catalogue column holding X positions [X]

    coly : str
        Name of catalogue column holding Y positions [Y]

    method : str
        Binning method [MEAN]

    colz : str
        Name of catalogue column holding Z positions [dyn.]

    box : List[float]
        Bin size [1.0]

    minval : int
        Min. number of good input values per bin [1]

    shape : bool
        Use spatial information in the input catalogue? [TRUE]

    sigmas : float
        Clipping limit (standard deviations) [4.0]


    Notes
    -----
    See http://www.starlink.ac.uk/cgi-bin/htxserver/sun223.htx/sun223.html?xref_POLIMAGE
    for full documentation of this command in the latest Starlink release

    """
    return wrapper.starcomm("$POLPACK_DIR/polimage", "polimage", in_, out, coldat, **kwargs)


def polimp(in_, **kwargs):
    """
    Copies FITS keyword values into the POLPACK extension.

    Runs the command: $POLPACK_DIR/polimp .

    Arguments
    ---------
    `in_` : str
        Input images


    Keyword Arguments
    -----------------
    table : str
        Import control table [!]

    abort : bool
        Abort if any data file cannot be processed? [dyn.]

    namelist : str
        File to contain a list of the NDFs [!]


    Notes
    -----
    See http://www.starlink.ac.uk/cgi-bin/htxserver/sun223.htx/sun223.html?xref_POLIMP
    for full documentation of this command in the latest Starlink release

    """
    return wrapper.starcomm("$POLPACK_DIR/polimp", "polimp", in_, **kwargs)


def polimpx(in_, **kwargs):
    """
    Copies FITS keyword values into the POLPACK extension.

    Runs the command: $POLPACK_DIR/polimpx .

    Arguments
    ---------
    `in_` : str,filename
        Input NDF


    Notes
    -----
    See http://www.starlink.ac.uk/cgi-bin/htxserver/sun223.htx/sun223.html?xref_POLIMPX
    for full documentation of this command in the latest Starlink release

    """
    return wrapper.starcomm("$POLPACK_DIR/polimpx", "polimpx", in_, **kwargs)


def polka(in_, out_s, **kwargs):
    """
    Creates Stokes vectors from a set of 2-dimensional intensity frames.

    Runs the command: $POLPACK_DIR/polka .

    Arguments
    ---------
    `in_` : str,filename
        Input object frames

    out_s : str
        Output cube for Stokes parameters


    Keyword Arguments
    -----------------
    badcol : str
        Colour with which to mark missing pixel data [CYAN]

    curcol : str
        Colour with which to mark current objects [RED]

    dpi : int
        Screen dots per inch [!]

    dualbeam : bool
        Run in dual-beam mode? [TRUE]

    fittype : int
        Fit type (1-5) for aligning images [1]

    helparea : bool
        Display the help area? [TRUE]

    items : str
        Required items in the status area (private) [.0]

    logfile : str
        The name of a file in which to store all ATASK messages. [!]

    oefittype : int
        Fit type (1-5) for aligning O and E rays [1]

    out : str
        Aligned output intensity images [*_A]

    out_e : str
        Aligned output images holding E-ray areas [*_E]

    out_o : str
        Aligned output images holding O-ray areas [*_O]

    percentiles : List[float]
        Percentiles for scaling [5,95]

    pmode : str
        Type of polarisation being measured [Linear]

    pol : bool
        Processing polarimetry data? [TRUE]

    psfsize : int
        Typical size of star-like image features (in pixels) [3]

    refcol : str
        Colour with which to mark reference objects [GREEN]

    refin : str,filename
        Reference frame [!]

    selcol : str
        Colour with which to mark the selected area [RED]

    skyframes : str,filename
        Input sky frames [!]

    skyoff : bool
        Subtract the sky background off the output images? [TRUE]

    skypar : int
        Order of polynomial sky fit on each axis [0]

    starthelp : bool
        Display hyper-text help automatically at start-up? [TRUE]

    statusarea : bool
        Display the status area? [TRUE]

    view : str
        View new images zoomed or unzoomed? [ZOOMED]

    xhair : bool
        Use a cross-hair over the image display area? [TRUE]

    xhaircol : str
        Colour with which to draw the cross-hair (if required) [YELLOW]


    Notes
    -----
    See http://www.starlink.ac.uk/cgi-bin/htxserver/sun223.htx/sun223.html?xref_POLKA
    for full documentation of this command in the latest Starlink release

    """
    return wrapper.starcomm("$POLPACK_DIR/polka", "polka", in_, out_s, **kwargs)


def polplot(cat, **kwargs):
    """
    Plots a 2-dimensional vector map.

    Runs the command: $POLPACK_DIR/polplot .

    Arguments
    ---------
    cat : str
        Input catalogue


    Keyword Arguments
    -----------------
    angrot : float
        Orientation of reference direction [0.0]

    arrow : float
        Fractional size of arrow heads [0.0]

    axes : bool
        Are annotated axes to be drawn? [TRUE]

    clear : bool
        Is the current picture to be cleared before plotting? [TRUE]

    colang : str
        Name of catalogue column holding vector angles [dyn.]

    colmag : str
        Name of catalogue column holding vector lengths [dyn.]

    colx : str
        Name of catalogue column holding vector X position [dyn.]

    coly : str
        Name of catalogue column holding vector Y position [dyn.]

    colz : str
        Name of catalogue column holding vector Z position [dyn.]

    device : 
        Name of graphics device [Current graphics device]

    epoch : float
        Epoch of observation

    fill : bool
        Fill the plotting area? [FALSE]

    frame : str
        Required co-ordinate Frame [!]

    just : str
        Vector justification ["Centre"]

    key : bool
        Do you want a key showing the vector scale? [TRUE]

    keypos : List[float]
        Horizontal and vertical position of key [current value]

    keystyle : str
        Plotting style for the key [current value]

    keyvec : float
        Key vector magnitude [dyn.]

    lbnd : List[float]
        Co-ordinates at lower left corner of plotting area [!]

    margin : List[float]
        Widths of margins around DATA picture [dyn.]

    negate : bool
        Are the supplied angles to be negated? [FALSE]

    style : str
        Plotting style for the annotated axes and vectors [current value]

    ubnd : List[float]
        Co-ordinates at upper right corner of plotting area [!]

    vscale : float
        Data value for a 1-centimetre vector [dyn.]

    zaxval : str
        The Z axis value to plot

    zcolval : str
        The Z column value to plot [!]


    Notes
    -----
    See http://www.starlink.ac.uk/cgi-bin/htxserver/sun223.htx/sun223.html?xref_POLPLOT
    for full documentation of this command in the latest Starlink release

    """
    return wrapper.starcomm("$POLPACK_DIR/polplot", "polplot", cat, **kwargs)


def polprep(in_, out, ref, **kwargs):
    """
    Prepare an input image for use by Polka.

    Runs the command: $POLPACK_DIR/polprep .

    Arguments
    ---------
    `in_` : str,filename
        Input NDF structure

    out : str,filename
        Output NDF structure

    ref : bool
        Is this the reference image?


    Returns
    -------
    frame : str
        The Domain name


    Notes
    -----
    See http://www.starlink.ac.uk/cgi-bin/htxserver/sun223.htx/sun223.html?xref_POLPREP
    for full documentation of this command in the latest Starlink release

    """
    return wrapper.starcomm("$POLPACK_DIR/polprep", "polprep", in_, out, ref, **kwargs)


def polrdtcl(in_, ref, out, **kwargs):
    """
    Reads a text file holding the contents of a specified catalogue in

    Runs the command: $POLPACK_DIR/polrdtcl .

    Arguments
    ---------
    `in_` : str
        Input text file

    ref : str
        Reference catalogue

    out : str
        Output catalogue


    Notes
    -----
    See http://www.starlink.ac.uk/cgi-bin/htxserver/sun223.htx/sun223.html?xref_POLRDTCL
    for full documentation of this command in the latest Starlink release

    """
    return wrapper.starcomm("$POLPACK_DIR/polrdtcl", "polrdtcl", in_, ref, out, **kwargs)


def polrotref(qin, uin, qout, uout, **kwargs):
    """
    Rotate the reference direction in a pair of Q and U images.

    Runs the command: $POLPACK_DIR/polrotref .

    Arguments
    ---------
    qin : str,filename
        Input Q NDF

    uin : str,filename
        Input U NDF

    qout : str,filename
        Output Q NDF

    uout : str,filename
        Output U NDF


    Keyword Arguments
    -----------------
    like : str,filename
        Template Q or U NDF [!]

    axis : int
        Index of axis to use as reference direction [2]

    epoch : float
        Epoch of observation

    frame : str
        Co-ordinate Frame defining new reference direction ["PIXEL"]

    useaxis : str
        The WCS axes spanning the spatial plane [!]


    Notes
    -----
    See http://www.starlink.ac.uk/cgi-bin/htxserver/sun223.htx/sun223.html?xref_POLROTREF
    for full documentation of this command in the latest Starlink release

    """
    return wrapper.starcomm("$POLPACK_DIR/polrotref", "polrotref", qin, uin, qout, uout, **kwargs)


def polsim(cube, in_, **kwargs):
    """
    Produces intensity data corresponding to given Stokes vectors.

    Runs the command: $POLPACK_DIR/polsim .

    Arguments
    ---------
    cube : str,filename
        Input Stokes cube

    `in_` : str
        Input intensity images


    Returns
    -------
    out : str
        Output intensity images


    Notes
    -----
    See http://www.starlink.ac.uk/cgi-bin/htxserver/sun223.htx/sun223.html?xref_POLSIM
    for full documentation of this command in the latest Starlink release

    """
    return wrapper.starcomm("$POLPACK_DIR/polsim", "polsim", cube, in_, **kwargs)


def polstack(in_, out, **kwargs):
    """
    Stack a set of intensity images.

    Runs the command: $POLPACK_DIR/polstack .

    Arguments
    ---------
    `in_` : str,filename
        Input intensity frames

    out : str,filename
        Output intensity images


    Keyword Arguments
    -----------------
    bin : float
        Bin size, in degrees [10]

    ilevel : int
        Screen information level [1]

    minin : int
        Minimum number of input images per output image [3]

    origin : float
        Analysis angle at start of first bin, in degrees [0.0]

    stack : str,filename
        3D output stack [!]

    twopi : bool
        Bin analysis angles in range 0 to 360 degrees? [FALSE]


    Notes
    -----
    See http://www.starlink.ac.uk/cgi-bin/htxserver/sun223.htx/sun223.html?xref_POLSTACK
    for full documentation of this command in the latest Starlink release

    """
    return wrapper.starcomm("$POLPACK_DIR/polstack", "polstack", in_, out, **kwargs)


def polvec(in_, cat, **kwargs):
    """
    Calculates polarization vectors from supplied Stokes parameters.

    Runs the command: $POLPACK_DIR/polvec .

    Arguments
    ---------
    `in_` : str,filename
        Input Stokes cube

    cat : str
        Output catalogue


    Keyword Arguments
    -----------------
    i : str,filename
        Total intensity [!]

    p : str,filename
        Percentage polarisation [!]

    ang : str,filename
        Polarisation angle [!]

    ip : str,filename
        Polarised intensity [!]

    q : str,filename
        Stokes parameter Q [!]

    u : str,filename
        Stokes parameter U [!]

    v : str,filename
        Stokes parameter V [!]

    box : List[int]
        Bin size [1]

    debias : bool
        Remove statistical bias? [!]

    method : str
        Binning method [MEDIAN]

    radec : bool
        Produce RA & DEC columns, if possible? [current value]

    refupdate : bool
        Update the output reference direction? [TRUE]

    sigmas : float
        Clipping limit (standard deviations) [4.0]

    variance : bool
        Are variance values to be generated? [TRUE]

    wlim : float
        Min. fraction of good input values per bin [0.0]


    Notes
    -----
    See http://www.starlink.ac.uk/cgi-bin/htxserver/sun223.htx/sun223.html?xref_POLVEC
    for full documentation of this command in the latest Starlink release

    """
    return wrapper.starcomm("$POLPACK_DIR/polvec", "polvec", in_, cat, **kwargs)


def polversion(*args, **kwargs):
    """
    Checks the package version number.

    Runs the command: $POLPACK_DIR/polversion .

    Keyword Arguments
    -----------------
    compare : str
        The version string for comparison [!]


    Returns
    -------
    result : int


    Notes
    -----
    See http://www.starlink.ac.uk/cgi-bin/htxserver/sun223.htx/sun223.html?xref_POLVERSION
    for full documentation of this command in the latest Starlink release

    """
    return wrapper.starcomm("$POLPACK_DIR/polversion", "polversion", *args, **kwargs)


def polwrtcl(in_, out, **kwargs):
    """
    Creates a text file holding the contents of a specified catalogue in

    Runs the command: $POLPACK_DIR/polwrtcl .

    Arguments
    ---------
    `in_` : str
        Input catalogue

    out : str
        Output text file


    Notes
    -----
    See http://www.starlink.ac.uk/cgi-bin/htxserver/sun223.htx/sun223.html?xref_POLWRTCL
    for full documentation of this command in the latest Starlink release

    """
    return wrapper.starcomm("$POLPACK_DIR/polwrtcl", "polwrtcl", in_, out, **kwargs)


def polzconv(cat, **kwargs):
    """
    Convert a Z axis value to a Z column value

    Runs the command: $POLPACK_DIR/polzconv .

    Arguments
    ---------
    cat : str
        Input catalogue


    Keyword Arguments
    -----------------
    colx : str
        Name of catalogue column holding vector X position [dyn.]

    coly : str
        Name of catalogue column holding vector Y position [dyn.]

    colz : str
        Name of catalogue column holding vector Z position [dyn.]

    zaxval : str
        The Z axis value to convert

    zcolval : str
        The Z column value to convert [!]


    Returns
    -------
    zaxuse : str
        The Z axis value to use

    zcoluse : str
        The Z column value to use


    Notes
    -----
    See http://www.starlink.ac.uk/cgi-bin/htxserver/sun223.htx/sun223.html?xref_POLZCONV
    for full documentation of this command in the latest Starlink release

    """
    return wrapper.starcomm("$POLPACK_DIR/polzconv", "polzconv", cat, **kwargs)

