# -*- coding: utf-8 -*-
# Test some of the aacgmv2 method functions

import datetime as dt
import numpy as np
import pysat
import pysatMissions.methods.magcoord as mm_magcoord


class TestBasics():
    def setup(self):
        """Runs before every method to create a clean testing setup."""
        self.testInst = pysat.Instrument(platform='pysat', name='testing',
                                         inst_id='100', clean_level='clean')

    def teardown(self):
        """Clean up test environment after tests"""
        del self

    def test_add_aacgm_coordinates(self):
        """Test adding thermal plasma data to test inst"""
        self.testInst.custom_attach(mm_magcoord.add_aacgm_coordinates,
                                    kwargs={'glat_label': 'latitude',
                                            'glong_label': 'longitude',
                                            'alt_label': 'altitude'})
        self.testInst.load(date=dt.datetime(2009, 1, 1))
        targets = ['aacgm_lat', 'aacgm_long', 'aacgm_mlt']
        for target in targets:
            # Check if data is added
            assert target in self.testInst.data.keys()
            assert not np.isnan(self.testInst[target]).any()
            # Check if metadata is added
            assert target in self.testInst.meta.data.index

    def test_add_quasi_dipole_coordinates(self):
        """Test adding thermal plasma data to test inst"""
        self.testInst.custom_attach(mm_magcoord.add_quasi_dipole_coordinates,
                                    kwargs={'glat_label': 'latitude',
                                            'glong_label': 'longitude',
                                            'alt_label': 'altitude'})
        self.testInst.load(date=dt.datetime(2009, 1, 1))
        targets = ['qd_lat', 'qd_long', 'mlt']
        for target in targets:
            # Check if data is added
            assert target in self.testInst.data.keys()
            assert not np.isnan(self.testInst[target]).any()
            # Check if metadata is added
            assert target in self.testInst.meta.data.index
