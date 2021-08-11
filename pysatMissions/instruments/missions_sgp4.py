# -*- coding: utf-8 -*-
"""Simulate satellite orbit data using Two Line Elements (TLEs) and SGP4.

Properties
----------
platform
    'missions'
name
    'sgp4'
tag
    None supported
inst_id
    None supported

"""

import datetime as dt
import functools
import numpy as np
import pandas as pds

import pysat
from pysat.instruments.methods import testing as ps_meth
from pysatMissions.instruments import _core as mcore
from pysatMissions.instruments.methods import orbits
from sgp4.api import jday, Satrec, SGP4_ERRORS, WGS72
from geospacepy import terrestrial_spherical as conv_sph
from geospacepy import terrestrial_ellipsoidal as conv_ell

logger = pysat.logger

# -------------------------------
# Required Instrument attributes
platform = 'missions'
name = 'sgp4'
tags = {'': 'Satellite simulation data set'}
inst_ids = {'': ['']}

# ------------------
# Testing attributes
_test_dates = {'': {'': dt.datetime(2018, 1, 1)}}


def init(self):
    """Initialize the Instrument object with required values.

    Runs once upon instantiation.

    """

    orbits._check_orbital_params(self.kwargs)

    self.acknowledgements = ' '.join((
        'The project uses the sgp4 library available at',
        'https://github.com/brandon-rhodes/python-sgp4'))
    self.references = ' '.join((
        'Vallado, David A., Paul Crawford, Richard, Hujsak, and T.S. Kelso,',
        '"Revisiting Spacetrack Report #3," presented at the AIAA/AAS',
        'Astrodynamics Specialist Conference, Keystone, CO, 2006',
        'August 21–24.'))
    logger.info(self.acknowledgements)

    return


# Clean method
clean = mcore._clean


