"""Provides default routines for projecting apexpy values onto locations
from pysat instruments.

"""

import apexpy


def add_quasi_dipole_coordinates(inst, glat_label='glat', glong_label='glong',
                                 alt_label='alt'):
    """
    Uses Apexpy package to add quasi-dipole coordinates to instrument object.

    The Quasi-Dipole coordinate system includes both the tilt and offset of the
    geomagnetic field to calculate the latitude, longitude, and local time
    of the spacecraft with respect to the geomagnetic field.

    This system is preferred over AACGM near the equator for LEO satellites.

    Parameters
    ----------
    inst : pysat.Instrument
        instrument object including lat, lon, and alt as timeseries
    glat_label : string
        label used in inst to identify WGS84 geodetic latitude (degrees)
    glong_label : string
        label used in inst to identify WGS84 geodetic longitude (degrees)
    alt_label : string
        label used in inst to identify WGS84 geodetic altitude (km, height
        above surface)

    Returns
    -------
    inst
        Input pysat.Instrument object modified to include quasi-dipole
        coordinates, 'qd_lat' for magnetic latitude, 'qd_long' for longitude,
        and 'mlt' for magnetic local time.
    Example
    -------
        # function added velow modifies the inst object upon every inst.load
        call inst.custom.add(add_quasi_dipole_coordinates, 'modify',
        glat_label='custom_label')

    """

    ap = apexpy.Apex(date=inst.date)

    qd_lat = []
    qd_lon = []
    mlt = []
    for lat, lon, alt, time in zip(inst[glat_label], inst[glong_label],
                                   inst[alt_label], inst.data.index):
        # quasi-dipole latitude and longitude from geodetic coords
        tlat, tlon = ap.geo2qd(lat, lon, alt)
        qd_lat.append(tlat)
        qd_lon.append(tlon)
        mlt.append(ap.mlon2mlt(tlon, time))

    inst['qd_lat'] = qd_lat
    inst['qd_long'] = qd_lon
    inst['mlt'] = mlt

    inst.meta['qd_lat'] = {'units': 'degrees',
                           'long_name': 'Quasi dipole latitude'}
    inst.meta['qd_long'] = {'units': 'degrees',
                            'long_name': 'Quasi dipole longitude'}
    inst.meta['mlt'] = {'units': 'hrs',
                        'long_name': 'Magnetic local time'}

    return
