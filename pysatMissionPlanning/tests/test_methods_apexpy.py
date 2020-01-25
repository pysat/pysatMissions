# -*- coding: utf-8 -*-
# Test some of the apexpy method functions

import numpy as np
import pysat
import pysatMissionPlanning.methods.apexpy as methapex


def add_altitude(inst, altitude=400.0):
    """Add altitudes to pysat_testing instrument"""

    inst['altitude'] = altitude*np.ones(inst.data.shape[0])


class TestBasics():
    def setup(self):
        """Runs before every method to create a clean testing setup."""
        self.testInst = pysat.Instrument(platform='pysat', name='testing',
                                         sat_id='100', clean_level='clean')
        self.testInst.custom.add(add_altitude, 'modify')

    def teardown(self):
        """Clean up test environment after tests"""
        del self

    def test_add_quasi_dipole_coordinates(self):
        """Test adding thermal plasma data to test inst"""
        self.testInst.custom.add(methapex.add_quasi_dipole_coordinates,
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
