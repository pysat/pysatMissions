# -*- coding: utf-8 -*-
"""Produce satellite orbit data.

.. deprecated:: 0.3.0
    pyephem is no longer updated, and the code maintainers suggest skyfield
    as a replacement.  The functionality of the instrument will be replaced by
    the new `missions_sgp4` instrument.  `missions_ephem` will be removed in
    versions 0.4.0+

Orbit is simulated using Two Line Elements (TLEs) and ephem. Satellite position
is coupled to several space science models to simulate the atmosphere the
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
import warnings

import ephem
import OMMBV
import pandas as pds
import pysat

from pysat.instruments.methods import testing as ps_meth
from pysatMissions.instruments import _core as mcore
from pysatMissions.methods import magcoord as mm_magcoord
from pysatMissions.methods import spacecraft as mm_sc

logger = pysat.logger

# -------------------------------
# Required Instrument attributes
platform = 'missions'
name = 'ephem'
tags = {'': 'Satellite simulation data set'}
inst_ids = {'': ['']}

# ------------------
# Testing attributes
_test_dates = {'': {'': dt.datetime(2018, 1, 1)}}


def init(self):
    """Add custom calculations to orbit simulation.

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

    warnings.warn(' '.join(("`missions_ephem` has been deprecated and will be",
                            "removed in pysatMissions 0.4.0+.",
                            "Use `missions_sgp4` instead.")),
                  DeprecationWarning, stacklevel=2)

    return


def preprocess(self):
    """Add modeled magnetic field values and attitude vectors to spacecraft.

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
         tle1=None, tle2=None, num_samples=None, cadence='1S'):
    """Generate position of satellite in both geographic and ECEF co-ordinates.

    Note
    ----
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
    tle1 : string or NoneType
        First string for Two Line Element. Must be in TLE format (default=None)
    tle2 : string or NoneType
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

          tle1='1 25544U 98067A   18135.61844383  .00002728  00000-0  48567-4 0  9998'
          tle2='2 25544  51.6402 181.0633 0004018  88.8954  22.2246 15.54059185113452'
          inst = pysat.Instrument('pysat', 'ephem', tle1=tle1, tle2=tle2)
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

    # Use ISS defaults if not provided by user
    if tle1 is not None:
        line1 = tle1
    if tle2 is not None:
        line2 = tle2

    if num_samples is None:
        num_samples = 100

    # Extract list of times from filenames and inst_id
    times, index, dates = ps_meth.generate_times(fnames, num_samples,
                                                 freq=cadence)

    # The observer's (ground station) position on the Earth surface
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

        # Parameters relative to the ground station
        lp['obs_sat_az_angle'] = ephem.degrees(sat.az)
        lp['obs_sat_el_angle'] = ephem.degrees(sat.alt)

        # Total distance between transmitter and receiver
        lp['obs_sat_slant_range'] = sat.range

        # Satellite location (sub-latitude and sub-longitude)
        lp['glat'] = np.degrees(sat.sublat)
        lp['glong'] = np.degrees(sat.sublong)

        # Elevation of satellite in m, converted to km
        lp['alt'] = sat.elevation / 1000.0

        # Get ECEF position of satellite
        lp['x'], lp['y'], lp['z'] = OMMBV.trans.geodetic_to_ecef(lp['glat'],
                                                                 lp['glong'],
                                                                 lp['alt'])
        output_params.append(lp)

    output = pds.DataFrame(output_params, index=index)
    # Modify input object to include calculated parameters
    # Put data into DataFrame
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

    meta = pysat.Meta()
    meta['Epoch'] = {
        meta.labels.units: 'Milliseconds since 1970-1-1',
        meta.labels.notes: 'UTC time at middle of geophysical measurement.',
        meta.labels.desc: 'UTC seconds',
        meta.labels.name: 'Time index in milliseconds'}
    meta['glong'] = {meta.labels.units: 'degrees',
                     meta.labels.desc: 'WGS84 geodetic longitude',
                     meta.labels.min_val: -180.0,
                     meta.labels.max_val: 180.0,
                     meta.labels.fill_val: np.nan}
    meta['glat'] = {meta.labels.units: 'degrees',
                    meta.labels.desc: 'WGS84 geodetic latitude',
                    meta.labels.min_val: -90.0,
                    meta.labels.max_val: 90.0,
                    meta.labels.fill_val: np.nan}
    meta['alt'] = {meta.labels.units: 'km',
                   meta.labels.desc: "WGS84 height above Earth's surface",
                   meta.labels.min_val: 0.0,
                   meta.labels.max_val: np.inf,
                   meta.labels.fill_val: np.nan}
    for v in ['x', 'y', 'z']:
        meta['position_ecef_{:}'.format(v)] = {
            meta.labels.units: 'km',
            meta.labels.name: 'ECEF {:}-position'.format(v),
            meta.labels.desc: 'Earth Centered Earth Fixed {:}-position'.format(v),
            meta.labels.min_val: -np.inf,
            meta.labels.max_val: np.inf,
            meta.labels.fill_val: np.nan}
    meta['obs_sat_az_angle'] = {
        meta.labels.units: 'degrees',
        meta.labels.name: 'Satellite Azimuth Angle',
        meta.labels.desc: 'Azimuth of satellite from ground station',
        meta.labels.min_val: -np.inf,
        meta.labels.max_val: np.inf,
        meta.labels.fill_val: np.nan}
    meta['obs_sat_el_angle'] = {
        meta.labels.units: 'degrees',
        meta.labels.name: 'Satellite Elevation Angle',
        meta.labels.desc: 'Elevation of satellite from ground station',
        meta.labels.min_val: -np.inf,
        meta.labels.max_val: np.inf,
        meta.labels.fill_val: np.nan}
    meta['obs_sat_slant_range'] = {
        meta.labels.units: 'km',
        meta.labels.name: 'Satellite Slant Distance',
        meta.labels.desc: 'Distance of satellite from ground station',
        meta.labels.min_val: -np.inf,
        meta.labels.max_val: np.inf,
        meta.labels.fill_val: np.nan}

    return data, meta


list_files = functools.partial(ps_meth.list_files, test_dates=_test_dates)
download = functools.partial(ps_meth.download)
