# -*- coding: utf-8 -*-
"""
Produces satellite orbit data. Orbit is simulated using
Two Line Elements (TLEs) and ephem. Satellite position is coupled
to several space science models to simulate the atmosphere the
satellite is in.

"""

import datetime as dt
import functools
import numpy as np

import ephem
import pysatMagVect
import pandas as pds
import pysat

from pysat.instruments.methods import testing as ps_meth
from pysatMissions.instruments import _core as mcore
from pysatMissions.methods import magcoord as mm_magcoord
from pysatMissions.methods import spacecraft as mm_sc

# pysat required parameters
platform = 'pysat'
name = 'ephem'
# dictionary of data 'tags' and corresponding description
tags = {'': 'Satellite simulation data set'}
# dictionary of satellite IDs, list of corresponding tags
inst_ids = {'': ['']}
_test_dates = {'': {'': dt.datetime(2018, 1, 1)}}


def init(self):
    """
    Adds custom calculations to orbit simulation.
    This routine is run once, and only once, upon instantiation.

    Adds quasi-dipole coordiantes, velocity calculation in ECEF coords,
    adds the attitude vectors of spacecraft assuming x is ram pointing and
    z is generally nadir, adds ionospheric parameters from the Interational
    Reference Ionosphere (IRI), as well as simulated winds from the
    Horiontal Wind Model (HWM).

    """

    self.custom.attach(mm_magcoord.add_quasi_dipole_coordinates)
    self.custom.attach(mm_magcoord.add_aacgm_coordinates)
    self.custom.attach(mm_sc.calculate_ecef_velocity)
    self.custom.attach(mm_sc.add_ram_pointing_sc_attitude_vectors)


def load(fnames, tag=None, inst_id=None, obs_long=0., obs_lat=0., obs_alt=0.,
         TLE1=None, TLE2=None, num_samples=None, freq='1S'):
    """
    Returns data and metadata in the format required by pysat. Generates
    position of satellite in both geographic and ECEF co-ordinates.

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
    num_samples : int
        Number of samples per day
    freq : str
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
      inst = pysat.Instrument('pysat', 'sgp4',
          TLE1='1 25544U 98067A   18135.61844383  .00002728  00000-0  48567-4 0  9998',
          TLE2='2 25544  51.6402 181.0633 0004018  88.8954  22.2246 15.54059185113452')
      inst.load(2018, 1)

    """

    # TLEs (Two Line Elements for ISS)
    # format of TLEs is fixed and available from wikipedia...
    # lines encode list of orbital elements of an Earth-orbiting object
    # for a given point in time
    line1 = ''.join(('1 25544U 98067A   18135.61844383  .00002728  00000-0  ',
                     '48567-4 0  9998'))
    line2 = ''.join(('2 25544  51.6402 181.0633 0004018  88.8954  22.2246 ',
                     '15.54059185113452'))
    # use ISS defaults if not provided by user
    if TLE1 is not None:
        line1 = TLE1
    if TLE2 is not None:
        line2 = TLE2

    if num_samples is None:
        num_samples = 100

    # Extract list of times from filenames and inst_id
    times, index, dates = ps_meth.generate_times(fnames, num_samples, freq=freq)

    # the observer's (ground station) position on the Earth surface
    site = ephem.Observer()
    site.lon = str(obs_long)
    site.lat = str(obs_lat)
    site.elevation = obs_alt

    # The first parameter in readtle() is the satellite name
    sat = ephem.readtle('pysat', line1, line2)
    output_params = []
    for timestep in index:
        lp = {}
        site.date = timestep
        sat.compute(site)
        # parameters relative to the ground station
        lp['obs_sat_az_angle'] = ephem.degrees(sat.az)
        lp['obs_sat_el_angle'] = ephem.degrees(sat.alt)
        # total distance away
        lp['obs_sat_slant_range'] = sat.range
        # satellite location
        # sub latitude point
        lp['glat'] = np.degrees(sat.sublat)
        # sublongitude point
        lp['glong'] = np.degrees(sat.sublong)
        # elevation of sat in m, stored as km
        lp['alt'] = sat.elevation / 1000.
        # get ECEF position of satellite
        lp['x'], lp['y'], lp['z'] = pysatMagVect.geodetic_to_ecef(lp['glat'],
                                                                  lp['glong'],
                                                                  lp['alt'])
        output_params.append(lp)

    output = pds.DataFrame(output_params, index=index)
    # modify input object to include calculated parameters
    # put data into DataFrame
    data = pds.DataFrame({'glong': output['glong'],
                          'glat': output['glat'],
                          'alt': output['alt'],
                          'position_ecef_x': output['x'],
                          'position_ecef_y': output['y'],
                          'position_ecef_z': output['z'],
                          'obs_sat_az_angle': output['obs_sat_az_angle'],
                          'obs_sat_el_angle': output['obs_sat_el_angle'],
                          'obs_sat_slant_range':
                          output['obs_sat_slant_range']},
                         index=times)
    data.index.name = 'Epoch'

    return data, meta.copy()


def clean(self):
    """Cleaning function
    """

    pass


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
meta['glong'] = {'units': 'degrees',
                 'long_name': 'Geodetic longitude',
                 'desc': 'WGS84 geodetic longitude'}
meta['glat'] = {'units': 'degrees',
                'long_name': 'Geodetic latitude',
                'desc': 'WGS84 geodetic latitude'}
meta['alt'] = {'units': 'km',
               'long_name': 'Geodetic height',
               'desc': "WGS84 height above Earth's surface"}
meta['position_ecef_x'] = {'units': 'km',
                           'desc': 'ECEF x co-ordinate of satellite'}
meta['position_ecef_y'] = {'units': 'km',
                           'desc': 'ECEF y co-ordinate of satellite'}
meta['position_ecef_z'] = {'units': 'km',
                           'desc': 'ECEF z co-ordinate of satellite'}
meta['obs_sat_az_angle'] = {'units': 'degrees',
                            'desc': 'Azimuth of satellite from ground station'}
meta['obs_sat_el_angle'] = {'units': 'degrees',
                            'desc': ' '.join(('Elevation of satellite from',
                                              'ground station'))}
meta['obs_sat_slant_range'] = {'units': 'km',
                               'desc': ' '.join(('Distance of satellite from',
                                                 'ground station'))}
