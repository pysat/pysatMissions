# -*- coding: utf-8 -*-
"""
Basic test of the instrument objects in pysatMissionPlanning

To be replaced once pysat testing techniques are finalized
"""

import numpy as np
import pysat


class TestSGP4():
    def setup(self):
        """Runs before every method to create a clean testing setup."""
        from pysatMissionPlanning.instruments import pysat_sgp4
        self.testInst = pysat.Instrument(inst_module=pysat_sgp4)
        self.targets = ['position_eci_x', 'position_eci_y', 'position_eci_z',
                        'velocity_eci_x', 'velocity_eci_y', 'velocity_eci_z']

    def teardown(self):
        """Clean up test environment after tests"""
        del self

    def test_basic_instrument_load(self):
        """Checks if instrument loads proper data and metadata"""
        self.testInst.load(date=pysat.datetime(2018, 1, 1))
        for target in self.targets:
            # Check if data is added
            assert target in self.testInst.data.keys()
            assert not np.isnan(self.testInst[target]).any()
            # Check if metadata is added
            assert target in self.testInst.meta.data.index


class TestEphem(TestSGP4):
    def setup(self):
        """Runs before every method to create a clean testing setup."""
        from pysatMissionPlanning.instruments import pysat_ephem
        self.testInst = pysat.Instrument(inst_module=pysat_ephem)
        self.targets = ['glong', 'glat', 'alt', 'obs_sat_slant_range',
                        'obs_sat_az_angle', 'obs_sat_el_angle',
                        'position_ecef_x', 'position_ecef_y', 'position_ecef_z',
                        'aacgm_lat', 'aacgm_long', 'aacgm_mlt',
                        'qd_lat', 'qd_long', 'mlt',
                        'e_temp', 'frac_dens_h', 'frac_dens_he', 'frac_dens_o',
                        'ion_dens', 'ion_temp',
                        'B', 'B_east', 'B_north', 'B_up', 'B_ecef_x',
                        'B_ecef_y', 'B_ecef_z',
                        'Nn', 'Nn_N', 'Nn_N2', 'Nn_O', 'Nn_O2', 'Tn_msis',
                        'total_wind_x', 'total_wind_y', 'total_wind_z',
                        'sim_wind_sc_x', 'sim_wind_sc_y', 'sim_wind_sc_z']

    def teardown(self):
        """Clean up test environment after tests"""
        del self
