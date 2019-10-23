# -*- coding: utf-8 -*-
"""
Produces satellite orbit data. Orbit is simulated using
Two Line Elements (TLEs) and SGP4. Satellite position is coupled
to several space science models to simulate the atmosphere the
satellite is in.

"""

from __future__ import print_function
from __future__ import absolute_import

# basestring abstract type is removed in Python 3 and is replaced by str
# python 2/3 compatibility
try:
    basestring
except NameError:
    basestring = str
import os

import pandas as pds
import numpy as np
import pysat

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

    Adds quasi-dipole coordiantes, velocity calculation in ECEF coords,
    adds the attitude vectors of spacecraft assuming x is ram pointing and
    z is generally nadir, adds ionospheric parameters from the Interational
    Reference Ionosphere (IRI), as well as simulated winds from the
    Horiontal Wind Model (HWM).

    """
    import pysatMissionPlanning.methods.aacgmv2 as methaacgm
    import pysatMissionPlanning.methods.apexpy as methapex
    import pysatMissionPlanning.methods.pyglow as methglow

    self.custom.add(methapex.add_quasi_dipole_coordinates, 'modify')
    self.custom.add(methaacgm.add_aacgm_coordinates, 'modify')
    self.custom.add(calculate_ecef_velocity, 'modify')
    self.custom.add(add_sc_attitude_vectors, 'modify')
    # Thermal Ion Parameters
    self.custom.add(methglow.add_iri_thermal_plasma, 'modify')
    # Thermal Neutral parameters
    self.custom.add(methglow.add_msis, 'modify')
    self.custom.add(methglow.add_hwm_winds_and_ecef_vectors, 'modify')
    # project simulated vectors onto s/c basis
    # IGRF
    self.custom.add(methglow.add_igrf, 'modify')
    # create metadata to be added along with vector projection
    in_meta = {'desc': 'IGRF geomagnetic field expressed in the s/c basis.',
               'units': 'nT'}
    # project IGRF
    self.custom.add(project_ecef_vector_onto_sc, 'modify', 'end', 'B_ecef_x',
                    'B_ecef_y', 'B_ecef_z', 'B_sc_x', 'B_sc_y', 'B_sc_z',
                    meta=[in_meta.copy(), in_meta.copy(), in_meta.copy()])
    # project total wind vector
    self.custom.add(project_hwm_onto_sc, 'modify')


def load(fnames, tag=None, sat_id=None, obs_long=0., obs_lat=0., obs_alt=0.,
         TLE1=None, TLE2=None):
    """
    Returns data and metadata in the format required by pysat. Finds position
    of satellite in both ECI and ECEF co-ordinates.

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

    # add position and velocity in ECEF
    # add call for GEI/ECEF translation here
    # instead, since available, I'll use an orbit predictor from another
    # package that outputs in ECEF
    # it also supports ground station calculations

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
    data[['glong', 'glat', 'alt']] = output[['glong', 'glat', 'alt']]
    data[['position_ecef_x', 'position_ecef_y', 'position_ecef_z']] = \
        output[['x', 'y', 'z']]
    data['obs_sat_az_angle'] = output['obs_sat_az_angle']
    data['obs_sat_el_angle'] = output['obs_sat_el_angle']
    data['obs_sat_slant_range'] = output['obs_sat_slant_range']
    return data, meta.copy()


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


def list_files(tag=None, sat_id=None, data_path=None, format_str=None):
    """Produce a fake list of files spanning a year"""

    index = pds.date_range(pysat.datetime(2017, 12, 1),
                           pysat.datetime(2018, 12, 1))
    # file list is effectively just the date in string format - '%D' works
    # only in Mac. '%x' workins in both Windows and Mac
    names = [data_path + date.strftime('%Y-%m-%d') + '.nofile'
             for date in index]
    return pysat.Series(names, index=index)


def download(date_array, tag, sat_id, data_path=None, user=None,
             password=None):
    """ Data is simulated so no download routine is possible. Simple pass
    function"""
    pass


