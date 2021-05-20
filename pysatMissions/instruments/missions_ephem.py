# -*- coding: utf-8 -*-
"""
Produces satellite orbit data. Orbit is simulated using
Two Line Elements (TLEs) and ephem. Satellite position is coupled
to several space science models to simulate the atmosphere the
satellite is in.

Properties
----------
platform
    'missions'
name
    'ephem'
tag
    None supported
inst_id
    None supported

"""

import datetime as dt
import functools
import numpy as np

import ephem
import OMMBV
import pandas as pds
import pysat

from pysat.instruments.methods import testing as ps_meth
from pysatMissions.instruments import _core as mcore
from pysatMissions.methods import magcoord as mm_magcoord
from pysatMissions.methods import spacecraft as mm_sc

logger = pysat.logger

# pysat required parameters
platform = 'missions'
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

    Adds custom routines for quasi-dipole coordinates, velocity calculation in
    ECEF coords, and attitude vectors of spacecraft (assuming x is ram pointing
    and z is generally nadir).

    """

    self.acknowledgements = ' '.join((
        'The project uses the pyephem library available at',
        'https://github.com/brandon-rhodes/pyephem'))
    self.references = 'Please contact the pyephem project for references'
    logger.info(self.acknowledgements)

    return


def preprocess(self):
    """
    Add modeled magnetic field values and attitude vectors to spacecraft

    Runs after load is invoked.

    """

    mm_magcoord.add_quasi_dipole_coordinates(self)
    mm_magcoord.add_aacgm_coordinates(self)
    mm_sc.calculate_ecef_velocity(self)
    mm_sc.add_ram_pointing_sc_attitude_vectors(self)

    return


# Clean method
clean = mcore._clean


def load(fnames, tag=None, inst_id=None, obs_long=0., obs_lat=0., obs_alt=0.,
         TLE1=None, TLE2=None, num_samples=None, cadence='1S'):
    """
    Returns data and metadata in the format required by pysat. Generates
    position of satellite in both geographic and ECEF co-ordinates.

    Routine is directly called by pysat and not the user.

    Parameters
    ----------
    fnames : list
        List of filenames
    tag : str or NoneType
        Identifies a particular subset of satellite data (accepts '')
        (default=None)
    inst_id : str or NoneType
        Instrument satellite ID (accepts '')
        (default=None)
    obs_long: float
        Longitude of the observer on the Earth's surface
        (default=0.)
    obs_lat: float
        Latitude of the observer on the Earth's surface
        (default=0.)
    obs_alt: float
        Altitude of the observer on the Earth's surface
        (default=0.)
    TLE1 : string or NoneType
        First string for Two Line Element. Must be in TLE format (default=None)
    TLE2 : string or NoneType
        Second string for Two Line Element. Must be in TLE format (default=None)
    num_samples : int or NoneType
        Number of samples per day (default=None)
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
          inst = pysat.Instrument('pysat', 'ephem', TLE1=TLE1, TLE2=TLE2)
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
    times, index, dates = ps_meth.generate_times(fnames, num_samples,
                                                 freq=cadence)

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
        lp['x'], lp['y'], lp['z'] = OMMBV.geodetic_to_ecef(lp['glat'],
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
                         index=index)
    data.index.name = 'Epoch'

    return data, meta.copy()


list_files = functools.partial(ps_meth.list_files, test_dates=_test_dates)
download = functools.partial(ps_meth.download)

# create metadata corresponding to variables in load routine just above
# made once here rather than regenerate every load call
meta = pysat.Meta()
meta['Epoch'] = {
    meta.labels.units: 'Milliseconds since 1970-1-1',
    meta.labels.notes: 'UTC time at middle of geophysical measurement.',
    meta.labels.desc: 'UTC seconds',
    meta.labels.name: 'Time index in milliseconds'}
meta['glong'] = {meta.labels.units: 'degrees',
                 meta.labels.desc: 'WGS84 geodetic longitude'}
meta['glat'] = {meta.labels.units: 'degrees',
                meta.labels.desc: 'WGS84 geodetic latitude'}
meta['alt'] = {meta.labels.units: 'km',
               meta.labels.desc: "WGS84 height above Earth's surface"}
meta['position_ecef_x'] = {meta.labels.units: 'km',
                           meta.labels.desc: 'ECEF x co-ordinate of satellite'}
meta['position_ecef_y'] = {meta.labels.units: 'km',
                           meta.labels.desc: 'ECEF y co-ordinate of satellite'}
meta['position_ecef_z'] = {meta.labels.units: 'km',
                           meta.labels.desc: 'ECEF z co-ordinate of satellite'}
meta['obs_sat_az_angle'] = {
    meta.labels.units: 'degrees',
    meta.labels.desc: 'Azimuth of satellite from ground station'}
meta['obs_sat_el_angle'] = {
    meta.labels.units: 'degrees',
    meta.labels.desc: 'Elevation of satellite from ground station'}
meta['obs_sat_slant_range'] = {
    meta.labels.units: 'km',
    meta.labels.desc: 'Distance of satellite from ground station'}