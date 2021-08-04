# -*- coding: utf-8 -*-
"""Test some of the spacecraft method functions."""

import datetime as dt
import numpy as np
import pysat
from pysatMissions.methods import spacecraft as mm_sc


def add_eci(inst):
    """Add ECI position to pysat_testing instrument."""

    inst['position_ecef_x'] = [-6197.135721, -6197.066687, -6196.990263,
                               -6196.906991, -6196.816336, -6196.718347,
                               -6196.613474, -6196.501303, -6196.382257]
    inst['position_ecef_y'] = [-2169.334337, -2174.014920, -2178.693373,
                               -2183.368212, -2188.040895, -2192.711426,
                               -2197.378290, -2202.042988, -2206.703992]
    inst['position_ecef_z'] = [1716.528241, 1710.870004, 1705.209738,
                               1699.547245, 1693.882731, 1688.216005,
                               1682.547257, 1676.876312, 1671.203352]
    return


def add_fake_data(inst):
    """Add arbitrary vector to pysat_testing instrument."""

    inst['ax'] = np.ones(9)
    inst['ay'] = np.zeros(9)
    inst['az'] = np.zeros(9)
    return


class TestBasics():
    """Unit tests for aacgmv2 methods."""

    def setup(self):
        """Create a clean testing setup before each method."""

        self.testInst = pysat.Instrument(platform='pysat', name='testing',
                                         num_samples=9, clean_level='clean')
        self.testInst.custom_attach(add_eci)
        return

    def teardown(self):
        """Clean up test environment after tests."""

        del self
        return

    def test_calculate_ecef_velocity(self):
        """Test `calculate_ecef_velocity` helper function."""

        self.testInst.custom_attach(mm_sc.calculate_ecef_velocity)
        self.testInst.load(date=dt.datetime(2009, 1, 1))
        targets = ['velocity_ecef_x', 'velocity_ecef_y', 'velocity_ecef_z']
        for target in targets:
            # Check if data is added
            assert target in self.testInst.data.keys()
            assert not np.isnan(self.testInst[target][1:-1]).any()
            # Endpoints should be NaN
            assert np.isnan(self.testInst[target][0])
            assert np.isnan(self.testInst[target][-1])
            # Check if metadata is added
            assert target in self.testInst.meta.data.index
        return

    def test_add_ram_pointing_sc_attitude_vectors(self):
        """Test `add_ram_pointing_sc_attitude_vectors` helper function."""

        # TODO: check if calculations are correct
        self.testInst.custom_attach(mm_sc.calculate_ecef_velocity)
        self.testInst.custom_attach(mm_sc.add_ram_pointing_sc_attitude_vectors)
        self.testInst.load(date=dt.datetime(2009, 1, 1))
        targets = ['sc_xhat_ecef_x', 'sc_xhat_ecef_y', 'sc_xhat_ecef_z',
                   'sc_yhat_ecef_x', 'sc_yhat_ecef_y', 'sc_yhat_ecef_z',
                   'sc_zhat_ecef_x', 'sc_zhat_ecef_y', 'sc_zhat_ecef_z']
        for target in targets:
            # Check if data is added
            assert target in self.testInst.data.keys()
            assert not np.isnan(self.testInst[target][1:-1]).any()
            # Endpoints should be NaN
            assert np.isnan(self.testInst[target][0])
            assert np.isnan(self.testInst[target][-1])
            # Check if metadata is added
            assert target in self.testInst.meta.data.index
        return

    def test_project_ecef_vector_onto_sc(self):
        """Test `project_ecef_vector_onto_sc` helper function."""

        # TODO: check if calculations are correct
        self.testInst.custom_attach(mm_sc.calculate_ecef_velocity)
        self.testInst.custom_attach(mm_sc.add_ram_pointing_sc_attitude_vectors)
        self.testInst.custom_attach(add_fake_data)
        self.testInst.custom_attach(mm_sc.project_ecef_vector_onto_sc,
                                    args=['ax', 'ay', 'az', 'bx', 'by', 'bz'])
        self.testInst.load(date=dt.datetime(2009, 1, 1))
        targets = ['bx', 'by', 'bz']
        for target in targets:
            # Check if data is added
            assert target in self.testInst.data.keys()
            assert not np.isnan(self.testInst[target][1:-1]).any()
            # Endpoints should be NaN
            assert np.isnan(self.testInst[target][0])
            assert np.isnan(self.testInst[target][-1])
            # Check if metadata is added
            assert target in self.testInst.meta.data.index
        return