def add_sc_attitude_vectors(inst):
    """
    Add attitude vectors for spacecraft assuming ram pointing.

    Presumes spacecraft is pointed along the velocity vector (x), z is
    generally nadir pointing (positive towards Earth), and y completes the
    right handed system (generally southward).

    Notes
    -----
        Expects velocity and position of spacecraft in Earth Centered
        Earth Fixed (ECEF) coordinates to be in the instrument object
        and named velocity_ecef_* (*=x,y,z) and position_ecef_* (*=x,y,z)

        Adds attitude vectors for spacecraft in the ECEF basis by calculating
        the scalar product of each attitude vector with each component of ECEF.

    Parameters
    ----------
    inst : pysat.Instrument
        Instrument object

    Returns
    -------
    None
        Modifies pysat.Instrument object in place to include S/C attitude
        unit vectors, expressed in ECEF basis. Vectors are named
        sc_(x,y,z)hat_ecef_(x,y,z).
        sc_xhat_ecef_x is the spacecraft unit vector along x (positive along
        velocity vector) reported in ECEF, ECEF x-component.

    """
    import pysatMagVect

    # ram pointing is along velocity vector
    inst['sc_xhat_ecef_x'], inst['sc_xhat_ecef_y'], inst['sc_xhat_ecef_z'] = \
        pysatMagVect.normalize_vector(inst['velocity_ecef_x'],
                                      inst['velocity_ecef_y'],
                                      inst['velocity_ecef_z'])

    # begin with z along Nadir (towards Earth)
    # if orbit isn't perfectly circular, then the s/c z vector won't
    # point exactly along nadir. However, nadir pointing is close enough
    # to the true z (in the orbital plane) that we can use it to get y,
    # and use x and y to get the real z
    inst['sc_zhat_ecef_x'], inst['sc_zhat_ecef_y'], inst['sc_zhat_ecef_z'] = \
        pysatMagVect.normalize_vector(-inst['position_ecef_x'],
                                      -inst['position_ecef_y'],
                                      -inst['position_ecef_z'])

    # get y vector assuming right hand rule
    # Z x X = Y
    inst['sc_yhat_ecef_x'], inst['sc_yhat_ecef_y'], inst['sc_yhat_ecef_z'] = \
        pysatMagVect.cross_product(inst['sc_zhat_ecef_x'],
                                   inst['sc_zhat_ecef_y'],
                                   inst['sc_zhat_ecef_z'],
                                   inst['sc_xhat_ecef_x'],
                                   inst['sc_xhat_ecef_y'],
                                   inst['sc_xhat_ecef_z'])
    # normalize since Xhat and Zhat from above may not be orthogonal
    inst['sc_yhat_ecef_x'], inst['sc_yhat_ecef_y'], inst['sc_yhat_ecef_z'] = \
        pysatMagVect.normalize_vector(inst['sc_yhat_ecef_x'],
                                      inst['sc_yhat_ecef_y'],
                                      inst['sc_yhat_ecef_z'])

    # strictly, need to recalculate Zhat so that it is consistent with RHS
    # just created
    # Z = X x Y
    inst['sc_zhat_ecef_x'], inst['sc_zhat_ecef_y'], inst['sc_zhat_ecef_z'] = \
        pysatMagVect.cross_product(inst['sc_xhat_ecef_x'],
                                   inst['sc_xhat_ecef_y'],
                                   inst['sc_xhat_ecef_z'],
                                   inst['sc_yhat_ecef_x'],
                                   inst['sc_yhat_ecef_y'],
                                   inst['sc_yhat_ecef_z'])

    # Adding metadata
    inst.meta['sc_xhat_ecef_x'] = {'units': '',
                                   'desc': 'S/C attitude (x-direction, ram) ' +
                                   'unit vector, expressed in ECEF basis, ' +
                                   'x-component'}
    inst.meta['sc_xhat_ecef_y'] = {'units': '',
                                   'desc': 'S/C attitude (x-direction, ram) ' +
                                   'unit vector, expressed in ECEF basis, ' +
                                   'y-component'}
    inst.meta['sc_xhat_ecef_z'] = {'units': '',
                                   'desc': 'S/C attitude (x-direction, ram) ' +
                                   'unit vector, expressed in ECEF basis, ' +
                                   'z-component'}

    inst.meta['sc_zhat_ecef_x'] = {'units': '',
                                   'desc': 'S/C attitude (z-direction, ' +
                                   'generally nadir) unit vector, expressed ' +
                                   'in ECEF basis, x-component'}
    inst.meta['sc_zhat_ecef_y'] = {'units': '',
                                   'desc': 'S/C attitude (z-direction, ' +
                                   'generally nadir) unit vector, expressed ' +
                                   'in ECEF basis, y-component'}
    inst.meta['sc_zhat_ecef_z'] = {'units': '',
                                   'desc': 'S/C attitude (z-direction, ' +
                                   'generally nadir) unit vector, expressed ' +
                                   'in ECEF basis, z-component'}

    inst.meta['sc_yhat_ecef_x'] = {'units': '',
                                   'desc': 'S/C attitude (y-direction, ' +
                                   'generally south) unit vector, expressed ' +
                                   'in ECEF basis, x-component'}
    inst.meta['sc_yhat_ecef_y'] = {'units': '',
                                   'desc': 'S/C attitude (y-direction, ' +
                                   'generally south) unit vector, expressed ' +
                                   'in ECEF basis, y-component'}
    inst.meta['sc_yhat_ecef_z'] = {'units': '',
                                   'desc': 'S/C attitude (y-direction, ' +
                                   'generally south) unit vector, expressed ' +
                                   'in ECEF basis, z-component'}

    # check what magnitudes we get
    mag = np.sqrt(inst['sc_zhat_ecef_x']**2 + inst['sc_zhat_ecef_y']**2 +
                  inst['sc_zhat_ecef_z']**2)
    idx, = np.where((mag < .999999999) | (mag > 1.000000001))
    if len(idx) > 0:
        print(mag[idx])
        raise RuntimeError('Unit vector generation failure. Not sufficently ' +
                           'orthogonal.')

    return


