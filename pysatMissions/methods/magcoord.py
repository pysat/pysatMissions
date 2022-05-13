"""Routines for projecting aacgmv2 and apexpy model values onto pysat instruments.
"""

import aacgmv2
import pysat

try:
    # Warn user if apexpy is not configured.  Bypass needed to function on
    # readthedocs.  Use of apexpy functions elsewhere in code will produce
    # errors.
    import apexpy
except ImportError as ierr:
    pysat.logger.warning(" ".join(["apexpy module could not be imported.",
                                   "apexpy interface won't work.",
                                   "Failed with error:", str(ierr)]))


def add_aacgm_coordinates(inst, glat_label='glat', glong_label='glong',
                          alt_label='alt'):
    """Add AACGM coordinates to instrument object using AACGMV2 package.

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
        call inst.custom.attach(add_quasi_dipole_coordinates,
        kwargs={'glat_label': 'custom_label'})

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


def add_quasi_dipole_coordinates(inst, glat_label='glat', glong_label='glong',
                                 alt_label='alt'):
    """Add quasi-dipole coordinates to instrument object using Apexpy package.

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
        call inst.custom.attach(add_quasi_dipole_coordinates,
        kwargs={'glat_label': 'custom_label'})

    """

    ap = apexpy.Apex(date=inst.date)

    qd_lat = []
    qd_lon = []
    mlt = []
    for lat, lon, alt, time in zip(inst[glat_label], inst[glong_label],
                                   inst[alt_label], inst.data.index):
        # Quasi-dipole latitude and longitude from geodetic coords
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
