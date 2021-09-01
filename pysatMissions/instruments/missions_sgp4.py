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

    return


# Clean method
clean = mcore._clean


def load(fnames, tag=None, inst_id=None,
         TLE1=None, TLE2=None, alt_periapsis=None, alt_apoapsis=None,
         inclination=None, raan=None, arg_periapsis=None, mean_anomaly=None,
         bstar=None, num_samples=None, cadence='1S'):
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

    if num_samples is None:
        num_samples = 100

    # Extract list of times from filenames and inst_id
    times, index, dates = ps_meth.generate_times(fnames, num_samples,
                                                 freq=cadence)
    # Calculate epoch for orbital propagator
    epoch = (dates[0] - dt.datetime(1949, 12, 31)).days
    jd, _ = sapi.jday(dates[0].year, dates[0].month, dates[0].day, 0, 0, 0)

    if inclination is not None:
        # If an inclination is provided, specify by Keplerian elements
        eccentricity, mean_motion = orbits.convert_to_keplerian(alt_periapsis,
                                                                alt_apoapsis)
        satellite = sapi.Satrec()
        # according to module webpage, wgs72 is common
        satellite.sgp4init(sapi.WGS72, 'i', 0, epoch, bstar, 0, 0,
                           eccentricity, np.radians(arg_periapsis),
                           np.radians(inclination), np.radians(mean_anomaly),
                           mean_motion, np.radians(raan))
    else:
        # Otherwise, use TLEs
        satellite = sapi.Satrec.twoline2rv(line1, line2, sapi.WGS72)

    jd = jd * np.ones(len(times))
    fr = times / 86400.

    err_code, position, velocity = satellite.sgp4_array(jd, fr)

    # Check all propagated values for errors in propagation
    errors = np.unique(err_code[err_code > 0])
    if len(errors) > 0:
        # Raise highest priority error.
        raise ValueError(sapi.SGP4_ERRORS[errors[0]])

    # Put data into DataFrame
    data = pds.DataFrame({'position_eci_x': position[:, 0],
                          'position_eci_y': position[:, 1],
                          'position_eci_z': position[:, 2],
                          'velocity_eci_x': velocity[:, 0],
                          'velocity_eci_y': velocity[:, 1],
                          'velocity_eci_z': velocity[:, 2]},
                         index=index)
    data.index.name = 'Epoch'

    # Create metadata corresponding to variables in load routine
    meta = pysat.Meta()
    meta['Epoch'] = {
        meta.labels.units: 'Milliseconds since 1970-1-1',
        meta.labels.notes: 'UTC time at middle of geophysical measurement.',
        meta.labels.desc: 'UTC seconds',
        meta.labels.name: 'Time index in milliseconds'}
    meta['position_eci_x'] = {
        meta.labels.units: 'km',
        meta.labels.name: 'ECI x-position',
        meta.labels.desc: 'Earth Centered Inertial x-position of satellite.'}
    meta['position_eci_y'] = {
        meta.labels.units: 'km',
        meta.labels.name: 'ECI y-position',
        meta.labels.desc: 'Earth Centered Inertial y-position of satellite.'}
    meta['position_eci_z'] = {
        meta.labels.units: 'km',
        meta.labels.name: 'ECI z-position',
        meta.labels.desc: 'Earth Centered Inertial z-position of satellite.'}
    meta['velocity_eci_x'] = {
        meta.labels.units: 'km/s',
        meta.labels.desc: 'Satellite velocity along ECI-x',
        meta.labels.name: 'Satellite velocity ECI-x'}
    meta['velocity_eci_y'] = {
        meta.labels.units: 'km/s',
        meta.labels.desc: 'Satellite velocity along ECI-y',
        meta.labels.name: 'Satellite velocity ECI-y'}
    meta['velocity_eci_z'] = {
        meta.labels.units: 'km/s',
        meta.labels.desc: 'Satellite velocity along ECI-z',
        meta.labels.name: 'Satellite velocity ECI-z'}

    # TODO(#56): add call for GEI/ECEF translation here

    return data, meta


list_files = functools.partial(ps_meth.list_files, test_dates=_test_dates)
download = functools.partial(ps_meth.download)
clean = functools.partial(mcore._clean)
