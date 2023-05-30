# -*- coding: utf-8 -*-
"""Test some of the spacecraft method functions."""

import datetime as dt
import numpy as np
import warnings

import pysat
from pysatMissions.methods import spacecraft as mm_sc


def add_ecef(inst):
    """Add ECEF position to pysat_testing instrument."""

    # Maintain each as unit vector to simplify checks.
    inst['position_ecef_x'] = [0.0, 0.0, 0.0, 1.0, 1.0, 0.0]
    inst['position_ecef_y'] = [1.0, 0.0, 0.0, 0.0, 0.0, 1.0]
    inst['position_ecef_z'] = [0.0, 1.0, 1.0, 0.0, 0.0, 0.0]
    return


def add_ecef_vel(inst):
    """Add ECEF velocity to pysat_testing instrument."""

    # Maintain each as unit vector to simplify checks.
    inst['velocity_ecef_x'] = [1.0, 1.0, 0.0, 0.0, 0.0, 0.0]
    inst['velocity_ecef_y'] = [0.0, 0.0, 1.0, 1.0, 0.0, 0.0]
    inst['velocity_ecef_z'] = [0.0, 0.0, 0.0, 0.0, 1.0, 1.0]
    return


def add_fake_data(inst):
    """Add an arbitrary vector to a pysat_testing instrument."""

    inst['ax'] = np.ones(6)
    inst['ay'] = np.zeros(6)
    inst['az'] = np.zeros(6)
    return


class TestBasics(object):
    """Unit tests for aacgmv2 methods."""

    def setup_method(self):
        """Create a clean testing setup before each method."""

        self.testInst = pysat.Instrument(platform='pysat', name='testing',
                                         num_samples=6, clean_level='clean',
                                         use_header=True)
        self.testInst.custom_attach(add_ecef)
        self.reftime = dt.datetime(2009, 1, 1)
        return

    def teardown_method(self):
        """Clean up test environment after tests."""

        del self.testInst, self.reftime
        return

    def eval_targets(self, targets):
        """Evaluate addition of new data targets to instrument."""

        for target in targets:
            assert target in self.testInst.data.keys(), \
                "{:s} not found in data".format(target)
            # By default, endpoints will be NaNs.  Ignore these.
            assert not np.isnan(self.testInst[target][1:-1]).any(), \
                "NaN values found in {:s}".format(target)
            assert target in self.testInst.meta.data.index, \
                "{:s} not found in metadata".format(target)
        return

    def test_calculate_ecef_velocity(self):
        """Test `calculate_ecef_velocity` helper function."""

        self.testInst.custom_attach(mm_sc.calculate_ecef_velocity)
        self.testInst.load(date=self.reftime)
        targets = ['velocity_ecef_x', 'velocity_ecef_y', 'velocity_ecef_z']
        self.eval_targets(targets)
        return

    def test_calculate_ecef_velocity_deprecation(self):
        """Test `calculate_ecef_velocity` helper function."""

        self.testInst.custom_attach(mm_sc.calculate_ecef_velocity)
        warnings.simplefilter("always", DeprecationWarning)
        with warnings.catch_warnings(record=True) as war:
            self.testInst.load(date=self.reftime)
        warn_msgs = ["`calculate_ecef_velocity` has been deprecated"]

        pysat.utils.testing.eval_warnings(war, warn_msgs)
        return

    def test_add_ram_pointing_sc_attitude_vectors(self):
        """Test `add_ram_pointing_sc_attitude_vectors` helper function."""

        self.testInst.custom_attach(add_ecef_vel)
        self.testInst.custom_attach(mm_sc.add_ram_pointing_sc_attitude_vectors)
        self.testInst.load(date=self.reftime)

        # Xhat vector should match velocity
        assert np.all(self.testInst['sc_xhat_ecef_x']
                      == self.testInst['velocity_ecef_x'])
        assert np.all(self.testInst['sc_xhat_ecef_y']
                      == self.testInst['velocity_ecef_y'])
        assert np.all(self.testInst['sc_xhat_ecef_z']
                      == self.testInst['velocity_ecef_z'])

        # Zhat vector should match - position
        assert np.all(self.testInst['sc_zhat_ecef_x']
                      == -self.testInst['position_ecef_x'])
        assert np.all(self.testInst['sc_zhat_ecef_y']
                      == -self.testInst['position_ecef_y'])
        assert np.all(self.testInst['sc_zhat_ecef_z']
                      == -self.testInst['position_ecef_z'])

        # Yhat vector should be orthogonal
        assert np.all(self.testInst['sc_yhat_ecef_x']
                      == [0.0, 0.0, 1.0, 0.0, 0.0, -1.0])
        assert np.all(self.testInst['sc_yhat_ecef_y']
                      == [0.0, -1.0, 0.0, 0.0, 1.0, 0.0])
        assert np.all(self.testInst['sc_yhat_ecef_z']
                      == [1.0, 0.0, 0.0, -1.0, 0.0, 0.0])
        return

    def test_project_ecef_vector_onto_sc(self):
        """Test `project_ecef_vector_onto_sc` helper function."""

        self.testInst.custom_attach(add_ecef_vel)
        self.testInst.custom_attach(mm_sc.add_ram_pointing_sc_attitude_vectors)
        self.testInst.custom_attach(add_fake_data)
        self.testInst.custom_attach(mm_sc.project_ecef_vector_onto_sc,
                                    args=['ax', 'ay', 'az', 'bx', 'by', 'bz'])
        self.testInst.load(date=self.reftime)

        assert np.all(self.testInst['bx'] == [1.0, 1.0, 0.0, 0.0, 0.0, 0.0])
        assert np.all(self.testInst['by'] == [0.0, 0.0, 1.0, 0.0, 0.0, -1.0])
        assert np.all(self.testInst['bz'] == [0.0, 0.0, 0.0, -1.0, -1.0, 0.0])
        return
