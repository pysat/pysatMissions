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

        self.testInst = pysat.Instrument(platform='pysat', name='testing',
                                         num_samples=100, clean_level='clean')
        self.kwargs = {'glat_label': 'latitude',
                       'glong_label': 'longitude',
                       'alt_label': 'altitude'}
        self.reftime = dt.datetime(2009, 1, 1)
        return

    def teardown(self):
        """Clean up test environment after each method."""

        del self.testInst, self.kwargs, self.reftime
        return

    def eval_targets(self, targets):
        """Evaluate addition of new data targets to instrument."""

        for target in targets:
            assert target in self.testInst.data.keys(), \
                "{:s} not found in data".format(target)
            assert not np.isnan(self.testInst[target]).any(), \
                "NaN values found in {:s}".format(target)
            assert target in self.testInst.meta.data.index, \
                "{:s} not found in metadata".format(target)
        return

    @pytest.mark.parametrize("func,targets",
                             [('add_aacgm_coordinates',
                               ['aacgm_lat', 'aacgm_long', 'aacgm_mlt']),
                              ('add_quasi_dipole_coordinates',
                               ['qd_lat', 'qd_long', 'mlt'])])
    def test_add_coordinates(self, func, targets):
        """Test adding thermal plasma data to test inst."""

        self.testInst.custom_attach(getattr(mm_magcoord, func),
                                    kwargs=self.kwargs)
        self.testInst.load(date=self.reftime)
        self.eval_targets(targets)
        return
