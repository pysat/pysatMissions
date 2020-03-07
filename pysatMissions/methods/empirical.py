# -*- coding: utf-8 -*-
"""Provides default routines for projecting pyglow model values onto locations
from pysat instruments.

"""

import pandas as pds
import numpy as np
import warnings

try:
    from pyglow.pyglow import Point
except ImportError:
    pass
import pysatMagVect

from pysatMissions.methods import spacecraft as mm_sc


# TODO add checks for ECEF and import rest of changes here
pyglow_warning = ' '.join(['pyglow must be installed to use this',
                           'function.  See instructions at',
                           'https://github.com/pysat/pysatMissions'])


def add_iri_thermal_plasma(inst, glat_label='glat', glong_label='glong',
                           alt_label='alt'):
    """
    Uses IRI (International Reference Ionosphere) model to simulate an
    ionosphere.

    Uses pyglow module to run IRI. Configured to use actual solar parameters
    to run model.

    Parameters
    ----------
    inst : pysat.Instrument
        instrument object including lat, lon, and alt as timeseries
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

    Example
    -------
        # function added velow modifies the inst object upon every inst.load
        call inst.custom.attach(add_iri_thermal_plasma, 'modify',
        glat_label='custom_label')

    """

    iri_params = []
    try:
        for time, lat, lon, alt in zip(inst.data.index, inst[glat_label],
                                       inst[glong_label], inst[alt_label]):
            # Point class is instantiated. Its parameters are a function of
            # time and spatial location
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
    except NameError:
        # Triggered if pyglow not installed
        warnings.warn(pyglow_warning, stacklevel=2)

    inst.meta['ion_temp'] = {'units': 'Kelvin', 'long_name': 'Ion Temperature',
                             'desc': ' '.join(['Ion temperature from IRI',
                                               'model run.'])}
    inst.meta['ion_dens'] = {'units': 'N/cc', 'long_name': 'Ion Density',
                             'desc': ' '.join(['Total ion density including O+'
                                               'and H+ from IRI model run.'])}
    inst.meta['frac_dens_o'] = {'units': '',
                                'long_name': 'Fractional O+ Density',
                                'desc': ' '.join(['Fraction of O+ generated'
                                                  'from IRI model run.'])}
    inst.meta['frac_dens_h'] = {'units': '',
                                'long_name': 'Fractional H+ Density',
                                'desc': ' '.join(['Fraction of O+ generated'
                                                  'from IRI model run.'])}


