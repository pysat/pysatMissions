# -*- coding: utf-8 -*-
"""
Produces satellite orbit data. Orbit is simulated using
Two Line Elements (TLEs) and SGP4.

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
import pandas as pds

import pysat
from pysat.instruments.methods import testing as ps_meth
from pysatMissions.instruments import _core as mcore

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
    """
    Initializes the Instrument object with required values.

    Runs once upon instantiation.

    """

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


def load(fnames, tag=None, inst_id=None, obs_long=0., obs_lat=0., obs_alt=0.,
         TLE1=None, TLE2=None, num_samples=None, cadence='1S'):
    """
    Returns data and metadata in the format required by pysat. Generates
    position of satellite in ECI co-ordinates.

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
    obs_long: float
        Longitude of the observer on the Earth's surface
        (default=0.)
    obs_lat: float
        Latitude of the observer on the Earth's surface
        (default=0.)
    obs_alt: float
        Altitude of the observer on the Earth's surface
        (default=0.)
    TLE1 : string
        First string for Two Line Element. Must be in TLE format
    TLE2 : string
        Second string for Two Line Element. Must be in TLE format
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

    # wgs72 is the most commonly used gravity model in satellite tracking
    # community
    from sgp4.earth_gravity import wgs72
    from sgp4.io import twoline2rv

    # TLEs (Two Line Elements for ISS)
    # format of TLEs is fixed and available from wikipedia...
    # lines encode list of orbital elements of an Earth-orbiting object
    # for a given point in time
    line1 = ('1 25544U 98067A   18135.61844383  .00002728  00000-0  48567-4 0  9998')
    line2 = ('2 25544  51.6402 181.0633 0004018  88.8954  22.2246 15.54059185113452')
    # use ISS defaults if not provided by user
    if TLE1 is not None:
        line1 = TLE1
    if TLE2 is not None:
        line2 = TLE2

    if num_samples is None:
        num_samples = 100

    # Create satellite from TLEs and assuming a gravity model;
    # according to module webpage, wgs72 is common
    satellite = twoline2rv(line1, line2, wgs72)

    # Extract list of times from filenames and inst_id
    times, index, dates = ps_meth.generate_times(fnames, num_samples,
                                                 freq=cadence)

    # Create list to hold satellite position, velocity
    position = []
    velocity = []
    for timestep in index:
        # orbit propagator - computes x,y,z position and velocity
        pos, vel = satellite.propagate(timestep.year, timestep.month,
                                       timestep.day, timestep.hour,
                                       timestep.minute, timestep.second)
        position.extend(pos)
        velocity.extend(vel)

    # Put data into DataFrame
    data = pds.DataFrame({'position_eci_x': position[::3],
                          'position_eci_y': position[1::3],
                          'position_eci_z': position[2::3],
                          'velocity_eci_x': velocity[::3],
                          'velocity_eci_y': velocity[1::3],
                          'velocity_eci_z': velocity[2::3]},
                         index=index)
    data.index.name = 'Epoch'

    # TODO: add call for GEI/ECEF translation here => #56

    return data, meta.copy()


list_files = functools.partial(ps_meth.list_files, test_dates=_test_dates)
download = functools.partial(ps_meth.download)
clean = functools.partial(mcore._clean)

# Create metadata corresponding to variables in load routine just above
# made once here rather than regenerate every load call
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
