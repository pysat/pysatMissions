# -*- coding: utf-8 -*-
"""
Produces satellite orbit data. Orbit is simulated using
Two Line Elements (TLEs) and ephem. Satellite position is coupled
to several space science models to simulate the atmosphere the
satellite is in.

"""

from __future__ import print_function
from __future__ import absolute_import

import os
import functools
import numpy as np
import pandas as pds
import pysat
import pysatMissionPlanning.instruments._core as meth

# pysat required parameters
platform = 'pysat'
name = 'ephem'
# dictionary of data 'tags' and corresponding description
tags = {'': 'Satellite simulation data set'}
# dictionary of satellite IDs, list of corresponding tags
sat_ids = {'': ['']}
test_dates = {'': {'': pysat.datetime(2018, 1, 1)}}


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
    import pysatMissionPlanning.methods.aacgmv2 as methaacgm
    import pysatMissionPlanning.methods.apexpy as methapex
    import pysatMissionPlanning.methods.pyglow as methglow
    import pysatMissionPlanning.methods.spacecraft as methsc

    self.custom.add(methapex.add_quasi_dipole_coordinates, 'modify')
    self.custom.add(methaacgm.add_aacgm_coordinates, 'modify')
    self.custom.add(methsc.calculate_ecef_velocity, 'modify')
    self.custom.add(methsc.add_sc_attitude_vectors, 'modify')
    # project simulated vectors onto s/c basis
    # IGRF
    self.custom.add(methglow.add_igrf, 'modify')
    # create metadata to be added along with vector projection
    in_meta = {'desc': 'IGRF geomagnetic field expressed in the s/c basis.',
               'units': 'nT'}
    # project IGRF
    self.custom.add(methsc.project_ecef_vector_onto_sc, 'modify', 'end',
                    'B_ecef_x', 'B_ecef_y', 'B_ecef_z', 'B_sc_x', 'B_sc_y',
                    'B_sc_z', meta=[in_meta.copy(), in_meta.copy(),
                                    in_meta.copy()])
    # Thermal Ion Parameters
    self.custom.add(methglow.add_iri_thermal_plasma, 'modify')
    # Thermal Neutral parameters
    self.custom.add(methglow.add_msis, 'modify')
    self.custom.add(methglow.add_hwm_winds_and_ecef_vectors, 'modify')
    # project total wind vector
    self.custom.add(methglow.project_hwm_onto_sc, 'modify')


def load(fnames, tag=None, sat_id=None, obs_long=0., obs_lat=0., obs_alt=0.,
         TLE1=None, TLE2=None):
    """
    Returns data and metadata in the format required by pysat. Finds position
    of satellite in both geographic and ECEF co-ordinates.

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

    import ephem
    import pysatMagVect

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

    # the observer's (ground station) position on the Earth surface
    site = ephem.Observer()
    site.lon = str(obs_long)
    site.lat = str(obs_lat)
    site.elevation = obs_alt

    # The first parameter in readtle() is the satellite name
    sat = ephem.readtle('pysat', line1, line2)
    output_params = []
    for time in times:
        lp = {}
        site.date = time
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
        lp['alt'] = sat.elevation/1000.
        # get ECEF position of satellite
        lp['x'], lp['y'], lp['z'] = pysatMagVect.geodetic_to_ecef(lp['glat'],
                                                                  lp['glong'],
                                                                  lp['alt'])
        output_params.append(lp)

    output = pds.DataFrame(output_params, index=times)
    # modify input object to include calculated parameters
    # put data into DataFrame
    data = pysat.DataFrame({'glong': output['glong'],
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


list_files = functools.partial(meth.list_files)
download = functools.partial(meth.download)

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
                            'desc': 'Elevation of satellite from ground ' +
                            'station'}
meta['obs_sat_slant_range'] = {'units': 'km',
                               'desc': 'Distance of satellite from ground ' +
                               'station'}