def calculate_ecef_velocity(inst):
    """
    Calculates spacecraft velocity in ECEF frame.

    Presumes that the spacecraft velocity in ECEF is in
    the input instrument object as position_ecef_*. Uses a symmetric
    difference to calculate the velocity thus endpoints will be
    set to NaN. Routine should be run using pysat data padding feature
    to create valid end points.

    Parameters
    ----------
    inst : pysat.Instrument
        Instrument object

    Returns
    -------
    None
        Modifies pysat.Instrument object in place to include ECEF velocity
        using naming scheme velocity_ecef_* (*=x,y,z)

    """

    x = inst['position_ecef_x']
    vel_x = (x.values[2:] - x.values[0:-2])/2.

    y = inst['position_ecef_y']
    vel_y = (y.values[2:] - y.values[0:-2])/2.

    z = inst['position_ecef_z']
    vel_z = (z.values[2:] - z.values[0:-2])/2.

    inst[1:-1, 'velocity_ecef_x'] = vel_x
    inst[1:-1, 'velocity_ecef_y'] = vel_y
    inst[1:-1, 'velocity_ecef_z'] = vel_z

    inst.meta['velocity_ecef_x'] = {'units': 'km/s',
                                    'desc': 'Velocity of satellite ' +
                                    'calculated with respect to ECEF frame.'}
    inst.meta['velocity_ecef_y'] = {'units': 'km/s',
                                    'desc': 'Velocity of satellite ' +
                                    'calculated with respect to ECEF frame.'}
    inst.meta['velocity_ecef_z'] = {'units': 'km/s',
                                    'desc': 'Velocity of satellite ' +
                                    'calculated with respect to ECEF frame.'}
    return


def project_ecef_vector_onto_sc(inst, x_label, y_label, z_label,
                                new_x_label, new_y_label, new_z_label,
                                meta=None):
    """Express input vector using s/c attitude directions

    x - ram pointing
    y - generally southward
    z - generally nadir

    Parameters
    ----------
    x_label : string
        Label used to get ECEF-X component of vector to be projected
    y_label : string
        Label used to get ECEF-Y component of vector to be projected
    z_label : string
        Label used to get ECEF-Z component of vector to be projected
    new_x_label : string
        Label used to set X component of projected vector
    new_y_label : string
        Label used to set Y component of projected vector
    new_z_label : string
        Label used to set Z component of projected vector
    meta : array_like of dicts (None)
        Dicts contain metadata to be assigned.
    """

    import pysatMagVect

    x, y, z = \
        pysatMagVect.project_ecef_vector_onto_basis(inst[x_label],
                                                    inst[y_label],
                                                    inst[z_label],
                                                    inst['sc_xhat_ecef_x'],
                                                    inst['sc_xhat_ecef_y'],
                                                    inst['sc_xhat_ecef_z'],
                                                    inst['sc_yhat_ecef_x'],
                                                    inst['sc_yhat_ecef_y'],
                                                    inst['sc_yhat_ecef_z'],
                                                    inst['sc_zhat_ecef_x'],
                                                    inst['sc_zhat_ecef_y'],
                                                    inst['sc_zhat_ecef_z'])
    inst[new_x_label] = x
    inst[new_y_label] = y
    inst[new_z_label] = z

    if meta is not None:
        inst.meta[new_x_label] = meta[0]
        inst.meta[new_y_label] = meta[1]
        inst.meta[new_z_label] = meta[2]

    return


