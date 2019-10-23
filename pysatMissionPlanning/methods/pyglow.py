# -*- coding: utf-8 -*-
"""Provides default routines for projecting pyglow model values onto locations
from pysat instruments.

"""

import pandas as pds
import numpy as np

from pyglow.pyglow import Point
import pysatMagVect

# TODO add checks for ECEF and import rest of changes here


def add_iri_thermal_plasma(inst, glat_label='glat', glong_label='glong',
                           alt_label='alt'):
    """
    Uses IRI (International Reference Ionosphere) model to simulate an
    ionosphere.

    Uses pyglow module to run IRI. Configured to use actual solar parameters
    to run model.

    Example
    -------
        # function added velow modifies the inst object upon every inst.load
        call inst.custom.add(add_iri_thermal_plasma, 'modify',
        glat_label='custom_label')

    Parameters
    ----------
    inst : pysat.Instrument
        Designed with pysat_sgp4 in mind
    glat_label : string
        label used in inst to identify WGS84 geodetic latitude (degrees)
    glong_label : string
        label used in inst to identify WGS84 geodetic longitude (degrees)
    alt_label : string
        label used in inst to identify WGS84 geodetic altitude (km, height
        above surface)

    Returns
    -------
    inst
        Input pysat.Instrument object modified to include thermal plasma
        parameters.
        'ion_temp' for ion temperature in Kelvin
        'e_temp' for electron temperature in Kelvin
        'ion_dens' for the total ion density (O+ and H+)
        'frac_dens_o' for the fraction of total density that is O+
        'frac_dens_h' for the fraction of total density that is H+

    """

    iri_params = []
    for time, lat, lon, alt in zip(inst.data.index, inst[glat_label],
                                   inst[glong_label], inst[alt_label]):
        # Point class is instantiated. Its parameters are a function of time
        # and spatial location
        pt = Point(time, lat, lon, alt)
        pt.run_iri()
        iri = {}
        # After the model is run, its members like Ti, ni[O+], etc. can be
        # accessed
        iri['ion_temp'] = pt.Ti
        iri['e_temp'] = pt.Te
        iri['ion_dens'] = pt.ni['O+'] + pt.ni['H+'] + pt.ni['HE+']
        # pt.ne - pt.ni['NO+'] - pt.ni['O2+'] - pt.ni['HE+']
        iri['frac_dens_o'] = pt.ni['O+']/iri['ion_dens']
        iri['frac_dens_h'] = pt.ni['H+']/iri['ion_dens']
        iri['frac_dens_he'] = pt.ni['HE+']/iri['ion_dens']
        iri_params.append(iri)
    iri = pds.DataFrame(iri_params)
    iri.index = inst.data.index
    inst[iri.keys()] = iri

    inst.meta['ion_temp'] = {'units': 'Kelvin', 'long_name': 'Ion Temperature'}
    inst.meta['ion_dens'] = {'units': 'N/cc', 'long_name': 'Ion Density',
                             'desc': 'Total ion density including O+ and H+ ' +
                             'from IRI model run.'}
    inst.meta['frac_dens_o'] = {'units': '',
                                'long_name': 'Fractional O+ Density'}
    inst.meta['frac_dens_h'] = {'units': '',
                                'long_name': 'Fractional H+ Density'}


