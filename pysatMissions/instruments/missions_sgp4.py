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

from geospacepy import terrestrial_ellipsoidal as conv_ell
from geospacepy import terrestrial_spherical as conv_sph
from sgp4 import api as sapi

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

    if 'epoch' not in self.kwargs['load'].keys():
        self.kwargs['load']['epoch'] = self.files.files.index[0]

    return


# Clean method
clean = mcore._clean


def load(fnames, tag=None, inst_id=None, tle1=None, tle2=None,
         alt_periapsis=None, alt_apoapsis=None,
         inclination=None, raan=0., arg_periapsis=0., mean_anomaly=0.,
         epoch=None, bstar=0., one_orbit=False, num_samples=None, cadence='1S'):
    """Generate position of satellite in ECI co-ordinates.

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
    tle1 : str or NoneType
        First string for Two Line Element. Must be in TLE format.  tle1 and tle2
        both required if instantiating instrument by TLEs. (defalt=None)
    tle2 : str or NoneType
        Second string for Two Line Element. Must be in TLE format.  tle1 and tle2
        both required if instantiating instrument by TLEs. (default=None)
    alt_periapsis : float or NoneType
        The lowest altitude from the mean planet surface along the orbit (km).
        Required along with inclination if instantiating via orbital elements.
        (default=None)
    alt_apoapsis : float or NoneType
        The highest altitude from the mean planet surface along the orbit (km)
        If None, assumed to be equal to periapsis (ie, circular orbit). Optional
        when instantiating via orbital elements. (default=None)
    inclination : float or NoneType
        Orbital Inclination in degrees.  Required along with alt_periapsis if
        instantiating via orbital elements. (default=None)
    raan : float
        Right Ascension of the Ascending Node (RAAN) in degrees. This defines
        the orientation of the orbital plane to the generalized reference frame.
        The Ascending Node is the point in the orbit where the spacecraft passes
        through the plane of reference moving northward.  For Earth orbits, the
        location of the RAAN is defined as the angle eastward of the First Point
        of Aries. Optional when instantiating via orbital elements.
        (default=0.)
    arg_periapsis : float
        Argument of Periapsis in degrees.  This defines the orientation of the
        ellipse in the orbital plane, as an angle measured from the ascending
        node to the periapsis.  Optional when instantiating via orbital elements.
        (default=0.)
    mean_anomaly : float
        The fraction of an elliptical orbit's period that has elapsed since the
        orbiting body passed periapsis.  Note that this is a "fictitious angle"
        (input in degrees) which defines the location of the spacecraft in the
        orbital plane based on the orbital period.  Optional when instantiating
        via orbital elements.
        (default=0.)
    epoch : dt.datetime or NoneType
        The epoch used for calculating orbital propagation from Keplerians.
        If None, then use the first date in the file list for consistency across
        multiple days. Note that this will be set in `init`. (default=None)
    bstar : float
        Inverse of the ballistic coefficient. Used to model satellite drag.
        Measured in inverse distance (1 / earth radius).  Optional when
        instantiating via orbital elements. (default=0.)
    one_orbit : bool
        Flag to override num_samples and only provide a single orbit.
        (default=False)
    num_samples : int
        Number of samples per day.  (default=None)
    cadence : str
        Uses pandas.frequency string formatting ('1S', etc)
        (default='1S')

    Returns
    -------
    data : pandas.DataFrame
        Object containing satellite data
    meta : pysat.Meta
        Object containing metadata such as column names and units

    Note
    ----
    * Routine is directly called by pysat and not the user.
    * Altitude accuracy expected to be on the order of 10 km in Low Earth Orbit.
      Efforts to improve accuracy documented under issue #79.


    Example
    -------
    ::

          tle1='1 25544U 98067A   18135.61844383  .00002728  00000-0  48567-4 0  9998'
          tle2='2 25544  51.6402 181.0633 0004018  88.8954  22.2246 15.54059185113452'
          inst = pysat.Instrument('pysat', 'sgp4', tle1=tle1, tle2=tle2)
          inst.load(2018, 1)

    """

    # TLEs (Two Line Elements for ISS)
    # format of TLEs is fixed and available from wikipedia...
    # lines encode list of orbital elements of an Earth-orbiting object
    # for a given point in time
    line1 = '1 25544U 98067A   18135.61844383  .00002728  00000-0  48567-4 0  9998'
    line2 = '2 25544  51.6402 181.0633 0004018  88.8954  22.2246 15.54059185113452'

    # If provided, use user-specified TLEs.  Otherwise use ISS defaults above.
    if tle1 is not None:
        line1 = tle1
    if tle2 is not None:
        line2 = tle2

    if (num_samples is None) or one_orbit:
        num_samples = 86400

    # Extract list of times from filenames and inst_id
    times, index, dates = ps_meth.generate_times(fnames, num_samples,
                                                 freq=cadence)
    # Calculate epoch for orbital propagator
    epoch_days = (epoch - dt.datetime(1949, 12, 31)).days
    jd, _ = sapi.jday(dates[0].year, dates[0].month, dates[0].day, 0, 0, 0)

    if inclination is not None:
        # If an inclination is provided, specify by Keplerian elements
        eccentricity, mean_motion = orbits.convert_to_keplerian(alt_periapsis,
                                                                alt_apoapsis)
        satellite = sapi.Satrec()
        # According to module webpage, wgs72 is common
        satellite.sgp4init(sapi.WGS72, 'i', 0, epoch_days, bstar, 0, 0,
                           eccentricity, np.radians(arg_periapsis),
                           np.radians(inclination), np.radians(mean_anomaly),
                           mean_motion, np.radians(raan))
    else:
        # Otherwise, use TLEs
        satellite = sapi.Satrec.twoline2rv(line1, line2, sapi.WGS72)
        mean_motion = satellite.mm

    if one_orbit:
        ind = times <= (2 * np.pi / mean_motion * 60)
        times = times[ind]
        index = index[ind]

    jd = jd * np.ones(len(times))
    fr = times / 86400.

    err_code, position, velocity = satellite.sgp4_array(jd, fr)

    # Check all propagated values for errors in propagation
    errors = np.unique(err_code[err_code > 0])
    if len(errors) > 0:
        # Raise highest priority error.
        raise ValueError(sapi.SGP4_ERRORS[errors[0]])

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
                          'geod_altitude': geod_alt / 1000.},  # Convert to km
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
            meta.labels.desc: 'Earth Centered Inertial {:}-position'.format(v),
            meta.labels.min_val: -np.inf,
            meta.labels.max_val: np.inf,
            meta.labels.fill_val: np.nan}
        meta['velocity_eci_{:}'.format(v)] = {
            meta.labels.units: 'km/s',
            meta.labels.name: 'Satellite velocity ECI-{:}'.format(v),
            meta.labels.desc: 'Satellite velocity along ECI-{:}'.format(v),
            meta.labels.min_val: -np.inf,
            meta.labels.max_val: np.inf,
            meta.labels.fill_val: np.nan}
        meta['position_ecef_{:}'.format(v)] = {
            meta.labels.units: 'km',
            meta.labels.notes: 'Calculated using geospacepy.terrestrial_spherical',
            meta.labels.name: 'ECEF {:}-position'.format(v),
            meta.labels.desc: 'Earth Centered Earth Fixed {:}-position'.format(v),
            meta.labels.min_val: -np.inf,
            meta.labels.max_val: np.inf,
            meta.labels.fill_val: np.nan}
        meta['velocity_ecef_{:}'.format(v)] = {
            meta.labels.units: 'km',
            meta.labels.notes: 'Calculated using geospacepy.terrestrial_spherical',
            meta.labels.name: 'ECEF {:}-velocity'.format(v),
            meta.labels.desc: 'Earth Centered Earth Fixed {:}-velocity'.format(v),
            meta.labels.min_val: -np.inf,
            meta.labels.max_val: np.inf,
            meta.labels.fill_val: np.nan}
    meta['latitude'] = {
        meta.labels.units: 'degrees',
        meta.labels.notes: 'Calculated using geospacepy.terrestrial_spherical',
        meta.labels.name: 'Geocentric Latitude',
        meta.labels.desc: 'Geocentric Latitude of satellite',
        meta.labels.min_val: -90.,
        meta.labels.max_val: 90.,
        meta.labels.fill_val: np.nan}
    meta['longitude'] = {
        meta.labels.units: 'degrees',
        meta.labels.notes: 'Calculated using geospacepy.terrestrial_spherical',
        meta.labels.name: 'Geocentric Longitude',
        meta.labels.desc: 'Geocentric Longitude of satellite',
        meta.labels.min_val: -180.,
        meta.labels.max_val: 180.,
        meta.labels.fill_val: np.nan}
    meta['mean_altitude'] = {
        meta.labels.units: 'km',
        meta.labels.notes: 'Calculated using geospacepy.terrestrial_spherical',
        meta.labels.name: 'Altitude',
        meta.labels.desc: 'Altitude of satellite above an ellipsoidal Earth',
        meta.labels.min_val: 0,
        meta.labels.max_val: np.inf,
        meta.labels.fill_val: np.nan}
    meta['geod_latitude'] = {
        meta.labels.units: 'degrees',
        meta.labels.notes: 'Calculated using geospacepy.terrestrial_ellipsoidal',
        meta.labels.name: 'Geodetic Latitude',
        meta.labels.desc: 'Geodetic Latitude of satellite',
        meta.labels.min_val: -90.,
        meta.labels.max_val: 90.,
        meta.labels.fill_val: np.nan}
    meta['geod_longitude'] = {
        meta.labels.units: 'degrees',
        meta.labels.notes: 'Calculated using geospacepy.terrestrial_ellipsoidal',
        meta.labels.name: 'Geodetic Longitude',
        meta.labels.desc: 'Geodetic Longitude of satellite',
        meta.labels.min_val: -180.,
        meta.labels.max_val: 180.,
        meta.labels.fill_val: np.nan}
    meta['geod_altitude'] = {
        meta.labels.units: 'km',
        meta.labels.notes: 'Calculated using geospacepy.terrestrial_ellipsoidal',
        meta.labels.name: 'Altitude',
        meta.labels.desc: 'Altitude of satellite above an ellipsoidal Earth',
        meta.labels.min_val: -np.inf,
        meta.labels.max_val: np.inf,
        meta.labels.fill_val: np.nan}

    return data, meta


list_files = functools.partial(ps_meth.list_files, test_dates=_test_dates)
download = functools.partial(ps_meth.download)
clean = functools.partial(mcore._clean)