def project_hwm_onto_sc(inst):

    import pysatMagVect

    total_wind_x = inst['zonal_wind']*inst['unit_zonal_wind_ecef_x'] + \
        inst['meridional_wind']*inst['unit_mer_wind_ecef_x']
    total_wind_y = inst['zonal_wind']*inst['unit_zonal_wind_ecef_y'] + \
        inst['meridional_wind']*inst['unit_mer_wind_ecef_y']
    total_wind_z = inst['zonal_wind']*inst['unit_zonal_wind_ecef_z'] + \
        inst['meridional_wind']*inst['unit_mer_wind_ecef_z']

    x, y, z = \
        pysatMagVect.project_ecef_vector_onto_basis(total_wind_x,
                                                    total_wind_y,
                                                    total_wind_z,
                                                    inst['sc_xhat_ecef_x'],
                                                    inst['sc_xhat_ecef_y'],
                                                    inst['sc_xhat_ecef_z'],
                                                    inst['sc_yhat_ecef_x'],
                                                    inst['sc_yhat_ecef_y'],
                                                    inst['sc_yhat_ecef_z'],
                                                    inst['sc_zhat_ecef_x'],
                                                    inst['sc_zhat_ecef_y'],
                                                    inst['sc_zhat_ecef_z'])
    inst['sim_wind_sc_x'] = x
    inst['sim_wind_sc_y'] = y
    inst['sim_wind_sc_z'] = z

    inst.meta['sim_wind_sc_x'] = {'units': 'm/s',
                                  'long_name': 'Simulated x-vector ' +
                                  'instrument wind',
                                  'desc': 'Wind from model as measured ' +
                                  'by instrument in its x-direction'}
    inst.meta['sim_wind_sc_y'] = {'units': 'm/s',
                                  'long_name': 'Simulated y-vector ' +
                                  'instrument wind',
                                  'desc': 'Wind from model as measured ' +
                                  'by instrument in its y-direction'}
    inst.meta['sim_wind_sc_z'] = {'units': 'm/s',
                                  'long_name': 'Simulated z-vector ' +
                                  'instrument wind',
                                  'desc': 'Wind from model as measured ' +
                                  'by instrument in its z-direction'}

    return


