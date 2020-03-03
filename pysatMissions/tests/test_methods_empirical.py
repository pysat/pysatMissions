# -*- coding: utf-8 -*-
# Test some of the pyglow method functions

import numpy as np
import pysat
from pysatMissions.methods import empirical as mm_emp


def add_altitude(inst, altitude=400.0):
    """Add altitudes to pysat_testing instrument"""

    inst['altitude'] = altitude*np.ones(inst.data.shape[0])


class TestBasics():
    def setup(self):
        """Runs before every method to create a clean testing setup."""
        self.testInst = pysat.Instrument(platform='pysat', name='testing',
                                         sat_id='100', clean_level='clean')
        # TODO: Update to custom.attach with release of pysat 3.0.0
        self.testInst.custom.attach(add_altitude, 'modify')

    def teardown(self):
        """Clean up test environment after tests"""
        del self

    def test_add_iri_thermal_plasma(self):
        """Test adding thermal plasma data to test inst"""
        # TODO: Update to custom.attach with release of pysat 3.0.0
        self.testInst.custom.attach(mm_emp.add_iri_thermal_plasma, 'modify',
                                 glat_label='latitude',
                                 glong_label='longitude',
                                 alt_label='altitude')
        self.testInst.load(date=pysat.datetime(2009, 1, 1))
        targets = ['e_temp', 'frac_dens_h', 'frac_dens_he', 'frac_dens_o',
                   'ion_dens', 'ion_temp']
        for target in targets:
            # Check if data is added
            assert target in self.testInst.data.keys()
            assert not np.isnan(self.testInst[target]).any()
            # Check if metadata is added
            assert target in self.testInst.meta.data.index

    def test_add_igrf(self):
        """Test adding igrf model to test inst"""
        # TODO: Update to custom.attach with release of pysat 3.0.0
        self.testInst.custom.attach(mm_emp.add_igrf, 'modify',
                                 glat_label='latitude',
                                 glong_label='longitude',
                                 alt_label='altitude')
        self.testInst.load(date=pysat.datetime(2009, 1, 1))
        targets = ['B', 'B_east', 'B_north', 'B_up', 'B_ecef_x', 'B_ecef_y',
                   'B_ecef_z']
        for target in targets:
            # Check if data is added
            assert target in self.testInst.data.keys()
            assert not np.isnan(self.testInst[target]).any()
            # Check if metadata is added
            assert target in self.testInst.meta.data.index

    def test_add_msis(self):
        """Test adding msis model to test inst"""
        # TODO: Update to custom.attach with release of pysat 3.0.0
        self.testInst.custom.attach(mm_emp.add_msis, 'modify',
                                 glat_label='latitude',
                                 glong_label='longitude',
                                 alt_label='altitude')
        self.testInst.load(date=pysat.datetime(2009, 1, 1))
        targets = ['Nn', 'Nn_H', 'Nn_He', 'Nn_N', 'Nn_N2', 'Nn_O', 'Nn_O2',
                   'Nn_Ar', 'Tn_msis']
        for target in targets:
            # Check if data is added
            assert target in self.testInst.data.keys()
            assert not np.isnan(self.testInst[target]).any()
            # Check if metadata is added
            assert target in self.testInst.meta.data.index

    # TODO: Add hwm tests once routine is generalized
