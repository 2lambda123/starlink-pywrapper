"""
Module for running PICARD recipes from python.
"""

from . import wrapper

def calc_scuba2_avpspec(*args, **kwargs):
    """Run PICARD'S CALC_SCUBA2_AVPSPEC recipe."""
    return wrapper.picard('CALC_SCUBA2_AVPSPEC', *args, **kwargs)


def calc_scuba2_fcf(*args, **kwargs):
    """Run PICARD'S CALC_SCUBA2_FCF recipe."""
    return wrapper.picard('CALC_SCUBA2_FCF', *args, **kwargs)


def calc_scuba2_nefd(*args, **kwargs):
    """Run PICARD'S CALC_SCUBA2_NEFD recipe."""
    return wrapper.picard('CALC_SCUBA2_NEFD', *args, **kwargs)


def calibrate_scuba2_data(*args, **kwargs):
    """Run PICARD'S CALIBRATE_SCUBA2_DATA recipe."""
    return wrapper.picard('CALIBRATE_SCUBA2_DATA', *args, **kwargs)


def coadd_jsa_tiles(*args, **kwargs):
    """Run PICARD'S COADD_JSA_TILES recipe."""
    return wrapper.picard('COADD_JSA_TILES', *args, **kwargs)


def create_moments_map(*args, **kwargs):
    """Run PICARD'S CREATE_MOMENTS_MAP recipe."""
    return wrapper.picard('CREATE_MOMENTS_MAP', *args, **kwargs)


def create_png(*args, **kwargs):
    """Run PICARD'S CREATE_PNG recipe."""
    return wrapper.picard('CREATE_PNG', *args, **kwargs)


def crop_scuba2_images(*args, **kwargs):
    """Run PICARD'S CROP_SCUBA2_IMAGES recipe."""
    return wrapper.picard('CROP_SCUBA2_IMAGES', *args, **kwargs)


def estimate_image_alignment(*args, **kwargs):
    """Run PICARD'S ESTIMATE_IMAGE_ALIGNMENT recipe."""
    return wrapper.picard('ESTIMATE_IMAGE_ALIGNMENT', *args, **kwargs)


def jsa_catalogue(*args, **kwargs):
    """Run PICARD'S JSA_CATALOGUE recipe."""
    return wrapper.picard('JSA_CATALOGUE', *args, **kwargs)


def mosaic_jcmt_images(*args, **kwargs):
    """Run PICARD'S MOSAIC_JCMT_IMAGES recipe."""
    return wrapper.picard('MOSAIC_JCMT_IMAGES', *args, **kwargs)


def picard_demonstrator(*args, **kwargs):
    """Run PICARD'S PICARD_DEMONSTRATOR recipe."""
    return wrapper.picard('PICARD_DEMONSTRATOR', *args, **kwargs)


def scuba2_check_cal(*args, **kwargs):
    """Run PICARD'S SCUBA2_CHECK_CAL recipe."""
    return wrapper.picard('SCUBA2_CHECK_CAL', *args, **kwargs)


def scuba2_check_rms(*args, **kwargs):
    """Run PICARD'S SCUBA2_CHECK_RMS recipe."""
    return wrapper.picard('SCUBA2_CHECK_RMS', *args, **kwargs)


def scuba2_display_pca(*args, **kwargs):
    """Run PICARD'S SCUBA2_DISPLAY_PCA recipe."""
    return wrapper.picard('SCUBA2_DISPLAY_PCA', *args, **kwargs)


def scuba2_jackknife(*args, **kwargs):
    """Run PICARD'S SCUBA2_JACKKNIFE recipe."""
    return wrapper.picard('SCUBA2_JACKKNIFE', *args, **kwargs)


def scuba2_jackknife_psf(*args, **kwargs):
    """Run PICARD'S SCUBA2_JACKKNIFE_PSF recipe."""
    return wrapper.picard('SCUBA2_JACKKNIFE_PSF', *args, **kwargs)


def scuba2_mapstats(*args, **kwargs):
    """Run PICARD'S SCUBA2_MAPSTATS recipe."""
    return wrapper.picard('SCUBA2_MAPSTATS', *args, **kwargs)


def scuba2_map_pspec(*args, **kwargs):
    """Run PICARD'S SCUBA2_MAP_PSPEC recipe."""
    return wrapper.picard('SCUBA2_MAP_PSPEC', *args, **kwargs)


def scuba2_matched_filter(*args, **kwargs):
    """Run PICARD'S SCUBA2_MATCHED_FILTER recipe."""
    return wrapper.picard('SCUBA2_MATCHED_FILTER', *args, **kwargs)


def scuba2_photom(*args, **kwargs):
    """Run PICARD'S SCUBA2_PHOTOM recipe."""
    return wrapper.picard('SCUBA2_PHOTOM', *args, **kwargs)


def scuba2_register_images(*args, **kwargs):
    """Run PICARD'S SCUBA2_REGISTER_IMAGES recipe."""
    return wrapper.picard('SCUBA2_REGISTER_IMAGES', *args, **kwargs)


def scuba2_remove_background(*args, **kwargs):
    """Run PICARD'S SCUBA2_REMOVE_BACKGROUND recipe."""
    return wrapper.picard('SCUBA2_REMOVE_BACKGROUND', *args, **kwargs)


def scuba2_sassy(*args, **kwargs):
    """Run PICARD'S SCUBA2_SASSY recipe."""
    return wrapper.picard('SCUBA2_SASSY', *args, **kwargs)


def stack_jcmt_frames(*args, **kwargs):
    """Run PICARD'S STACK_JCMT_FRAMES recipe."""
    return wrapper.picard('STACK_JCMT_FRAMES', *args, **kwargs)


def uncalibrate_scuba2_data(*args, **kwargs):
    """Run PICARD'S UNCALIBRATE_SCUBA2_DATA recipe."""
    return wrapper.picard('UNCALIBRATE_SCUBA2_DATA', *args, **kwargs)


def untrim_jsa_tiles(*args, **kwargs):
    """Run PICARD'S UNTRIM_JSA_TILES recipe."""
    return wrapper.picard('UNTRIM_JSA_TILES', *args, **kwargs)

