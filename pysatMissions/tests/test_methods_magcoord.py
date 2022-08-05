# -*- coding: utf-8 -*-
"""Test some of the aacgmv2 method functions."""

import datetime as dt
import numpy as np

import pytest

import pysat
import pysatMissions.methods.magcoord as mm_magcoord


class TestBasics(object):
    """Main testing class for aacgmv2."""

    def setup(self):
        """Create a clean testing setup before each method."""

        self.test_inst = pysat.Instrument(platform='pysat', name='testing',
                                          num_samples=100, clean_level='clean',
                                          use_header=True)
        self.kwargs = {'glat_label': 'latitude',
                       'glong_label': 'longitude',
                       'alt_label': 'altitude'}
        self.reftime = dt.datetime(2009, 1, 1)
        return

    def teardown(self):
        """Clean up test environment after each method."""

        del self.test_inst, self.kwargs, self.reftime
        return

    def eval_targets(self, targets):
        """Evaluate addition of new data targets to instrument."""

        for target in targets:
            assert target in self.test_inst.data.keys(), \
                "{:s} not found in data".format(target)
            assert not np.isnan(self.test_inst[target]).any(), \
                "NaN values found in {:s}".format(target)
            assert target in self.test_inst.meta.data.index, \
                "{:s} not found in metadata".format(target)
        return

    @pytest.mark.parametrize("func,targets",
                             [('add_aacgm_coordinates',
                               ['aacgm_lat', 'aacgm_long', 'aacgm_mlt']),
                              ('add_quasi_dipole_coordinates',
                               ['qd_lat', 'qd_long', 'mlt'])])
    def test_add_coordinates(self, func, targets):
        """Test adding thermal plasma data to test inst."""

        self.test_inst.custom_attach(getattr(mm_magcoord, func),
                                     kwargs=self.kwargs)
        self.test_inst.load(date=self.reftime)
        self.eval_targets(targets)
        return
