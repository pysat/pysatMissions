# -*- coding: utf-8 -*-
"""
Produces satellite orbit data. Orbit is simulated using
Two Line Elements (TLEs) and SGP4.

"""

from __future__ import print_function
from __future__ import absolute_import
import functools

import pysat

from pysatMissions.instruments import _core as mcore

# pysat required parameters
platform = 'pysat'
name = 'sgp4'
# dictionary of data 'tags' and corresponding description
tags = {'': 'Satellite simulation data set'}
# dictionary of satellite IDs, list of corresponding tags
sat_ids = {'': ['']}
_test_dates = {'': {'': pysat.datetime(2018, 1, 1)}}


def init(self):
    """
    Adds custom calculations to orbit simulation.
    This routine is run once, and only once, upon instantiation.

    """

    pass


def load(fnames, tag=None, sat_id=None, obs_long=0., obs_lat=0., obs_alt=0.,
         TLE1=None, TLE2=None):
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
    sat_id : string
        Instrument satellite ID (accepts '' or a number (i.e., '10'), which
        specifies the number of seconds to simulate the satellite)
        (default = '')
    obs_long: float
        Longitude of the observer on the Earth's surface
        (default = 0.)
    obs_lat: float
        Latitude of the observer on the Earth's surface
        (default = 0.)
    obs_alt: float
        Altitude of the observer on the Earth's surface
        (default = 0.)
    TLE1 : string
        First string for Two Line Element. Must be in TLE format
    TLE2 : string
        Second string for Two Line Element. Must be in TLE format

    Returns
    -------
    data : (pandas.DataFrame)
        Object containing satellite data
    meta : (pysat.Meta)
        Object containing metadata such as column names and units

    Example
    -------
      inst = pysat.Instrument('pysat', 'sgp4',
          TLE1='1 25544U 98067A   18135.61844383  .00002728  00000-0  48567-4 0  9998',
          TLE2='2 25544  51.6402 181.0633 0004018  88.8954  22.2246 15.54059185113452')
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

    # create satellite from TLEs and assuming a gravity model
    # according to module webpage, wgs72 is common
    satellite = twoline2rv(line1, line2, wgs72)

    # Extract list of times from filenames and sat_id
    times = mcore._get_times(fnames, sat_id)

    # create list to hold satellite position, velocity
    position = []
    velocity = []
    for timestep in times:
        # orbit propagator - computes x,y,z position and velocity
        pos, vel = satellite.propagate(timestep.year, timestep.month,
                                       timestep.day, timestep.hour,
                                       timestep.minute, timestep.second)
        position.extend(pos)
        velocity.extend(vel)

    # put data into DataFrame
    data = pysat.DataFrame({'position_eci_x': position[::3],
                            'position_eci_y': position[1::3],
                            'position_eci_z': position[2::3],
                            'velocity_eci_x': velocity[::3],
                            'velocity_eci_y': velocity[1::3],
                            'velocity_eci_z': velocity[2::3]},
                           index=times)
    data.index.name = 'Epoch'

    # TODO: add call for GEI/ECEF translation here

    return data, meta.copy()


list_files = functools.partial(mcore._list_files)
download = functools.partial(mcore._download)

# create metadata corresponding to variables in load routine just above
# made once here rather than regenerate every load call
meta = pysat.Meta()
meta['Epoch'] = {'units': 'Milliseconds since 1970-1-1',
                 'Bin_Location': 0.5,
                 'notes': 'UTC time at middle of geophysical measurement.',
                 'desc': 'UTC seconds',
                 'long_name': 'Time index in milliseconds'}
meta['position_eci_x'] = {'units': 'km',
                          'long_name': 'ECI x-position',
                          'desc': 'Earth Centered Inertial x-position of ' +
                          'satellite.',
                          'label': 'ECI-X'}
meta['position_eci_y'] = {'units': 'km',
                          'long_name': 'ECI y-position',
                          'desc': 'Earth Centered Inertial y-position of ' +
                          'satellite.',
                          'label': 'ECI-Y'}
meta['position_eci_z'] = {'units': 'km',
                          'long_name': 'ECI z-position',
                          'desc': 'Earth Centered Inertial z-position of ' +
                          'satellite.',
                          'label': 'ECI-Z'}
meta['velocity_eci_x'] = {'units': 'km/s',
                          'desc': 'Satellite velocity along ECI-x',
                          'long_name': 'Satellite velocity ECI-x'}
meta['velocity_eci_y'] = {'units': 'km/s',
                          'desc': 'Satellite velocity along ECI-y',
                          'long_name': 'Satellite velocity ECI-y'}
meta['velocity_eci_z'] = {'units': 'km/s',
                          'desc': 'Satellite velocity along ECI-z',
                          'long_name': 'Satellite velocity ECI-z'}
