# -*- coding: utf-8 -*-
# Test some of the aacgmv2 method functions

import numpy as np
import pysat
import pysatMissions.methods.magcoord as mm_magcoord


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

    def test_add_aacgm_coordinates(self):
        """Test adding thermal plasma data to test inst"""
        # TODO: Update to custom.attach with release of pysat 3.0.0
        self.testInst.custom.attach(mm_magcoord.add_aacgm_coordinates,
                                 'modify',
                                 glat_label='latitude',
                                 glong_label='longitude',
                                 alt_label='altitude')
        self.testInst.load(date=pysat.datetime(2009, 1, 1))
        targets = ['aacgm_lat', 'aacgm_long', 'aacgm_mlt']
        for target in targets:
            # Check if data is added
            assert target in self.testInst.data.keys()
            assert not np.isnan(self.testInst[target]).any()
            # Check if metadata is added
            assert target in self.testInst.meta.data.index

    def test_add_quasi_dipole_coordinates(self):
        """Test adding thermal plasma data to test inst"""
        # TODO: Update to custom.attach with release of pysat 3.0.0
        self.testInst.custom.attach(mm_magcoord.add_quasi_dipole_coordinates,
                                 'modify',
                                 glat_label='latitude',
                                 glong_label='longitude',
                                 alt_label='altitude')
        self.testInst.load(date=pysat.datetime(2009, 1, 1))
        targets = ['qd_lat', 'qd_long', 'mlt']
        for target in targets:
            # Check if data is added
            assert target in self.testInst.data.keys()
            assert not np.isnan(self.testInst[target]).any()
            # Check if metadata is added
            assert target in self.testInst.meta.data.index
