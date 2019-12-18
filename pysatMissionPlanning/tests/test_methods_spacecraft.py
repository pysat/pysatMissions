# -*- coding: utf-8 -*-
# Test some of the spacecraft method functions

import numpy as np
import pysat
from pysatMissionPlanning.methods import spacecraft as methsc


def add_eci(inst):
    """Add ECI position to pysat_testing instrument"""

    inst['position_ecef_x'] = [-6197.135721, -6197.066687, -6196.990263,
                               -6196.906991, -6196.816336, -6196.718347,
                               -6196.613474, -6196.501303, -6196.382257]
    inst['position_ecef_y'] = [-2169.334337, -2174.014920, -2178.693373,
                               -2183.368212, -2188.040895, -2192.711426,
                               -2197.378290, -2202.042988, -2206.703992]
    inst['position_ecef_z'] = [1716.528241, 1710.870004, 1705.209738,
                               1699.547245, 1693.882731, 1688.216005,
                               1682.547257, 1676.876312, 1671.203352]


class TestBasics():
    def setup(self):
        """Runs before every method to create a clean testing setup."""
        self.testInst = pysat.Instrument(platform='pysat', name='testing',
                                         sat_id='9', clean_level='clean')
        self.testInst.custom.add(add_eci, 'modify')

    def teardown(self):
        """Clean up test environment after tests"""
        del self

    def test_calculate_ecef_velocity(self):
        self.testInst.custom.add(methsc.calculate_ecef_velocity, 'modify')
        self.testInst.load(date=pysat.datetime(2009, 1, 1))
        targets = ['velocity_ecef_x', 'velocity_ecef_y', 'velocity_ecef_z']
        for target in targets:
            # Check if data is added
            assert target in self.testInst.data.keys()
            assert not np.isnan(self.testInst[target][1:-1]).any()
            # Endpoints hsould be NaN
            assert np.isnan(self.testInst[target][0])
            assert np.isnan(self.testInst[target][-1])
            # Check if metadata is added
            assert target in self.testInst.meta.data.index
