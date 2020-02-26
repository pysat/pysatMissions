"""Provides default routines for projecting aacgmv2 model values onto locations
from pysat instruments.

"""

import aacgmv2


def add_aacgm_coordinates(inst, glat_label='glat', glong_label='glong',
                          alt_label='alt'):
    """
    Uses AACGMV2 package to add AACGM coordinates to instrument object.

    The Altitude Adjusted Corrected Geomagnetic Coordinates library is used
    to calculate the latitude, longitude, and local time
    of the spacecraft with respect to the geomagnetic field.

    Parameters
    ----------
    inst : pysat.Instrument
        instrument object including lat, lon, and alt as timeseries
    glat_label : string
        label used in inst to identify WGS84 geodetic latitude (degrees N)
    glong_label : string
        label used in inst to identify WGS84 geodetic longitude (degrees E)
    alt_label : string
        label used in inst to identify WGS84 geodetic altitude (km, height
        above surface)

    Returns
    -------
    inst
        Input pysat.Instrument object modified to include quasi-dipole
        coordinates, 'aacgm_lat' for magnetic latitude, 'aacgm_long' for
        longitude, and 'aacgm_mlt' for magnetic local time.
    
    Example
    -------
        # function added velow modifies the inst object upon every inst.load
        call inst.custom.add(add_quasi_dipole_coordinates, 'modify',
        glat_label='custom_label')

    """

    aalat = []
    aalon = []
    mlt = []
    for lat, lon, alt, time in zip(inst[glat_label], inst[glong_label],
                                   inst[alt_label], inst.data.index):
        # aacgmv2 latitude and longitude from geodetic coords
        tlat, tlon, tmlt = aacgmv2.get_aacgm_coord(lat, lon, alt, time)
        aalat.append(tlat)
        aalon.append(tlon)
        mlt.append(tmlt)

    inst['aacgm_lat'] = aalat
    inst['aacgm_long'] = aalon
    inst['aacgm_mlt'] = mlt

    inst.meta['aacgm_lat'] = {'units': 'degrees',
                              'long_name': 'AACGM latitude'}
    inst.meta['aacgm_long'] = {'units': 'degrees',
                               'long_name': 'AACGM longitude'}
    inst.meta['aacgm_mlt'] = {'units': 'hrs',
                              'long_name': 'AACGM Magnetic local time'}

    return
