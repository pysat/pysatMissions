# -*- coding: utf-8 -*-
"""
Produces satellite orbit data. Orbit is simulated using
Two Line Elements (TLEs) and SGP4.

"""

from __future__ import print_function
from __future__ import absolute_import

import os
import functools
import pandas as pds
import pysat
from pysatMissionPlanning.instruments import _core as meth

# pysat required parameters
platform = 'pysat'
name = 'sgp4'
# dictionary of data 'tags' and corresponding description
tags = {'': 'Satellite simulation data set'}
# dictionary of satellite IDs, list of corresponding tags
sat_ids = {'': ['']}
test_dates = {'': {'': pysat.datetime(2018, 1, 1)}}


def init(self):
    """
    Adds custom calculations to orbit simulation.
    This routine is run once, and only once, upon instantiation.

    """


def load(fnames, tag=None, sat_id=None, obs_long=0., obs_lat=0., obs_alt=0.,
         TLE1=None, TLE2=None):
    """
    Returns data and metadata in the format required by pysat. Finds position
    of satellite in ECI co-ordinates.

    Routine is directly called by pysat and not the user.

    Parameters
    ----------
    fnames : list-like collection
        File name that contains date in its name.
    tag : string
        Identifies a particular subset of satellite data
    sat_id : string
        Satellite ID
    obs_long: float
        Longitude of the observer on the Earth's surface
    obs_lat: float
        Latitude of the observer on the Earth's surface
    obs_alt: float
        Altitude of the observer on the Earth's surface
    TLE1 : string
        First string for Two Line Element. Must be in TLE format
    TLE2 : string
        Second string for Two Line Element. Must be in TLE format

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

    # grab date from filename
    parts = os.path.split(fnames[0])[-1].split('-')
    yr = int(parts[0])
    month = int(parts[1])
    day = int(parts[2][0:2])
    date = pysat.datetime(yr, month, day)

    # create timing at 1 Hz (for 1 day)
    times = pds.date_range(start=date, end=date+pds.DateOffset(seconds=86399),
                           freq='1S')
    # reduce requirements if on testing server
    # TODO Remove this when testing resources are higher
    on_travis = os.environ.get('ONTRAVIS') == 'True'
    if on_travis:
        times = times[0:100]

    # create list to hold satellite position, velocity
    position = []
    velocity = []
    for time in times:
        # orbit propagator - computes x,y,z position and velocity
        pos, vel = satellite.propagate(time.year, time.month, time.day,
                                       time.hour, time.minute, time.second)
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


list_files = functools.partial(meth._list_files)
download = functools.partial(meth._download)

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