def add_igrf(inst, glat_label='glat', glong_label='glong', alt_label='alt'):
    """
    Uses International Geomagnetic Reference Field (IGRF) model to obtain
    geomagnetic field values.

    Uses pyglow module to run IGRF. Configured to use actual solar parameters
    to run model.

    Example
    -------
        # function added velow modifies the inst object upon every inst.load
        call inst.custom.add(add_igrf, 'modify', glat_label='custom_label')

    Parameters
    ----------
    inst : pysat.Instrument
        Designed with pysat_sgp4 in mind
    glat_label : string
        label used in inst to identify WGS84 geodetic latitude (degrees)
    glong_label : string
        label used in inst to identify WGS84 geodetic longitude (degrees)
    alt_label : string
        label used in inst to identify WGS84 geodetic altitude (km, height
        above surface)

    Returns
    -------
    inst
        Input pysat.Instrument object modified to include HWM winds.
        'B' total geomagnetic field
        'B_east' Geomagnetic field component along east/west directions
                (+ east)
        'B_north' Geomagnetic field component along north/south directions
                (+ north)
        'B_up' Geomagnetic field component along up/down directions (+ up)
        'B_ecef_x' Geomagnetic field component along ECEF x
        'B_ecef_y' Geomagnetic field component along ECEF y
        'B_ecef_z' Geomagnetic field component along ECEF z

    """

    igrf_params = []
    for time, lat, lon, alt in zip(inst.data.index, inst[glat_label],
                                   inst[glong_label], inst[alt_label]):
        pt = Point(time, lat, lon, alt)
        pt.run_igrf()
        igrf = {}
        igrf['B'] = pt.B
        igrf['B_east'] = pt.Bx
        igrf['B_north'] = pt.By
        igrf['B_up'] = pt.Bz
        igrf_params.append(igrf)
    igrf = pds.DataFrame(igrf_params)
    igrf.index = inst.data.index
    inst[igrf.keys()] = igrf

    # convert magnetic field in East/north/up to ECEF basis
    x, y, z = pysatMagVect.enu_to_ecef_vector(inst['B_east'],
                                              inst['B_north'],
                                              inst['B_up'],
                                              inst[glat_label],
                                              inst[glong_label])
    inst['B_ecef_x'] = x
    inst['B_ecef_y'] = y
    inst['B_ecef_z'] = z

    # metadata
    inst.meta['B'] = {'units': 'nT',
                      'desc': 'Total geomagnetic field from IGRF.'}
    inst.meta['B_east'] = {'units': 'nT',
                           'desc': 'Geomagnetic field from IGRF expressed ' +
                           'using the East/North/Up (ENU) basis.'}
    inst.meta['B_north'] = {'units': 'nT',
                            'desc': 'Geomagnetic field from IGRF expressed ' +
                            'using the East/North/Up (ENU) basis.'}
    inst.meta['B_up'] = {'units': 'nT',
                         'desc': 'Geomagnetic field from IGRF expressed ' +
                         'using the East/North/Up (ENU) basis.'}

    inst.meta['B_ecef_x'] = {'units': 'nT',
                             'desc': 'Geomagnetic field from IGRF expressed ' +
                             'using the Earth Centered Earth Fixed (ECEF) ' +
                             'basis.'}
    inst.meta['B_ecef_y'] = {'units': 'nT',
                             'desc': 'Geomagnetic field from IGRF expressed ' +
                             'using the Earth Centered Earth Fixed (ECEF) ' +
                             'basis.'}
    inst.meta['B_ecef_z'] = {'units': 'nT',
                             'desc': 'Geomagnetic field from IGRF expressed ' +
                             'using the Earth Centered Earth Fixed (ECEF) ' +
                             'basis.'}
    return


def add_msis(inst, glat_label='glat', glong_label='glong', alt_label='alt'):
    """
    Uses MSIS model to obtain thermospheric values.

    Uses pyglow module to run MSIS. Configured to use actual solar parameters
    to run model.

    Example
    -------
        # function added velow modifies the inst object upon every inst.load
        call inst.custom.add(add_msis, 'modify', glat_label='custom_label')

    Parameters
    ----------
    inst : pysat.Instrument
        Designed with pysat_sgp4 in mind
    glat_label : string
        label used in inst to identify WGS84 geodetic latitude (degrees)
    glong_label : string
        label used in inst to identify WGS84 geodetic longitude (degrees)
    alt_label : string
        label used in inst to identify WGS84 geodetic altitude (km, height
        above surface)

    Returns
    -------
    inst
        Input pysat.Instrument object modified to include MSIS values winds.
        'Nn' total neutral density particles/cm^3
        'Nn_N' Nitrogen number density (particles/cm^3)
        'Nn_N2' N2 number density (particles/cm^3)
        'Nn_O' Oxygen number density (particles/cm^3)
        'Nn_O2' O2 number density (particles/cm^3)
        'Tn_msis' Temperature from MSIS (Kelvin)

    """

    msis_params = []
    for time, lat, lon, alt in zip(inst.data.index, inst[glat_label],
                                   inst[glong_label], inst[alt_label]):
        pt = Point(time, lat, lon, alt)
        pt.run_msis()
        msis = {}
        total = 0
        for key in pt.nn.keys():
            total += pt.nn[key]
        msis['Nn'] = total
        msis['Nn_N'] = pt.nn['N']
        msis['Nn_N2'] = pt.nn['N2']
        msis['Nn_O'] = pt.nn['O']
        msis['Nn_O2'] = pt.nn['O2']
        msis['Tn_msis'] = pt.Tn_msis
        msis_params.append(msis)
    msis = pds.DataFrame(msis_params)
    msis.index = inst.data.index
    inst[msis.keys()] = msis

    # metadata
    inst.meta['Nn'] = {'units': 'cm^-3',
                       'desc': 'Total neutral number particle density ' +
                       'from MSIS.'}
    inst.meta['Nn_N'] = {'units': 'cm^-3',
                         'desc': 'Total nitrogen number particle density ' +
                         'from MSIS.'}
    inst.meta['Nn_N2'] = {'units': 'cm^-3',
                          'desc': 'Total N2 number particle density ' +
                          'from MSIS.'}
    inst.meta['Nn_O'] = {'units': 'cm^-3',
                         'desc': 'Total oxygen number particle density ' +
                         'from MSIS.'}
    inst.meta['Nn_O2'] = {'units': 'cm^-3',
                          'desc': 'Total O2 number particle density ' +
                          'from MSIS.'}
    inst.meta['Tn_msis'] = {'units': 'K',
                            'desc': 'Neutral temperature from MSIS.'}

    return