def load(fnames, tag=None, inst_id=None, TLE1=None, TLE2=None,
         alt_periapsis=None, alt_apoapsis=None,
         inclination=None, raan=0., arg_periapsis=0., mean_anomaly=0.,
         bstar=0., one_orbit=False, num_samples=None, cadence='1S'):
    """Generate position of satellite in ECI co-ordinates.

    Note
    ----
    Routine is directly called by pysat and not the user.

    Parameters
    ----------
    fnames : list-like collection
        File name that contains date in its name.
    tag : string
        Identifies a particular subset of satellite data
    inst_id : string
        Instrument satellite ID (accepts '' or a number (i.e., '10'), which
        specifies the number of seconds to simulate the satellite)
        (default='')
    TLE1 : string
        First string for Two Line Element. Must be in TLE format
    TLE2 : string
        Second string for Two Line Element. Must be in TLE format
    alt_periapsis : float
        The lowest altitude from the mean planet surface along the orbit (km)
    alt_apoapsis : float or NoneType
        The highest altitude from the mean planet surface along the orbit (km)
        If None, assumed to be equal to periapsis. (default=None)
    inclination : float
        Orbital Inclination in degrees (default=None)
    raan : float
        Right Ascension of the Ascending Node (RAAN) in degrees. This defines
        the orientation of the orbital plane to the generalized reference frame.
        The Ascending Node is the point in the orbit where the spacecraft passes
        through the plane of reference moving northward.  For Earth orbits, the
        location of the RAAN is defined as the angle eastward of the First Point
        of Aries.
        (default=None)
    arg_periapsis : float
        Argument of Periapsis in degrees.  This defines the orientation of the
        ellipse in the orbital plane, as an angle measured from the ascending
        node to the periapsis  (default=None)
    mean_anomaly : float
        The fraction of an elliptical orbit's period that has elapsed since the
        orbiting body passed periapsis.  Note that this is a "fictitious angle"
        (input in degrees) which defines the location of the spacecraft in the
        orbital plane based on the orbital period.
        (default=None)
    bstar : float
        Inverse of the ballistic coefficient. Used to model satellite drag.
        Measured in inverse distance (1 / earth radius). (default=None)
    one_orbit : bool
        Flag to override num_samples and only provide a single orbit.
        (default=False)
    num_samples : int
        Number of samples per day
    cadence : str
        Uses pandas.frequency string formatting ('1S', etc)
        (default='1S')

    Returns
    -------
    data : pandas.DataFrame
        Object containing satellite data
    meta : pysat.Meta
        Object containing metadata such as column names and units

    Example
    -------
    ::

          TLE1='1 25544U 98067A   18135.61844383  .00002728  00000-0  48567-4 0  9998'
          TLE2='2 25544  51.6402 181.0633 0004018  88.8954  22.2246 15.54059185113452'
          inst = pysat.Instrument('pysat', 'sgp4', TLE1=TLE1, TLE2=TLE2)
          inst.load(2018, 1)

    """

    # TLEs (Two Line Elements for ISS)
    # format of TLEs is fixed and available from wikipedia...
    # lines encode list of orbital elements of an Earth-orbiting object
    # for a given point in time
    line1 = '1 25544U 98067A   18135.61844383  .00002728  00000-0  48567-4 0  9998'
    line2 = '2 25544  51.6402 181.0633 0004018  88.8954  22.2246 15.54059185113452'

    # If provided, use user-specified TLEs.  Otherwise use ISS defaults above.
    if TLE1 is not None:
        line1 = TLE1
    if TLE2 is not None:
        line2 = TLE2

    if (num_samples is None) or one_orbit:
        num_samples = 86400

    # Extract list of times from filenames and inst_id
    times, index, dates = ps_meth.generate_times(fnames, num_samples,
                                                 freq=cadence)
    # Calculate epoch for orbital propagator
    epoch = (dates[0] - dt.datetime(1949, 12, 31)).days
    jd, _ = jday(dates[0].year, dates[0].month, dates[0].day, 0, 0, 0)

    if inclination is not None:
        # If an inclination is provided, specify by Keplerian elements
        eccentricity, mean_motion = orbits.convert_to_keplerian(alt_periapsis,
                                                                alt_apoapsis)
        satellite = Satrec()
        # according to module webpage, wgs72 is common
        satellite.sgp4init(WGS72, 'i', 0, epoch, bstar, 0, 0,
                           eccentricity, np.radians(arg_periapsis),
                           np.radians(inclination), np.radians(mean_anomaly),
                           mean_motion, np.radians(raan))
    else:
        # Otherwise, use TLEs
        satellite = Satrec.twoline2rv(line1, line2, WGS72)
        mean_motion = satellite.mean_motion

    if one_orbit:
        ind = times <= (2 * np.pi / mean_motion * 60)
        times = times[ind]
        index = index[ind]

    jd = jd * np.ones(len(times))
    fr = times / 86400.

    err_code, position, velocity = satellite.sgp4_array(jd, fr)

    # Check all propagated values for errors in propagation
    for i in range(1, 7):
        if np.any(err_code == i):
            raise ValueError(SGP4_ERRORS[i])

    # Add ECEF values to instrument.

    pos_ecef = conv_sph.eci2ecef(position, (jd + fr))
    vel_ecef = conv_sph.eci2ecef(velocity, (jd + fr))

    # Convert to geocentric latitude, longitude, altitude.
    lat, lon, rad = conv_sph.ecef_cart2spherical(pos_ecef)
    # Convert to geodetic latitude, longitude, altitude.
    # Ellipsoidal conversions require input in meters.
    geod_lat, geod_lon, geod_alt = conv_ell.ecef_cart2geodetic(pos_ecef * 1000.)

    # Put data into DataFrame
    data = pds.DataFrame({'position_eci_x': position[:, 0],
                          'position_eci_y': position[:, 1],
                          'position_eci_z': position[:, 2],
                          'velocity_eci_x': velocity[:, 0],
                          'velocity_eci_y': velocity[:, 1],
                          'velocity_eci_z': velocity[:, 2],
                          'position_ecef_x': pos_ecef[:, 0],
                          'position_ecef_y': pos_ecef[:, 1],
                          'position_ecef_z': pos_ecef[:, 2],
                          'velocity_ecef_x': vel_ecef[:, 0],
                          'velocity_ecef_y': vel_ecef[:, 1],
                          'velocity_ecef_z': vel_ecef[:, 2],
                          'latitude': lat,
                          'longitude': lon,
                          'mean_altitude': rad - 6371.2,
                          'geod_latitude': geod_lat,
                          'geod_longitude': geod_lon,
                          'geod_altitude': geod_alt / 1000.},  # Convert altitude to km
                         index=index)
    data.index.name = 'Epoch'

    # Create metadata corresponding to variables in load routine
    meta = pysat.Meta()
    meta['Epoch'] = {
        meta.labels.units: 'Milliseconds since 1970-1-1',
        meta.labels.notes: 'UTC time at middle of geophysical measurement.',
        meta.labels.desc: 'UTC seconds',
        meta.labels.name: 'Time index in milliseconds'}
    for v in ['x', 'y', 'z']:
        meta['position_eci_{:}'.format(v)] = {
            meta.labels.units: 'km',
            meta.labels.name: 'ECI {:}-position'.format(v),
            meta.labels.desc: 'Earth Centered Inertial {:}-position'.format(v)}
        meta['velocity_eci_{:}'.format(v)] = {
            meta.labels.units: 'km/s',
            meta.labels.name: 'Satellite velocity ECI-{:}'.format(v),
            meta.labels.desc: 'Satellite velocity along ECI-{:}'.format(v)}
        meta['position_ecef_{:}'.format(v)] = {
            meta.labels.units: 'km',
            meta.labels.notes: 'Calculated using geospacepy.terrestrial_spherical',
            meta.labels.name: 'ECEF {:}-position'.format(v),
            meta.labels.desc: 'Earth Centered Earth Fixed {:}-position'.format(v)}
        meta['velocity_ecef_{:}'.format(v)] = {
            meta.labels.units: 'km',
            meta.labels.notes: 'Calculated using geospacepy.terrestrial_spherical',
            meta.labels.name: 'ECEF {:}-velocity'.format(v),
            meta.labels.desc: 'Earth Centered Earth Fixed {:}-velocity'.format(v)}
    meta['latitude'] = {
        meta.labels.units: 'degrees',
        meta.labels.notes: 'Calculated using geospacepy.terrestrial_spherical',
        meta.labels.name: 'Geocentric Latitude',
        meta.labels.desc: 'Geocentric Latitude of satellite',
        meta.labels.min_val: -90.,
        meta.labels.max_val: 90.}
    meta['longitude'] = {
        meta.labels.units: 'degrees',
        meta.labels.notes: 'Calculated using geospacepy.terrestrial_spherical',
        meta.labels.name: 'Geocentric Longitude',
        meta.labels.desc: 'Geocentric Longitude of satellite',
        meta.labels.min_val: -180.,
        meta.labels.max_val: 180.}
    meta['mean_altitude'] = {
        meta.labels.units: 'km',
        meta.labels.notes: 'Calculated using geospacepy.terrestrial_spherical',
        meta.labels.name: 'Altitude',
        meta.labels.desc: 'Altitude of satellite above an ellipsoidal Earth'}
    meta['geod_latitude'] = {
        meta.labels.units: 'degrees',
        meta.labels.notes: 'Calculated using geospacepy.terrestrial_ellipsoidal',
        meta.labels.name: 'Geodetic Latitude',
        meta.labels.desc: 'Geodetic Latitude of satellite',
        meta.labels.min_val: -90.,
        meta.labels.max_val: 90.}
    meta['geod_longitude'] = {
        meta.labels.units: 'degrees',
        meta.labels.notes: 'Calculated using geospacepy.terrestrial_ellipsoidal',
        meta.labels.name: 'Geodetic Longitude',
        meta.labels.desc: 'Geodetic Longitude of satellite',
        meta.labels.min_val: -180.,
        meta.labels.max_val: 180.}
    meta['geod_altitude'] = {
        meta.labels.units: 'km',
        meta.labels.notes: 'Calculated using geospacepy.terrestrial_ellipsoidal',
        meta.labels.name: 'Altitude',
        meta.labels.desc: 'Altitude of satellite above an ellipsoidal Earth'}

    return data, meta


list_files = functools.partial(ps_meth.list_files, test_dates=_test_dates)
download = functools.partial(ps_meth.download)
clean = functools.partial(mcore._clean)
