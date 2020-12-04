# -*- coding: utf-8 -*-
"""
Basic test of the instrument objects in pysatMissions

To be replaced once pysat testing techniques are finalized
"""

import datetime as dt
import numpy as np
import pysat


class TestSGP4():
    def setup(self):
        """Runs before every method to create a clean testing setup."""
        from pysatMissions.instruments import pysat_sgp4
        self.testInst = pysat.Instrument(inst_module=pysat_sgp4, inst_id='100')
        self.targets1 = ['position_eci_x', 'position_eci_y', 'position_eci_z',
                         'velocity_eci_x', 'velocity_eci_y', 'velocity_eci_z']
        self.targets2 = []

    def teardown(self):
        """Clean up test environment after tests"""
        del self

    def test_basic_instrument_load(self):
        """Checks if instrument loads proper data and metadata"""
        # Check if instrument is instrument
        assert isinstance(self.testInst, pysat._instrument.Instrument)

        self.testInst.load(date=dt.datetime(2018, 1, 1))
        # Check for completeness of first set of targets
        for target in self.targets1:
            # Check if data is added
            assert target in self.testInst.data.keys()
            assert not np.isnan(self.testInst[target]).any()
            # Check if metadata is added
            assert target in self.testInst.meta.data.index
        # Check for completeness of second set of targets
        for target in self.targets2:
            # Check if data is added
            assert target in self.testInst.data.keys()
            # First and last values are NaN if related to velocity
            assert not np.isnan(self.testInst[target][1:-1]).any()
            assert np.isnan(self.testInst[target][0])
            assert np.isnan(self.testInst[target][-1])
            # Check if metadata is added
            assert target in self.testInst.meta.data.index


class TestEphem(TestSGP4):
    def setup(self):
        """Runs before every method to create a clean testing setup."""
        # NOTE: aacgm not checked here because undefined near the equator
        # TODO: add check for aacgm values
        from pysatMissions.instruments import pysat_ephem
        self.testInst = pysat.Instrument(inst_module=pysat_ephem, tag='all',
                                         inst_id='100')
        self.targets1 = ['glong', 'glat', 'alt', 'obs_sat_slant_range',
                         'obs_sat_az_angle', 'obs_sat_el_angle',
                         'position_ecef_x', 'position_ecef_y', 'position_ecef_z',
                         'qd_lat', 'qd_long', 'mlt']
        self.targets2 = ['velocity_ecef_x', 'velocity_ecef_y', 'velocity_ecef_z',
                         'sc_xhat_ecef_x', 'sc_xhat_ecef_y', 'sc_xhat_ecef_z',
                         'sc_yhat_ecef_x', 'sc_yhat_ecef_y', 'sc_yhat_ecef_z',
                         'sc_zhat_ecef_x', 'sc_zhat_ecef_y', 'sc_zhat_ecef_z']

    def teardown(self):
        """Clean up test environment after tests"""
        del self