def add_hwm_winds_and_ecef_vectors(inst, glat_label='glat',
                                   glong_label='glong', alt_label='alt'):
    """
    Uses HWM (Horizontal Wind Model) model to obtain neutral wind details.

    Uses pyglow module to run HWM. Configured to use actual solar parameters
    to run model.

    Example
    -------
        # function added velow modifies the inst object upon every inst.load
        call inst.custom.add(add_hwm_winds_and_ecef_vectors, 'modify',
        glat_label='custom_label')

    Parameters
    ----------
    inst : pysat.Instrument
        Designed with pysat_sgp4 in mind
    glat_label : string
        label used in inst to identify WGS84 geodetic latitude (degrees)
    glong_label : string
        label used in inst to identify WGS84 geodetic longitude (degrees)
    alt_label : string
        label used in inst to identify WGS84 geodetic altitude (km, height
        above surface)

    Returns
    -------
    inst
        Input pysat.Instrument object modified to include HWM winds.
        'zonal_wind' for the east/west winds (u in model) in m/s
        'meiridional_wind' for the north/south winds (v in model) in m/s
        'unit_zonal_wind_ecef_*' (*=x,y,z) is the zonal vector expressed in
                the ECEF basis
        'unit_mer_wind_ecef_*' (*=x,y,z) is the meridional vector expressed
                in the ECEF basis
        'sim_inst_wind_*' (*=x,y,z) is the projection of the total wind
                vector onto s/c basis

    """

    hwm_params = []
    for time, lat, lon, alt in zip(inst.data.index, inst[glat_label],
                                   inst[glong_label], inst[alt_label]):
        # Point class is instantiated.
        # Its parameters are a function of time and spatial location
        pt = Point(time, lat, lon, alt)
        pt.run_hwm()
        hwm = {}
        hwm['zonal_wind'] = pt.u
        hwm['meridional_wind'] = pt.v
        hwm_params.append(hwm)
    hwm = pds.DataFrame(hwm_params)
    hwm.index = inst.data.index
    inst[['zonal_wind', 'meridional_wind']] = hwm[['zonal_wind',
                                                   'meridional_wind']]

    # calculate zonal unit vector in ECEF
    # zonal wind: east - west; positive east
    # EW direction is tangent to XY location of S/C in ECEF coordinates
    mag = np.sqrt(inst['position_ecef_x']**2 + inst['position_ecef_y']**2)
    inst['unit_zonal_wind_ecef_x'] = -inst['position_ecef_y']/mag
    inst['unit_zonal_wind_ecef_y'] = inst['position_ecef_x']/mag
    inst['unit_zonal_wind_ecef_z'] = 0 * inst['position_ecef_x']

    # calculate meridional unit vector in ECEF
    # meridional wind: north - south; positive north
    # mer direction completes RHS of position and zonal vector
    unit_pos_x, unit_pos_y, unit_pos_z = \
        pysatMagVect.normalize_vector(-inst['position_ecef_x'],
                                      -inst['position_ecef_y'],
                                      -inst['position_ecef_z'])

    # mer = r x zonal
    merx, mery, merz = \
        pysatMagVect.cross_product(unit_pos_x, unit_pos_y, unit_pos_z,
                                   inst['unit_zonal_wind_ecef_x'],
                                   inst['unit_zonal_wind_ecef_y'],
                                   inst['unit_zonal_wind_ecef_z'])
    inst['unit_mer_wind_ecef_x'] = merx
    inst['unit_mer_wind_ecef_y'] = mery
    inst['unit_mer_wind_ecef_z'] = merz

    # Adding metadata information
    inst.meta['zonal_wind'] = {'units': 'm/s', 'long_name': 'Zonal Wind',
                               'desc': 'HWM model zonal wind'}
    inst.meta['meridional_wind'] = {'units': 'm/s',
                                    'long_name': 'Meridional Wind',
                                    'desc': 'HWM model meridional wind'}
    inst.meta['unit_zonal_wind_ecef_x'] = \
        {'units': '',
         'long_name': 'Zonal Wind Unit ECEF x-vector',
         'desc': 'x-value of zonal wind unit vector in ECEF coordinates'}
    inst.meta['unit_zonal_wind_ecef_y'] = \
        {'units': '',
         'long_name': 'Zonal Wind Unit ECEF y-vector',
         'desc': 'y-value of zonal wind unit vector in ECEF coordinates'}
    inst.meta['unit_zonal_wind_ecef_z'] = \
        {'units': '',
         'long_name': 'Zonal Wind Unit ECEF z-vector',
         'desc': 'z-value of zonal wind unit vector in ECEF coordinates'}
    inst.meta['unit_mer_wind_ecef_x'] = \
        {'units': '',
         'long_name': 'Meridional Wind Unit ECEF x-vector',
         'desc': 'x-value of meridional wind unit vector in ECEF coordinates'}
    inst.meta['unit_mer_wind_ecef_y'] = \
        {'units': '',
         'long_name': 'Meridional Wind Unit ECEF y-vector',
         'desc': 'y-value of meridional wind unit vector in ECEF coordinates'}
    inst.meta['unit_mer_wind_ecef_z'] = \
        {'units': '',
         'long_name': 'Meridional Wind Unit ECEF z-vector',
         'desc': 'z-value of meridional wind unit vector in ECEF coordinates'}

    return