def add_igrf(inst, glat_label='glat', glong_label='glong', alt_label='alt'):
    """
    Uses International Geomagnetic Reference Field (IGRF) model to obtain
    geomagnetic field values.

    Uses pyglow module to run IGRF. Configured to use actual solar parameters
    to run model.

    Parameters
    ----------
    inst : pysat.Instrument
        instrument object including lat, lon, and alt as timeseries
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

    Example
    -------
        # function added velow modifies the inst object upon every inst.load
        call inst.custom.attach(add_igrf, 'modify', glat_label='custom_label')

    """

    igrf_params = []
    try:
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
    except NameError:
        # Triggered if pyglow not installed
        warnings.warn(pyglow_warning, stacklevel=2)

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

    Parameters
    ----------
    inst : pysat.Instrument
        instrument object including lat, lon, and alt as timeseries
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

    Example
    -------
        # function added velow modifies the inst object upon every inst.load
        call inst.custom.attach(add_msis, 'modify', glat_label='custom_label')

    """

    msis_params = []
    try:
        for time, lat, lon, alt in zip(inst.data.index, inst[glat_label],
                                       inst[glong_label], inst[alt_label]):
            pt = Point(time, lat, lon, alt)
            pt.run_msis()
            msis = {}
            total = 0
            for key in pt.nn.keys():
                total += pt.nn[key]
            msis['Nn'] = total
            msis['Nn_H'] = pt.nn['H']
            msis['Nn_He'] = pt.nn['HE']
            msis['Nn_N'] = pt.nn['N']
            msis['Nn_N2'] = pt.nn['N2']
            msis['Nn_O'] = pt.nn['O']
            msis['Nn_O2'] = pt.nn['O2']
            msis['Nn_Ar'] = pt.nn['AR']
            msis['Tn_msis'] = pt.Tn_msis
            msis_params.append(msis)
        msis = pds.DataFrame(msis_params)
        msis.index = inst.data.index
        inst[msis.keys()] = msis
    except NameError:
        # Triggered if pyglow not installed
        warnings.warn(pyglow_warning, stacklevel=2)

    # metadata
    inst.meta['Nn'] = {'units': 'cm^-3',
                       'desc': 'Total neutral number particle density ' +
                       'from MSIS.'}
    inst.meta['Nn_H'] = {'units': 'cm^-3',
                         'desc': 'Total hydrogen number particle density ' +
                         'from MSIS.'}
    inst.meta['Nn_He'] = {'units': 'cm^-3',
                          'desc': 'Total helium number particle density ' +
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
    inst.meta['Nn_Ar'] = {'units': 'cm^-3',
                          'desc': 'Total argon number particle density ' +
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

    Parameters
    ----------
    inst : pysat.Instrument
        instrument object including lat, lon, and alt as timeseries
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

    Example
    -------
        # function added velow modifies the inst object upon every inst.load
        call inst.custom.attach(add_hwm_winds_and_ecef_vectors, 'modify',
        glat_label='custom_label')

    """

    hwm_params = []
    try:
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
    except NameError:
        # Triggered if pyglow not installed
        warnings.warn(pyglow_warning, stacklevel=2)

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
    def get_ecef_wind_meta(coord='x', geo='mer'):
        """Generates consistent metadat for ecef winds"""
        if geo == 'mer':
            name = 'Meridional'
        else:
            name = 'Zonal'
        dict = {'units': '',
                'long_name': ' '.join(['{name:s} Wind Unit ECEF',
                                       '{coord:s}-vector']
                                      ).format(name=name, coord=coord),
                'desc': ' '.join(['{coord:s}-value of {name:s} wind unit',
                                  'vector in ECEF coordinates']
                                 ).format(name=name.lower(), coord=coord)}
        return dict

    inst.meta['zonal_wind'] = {'units': 'm/s',
                               'long_name': 'Zonal Wind',
                               'desc': 'HWM model zonal wind'}
    inst.meta['meridional_wind'] = {'units': 'm/s',
                                    'long_name': 'Meridional Wind',
                                    'desc': 'HWM model meridional wind'}
    inst.meta['unit_zonal_wind_ecef_x'] = get_ecef_wind_meta(coord='x',
                                                             geo='zon')
    inst.meta['unit_zonal_wind_ecef_y'] = get_ecef_wind_meta(coord='y',
                                                             geo='zon')
    inst.meta['unit_zonal_wind_ecef_z'] = get_ecef_wind_meta(coord='z',
                                                             geo='zon')
    inst.meta['unit_mer_wind_ecef_x'] = get_ecef_wind_meta(coord='x',
                                                           geo='mer')
    inst.meta['unit_mer_wind_ecef_y'] = get_ecef_wind_meta(coord='y',
                                                           geo='mer')
    inst.meta['unit_mer_wind_ecef_z'] = get_ecef_wind_meta(coord='z',
                                                           geo='mer')

    return


def project_hwm_onto_sc(inst):
    """
    Projects the modeled wind onto the spacecraft coordinates.

    Parameters
    ----------
    inst : pysat.Instrument
        instrument object including unit vectors in ecef coords

    Returns
    -------
    inst
        Input pysat.Instrument object modified to include neutral wind
        parameters.

    Example
    -------
        # function added velow modifies the inst object upon every inst.load
        call inst.custom.attach(project_hwm_onto_sc, 'modify')

    """

    def get_wind_comp(inst, direction='x'):
        unit_zon = 'unit_zonal_wind_ecef_' + direction
        unit_mer = 'unit_mer_wind_ecef_' + direction

        return (inst['zonal_wind']*inst[unit_zon] +
                inst['meridional_wind']*inst[unit_mer])

    def get_wind_meta(coord='x'):
        dict = {'units': 'm/s',
                'long_name': ' '.join(['Simulated {:s}-vector instrument',
                                       'wind']).format(coord),
                'desc': ' '.join(['Wind from model as measured by instrument',
                                  'in its {:s}-direction']).format(coord)}
        return dict

    inst['total_wind_x'] = get_wind_comp(inst, direction='x')
    inst['total_wind_y'] = get_wind_comp(inst, direction='y')
    inst['total_wind_z'] = get_wind_comp(inst, direction='z')

    mm_sc.project_ecef_vector_onto_sc(inst, 'total_wind_x', 'total_wind_y',
                                      'total_wind_z', 'sim_wind_sc_x',
                                      'sim_wind_sc_y', 'sim_wind_sc_z')

    inst.meta['sim_wind_sc_x'] = get_wind_meta('x')
    inst.meta['sim_wind_sc_y'] = get_wind_meta('y')
    inst.meta['sim_wind_sc_z'] = get_wind_meta('z')

    return