def plot_simulated_data(inst, filename=None):

    import matplotlib
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec
    from matplotlib.collections import LineCollection
    from mpl_toolkits.basemap import Basemap

    if filename is None:
        out_fname = './summary_orbit_simulated_data.png'
    else:
        out_fname = filename

    # make monotonically increasing longitude signal
    diff = inst['glong'].diff()

    idx, = np.where(diff < 0.)
    for item in idx:
        inst[item:, 'glong'] += 360.

    f = plt.figure(figsize=(8.5, 7))

    time1 = inst.data.index[0].strftime('%Y-%h-%d %H:%M:%S')
    if inst.data.index[0].date() == inst.data.index[-1].date():
        time2 = inst.data.index[-1].strftime('%H:%M:%S')
    else:
        time2 = inst.data.index[-1].strftime('%Y-%h-%d %H:%M:%S')
    # Overall Plot Title
    plt.suptitle(''.join(('Simulated inst ', time1, ' -- ', time2)),
                 fontsize=18)

    # create grid for plots
    gs = gridspec.GridSpec(5, 2, width_ratios=[12, 1])

    ax = f.add_subplot(gs[0, 0])
    plt.plot(np.log10(inst['ion_dens']), 'k', label='total')
    plt.plot(np.log10(inst['ion_dens']*inst['frac_dens_o']), 'r', label='O+')
    plt.plot(np.log10(inst['ion_dens']*inst['frac_dens_h']), 'b', label='H+')
    plt.legend(loc=(01.01, 0.15))
    ax.set_title('Log Ion Density')
    ax.set_ylabel('Log Density (N/cc)')
    ax.set_ylim([1., 6.])
    ax.axes.get_xaxis().set_visible(False)

    ax2 = f.add_subplot(gs[1, 0], sharex=ax)
    plt.plot(inst['ion_temp'])
    plt.legend(loc=(1.01, 0.15))
    ax2.set_title('Ion Temperature')
    ax2.set_ylabel('Temp (K)')
    ax2.set_ylim([500., 1500.])
    ax2.axes.get_xaxis().set_visible(False)

    # determine altitudes greater than 770 km
    # idx, = np.where(inst['alt'] > 770.)

    ax3 = f.add_subplot(gs[2, 0], sharex=ax)
    plt.plot(inst['sim_wind_sc_x'], color='b', linestyle='--')
    plt.plot(inst['sim_wind_sc_y'], color='r', linestyle='--')
    plt.plot(inst['sim_wind_sc_z'], color='g', linestyle='--')
    ax3.set_title('Neutral Winds in S/C X, Y, and Z')
    ax3.set_ylabel('Velocity (m/s)')
    ax3.set_ylim([-200., 200.])
    ax3.axes.get_xaxis().set_visible(False)
    plt.legend(loc=(1.01, 0.15))
    ax3.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%H:%M'))
    # # xlabels = [label[0:6] for label in xlabels]
    # plt.setp(ax3.xaxis.get_majorticklabels(), rotation=20, ha='right')

    ax4 = f.add_subplot(gs[3, 0], sharex=ax)
    plt.plot(inst['B_sc_x']*1e5, color='b', linestyle='--')
    plt.plot(inst['B_sc_y']*1e5, color='r', linestyle='--')
    plt.plot(inst['B_sc_z']*1e5, color='g', linestyle='--')
    ax4.set_title('Magnetic Field in S/C X, Y, and Z')
    ax4.set_ylabel('Gauss')
    ax4.set_ylim([-3.5, 3.5])
    # ax3.axes.get_xaxis().set_visible(False)
    plt.legend(loc=(1.01, 0.15))
    ax4.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%H:%M'))
    # # xlabels = [label[0:6] for label in xlabels]
    plt.setp(ax4.xaxis.get_majorticklabels(), rotation=20, ha='right')

    # inst info
    ax6 = f.add_subplot(gs[4, 0])

    # do world plot if time to be plotted is less than 285 minutes, less than
    # 3 orbits
    time_diff = inst.data.index[-1] - inst.data.index[0]
    if time_diff > pds.Timedelta(minutes=285):
        # do long time plot
        inst['glat'].plot(label='glat')  # legend=True, label='mlat')
        inst['mlt'].plot(label='mlt')  # legend=True, label='mlt')
        plt.title('Satellite Position')
        plt.legend(['mlat', 'mlt'], loc=(1.01, 0.15))
    #    inst['glong'].plot(secondary_y = True, label='glong')#legend=True,
    #       secondary_y = True, label='glong')

    else:

        # make map the same size as the other plots
        s1pos = plt.get(ax, 'position').bounds
        s6pos = plt.get(ax6, 'position').bounds
        ax6.set_position([s1pos[0], s6pos[1]+.008, s1pos[2], s1pos[3]])

        # fix longitude range for plot. Pad longitude so that first sample
        # aligned with inst measurement sample
        lon0 = inst[0, 'glong']
        lon1 = inst[-1, 'glong']

        # enforce minimal longitude window, keep graphics from being too
        # disturbed
        if (lon1-lon0) < 90:
            lon0 -= 45.
            lon1 += 45.
        if lon1 > 720:
            lon0 -= 360.
            lon1 -= 360.
            inst[:, 'glong'] -= 360.

        m = Basemap(projection='mill', llcrnrlat=-60, urcrnrlat=60.,
                    urcrnrlon=lon1.copy(), llcrnrlon=lon0.copy(),
                    resolution='c', ax=ax6, fix_aspect=False)
        # m is an object which manages drawing to the map
        # it also acts as a transformation function for geo coords to
        # plotting coords

        # coastlines
        m.drawcoastlines(ax=ax6)
        # get first longitude meridian to plot
        plon = np.ceil(lon0/60.)*60.
        m.drawmeridians(np.arange(plon, plon+360.-22.5, 60),
                        labels=[0, 0, 0, 1], ax=ax6)
        m.drawparallels(np.arange(-20, 20, 20))
        # time midway through inst to plot terminator locations
        midDate = inst.data.index[len(inst.data.index)//2]

        # plot day/night terminators
        try:
            _ = m.nightshade(midDate)
        except ValueError:
            pass

        x, y = m(inst['glong'].values, inst['glat'].values)
        points = np.array([x, y]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)
        plot_norm = plt.Normalize(300, 500)
        plot_cmap = plt.get_cmap('viridis')

        lc = LineCollection(segments, cmap=plot_cmap, norm=plot_norm,
                            linewidths=5.0)
        lc.set_array(inst['alt'].values)
        sm = plt.cm.ScalarMappable(cmap=plot_cmap, norm=plot_norm)
        sm._A = []

        ax6.add_collection(lc)

        ax6_bar = f.add_subplot(gs[4, 1])
        # plt.colorbar(sm)
        plt.colorbar(cax=ax6_bar, ax=ax6, mappable=sm,
                     orientation='vertical',
                     ticks=[300., 400., 500.])
        plt.xlabel('Altitude')
        plt.ylabel('km')

    f.tight_layout()
    # buffer for overall title
    f.subplots_adjust(bottom=0.06, top=0.91, right=.91)
    plt.subplots_adjust(hspace=0.44)

    plt.savefig(out_fname)

    return
