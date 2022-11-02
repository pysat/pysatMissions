"""Unit tests for deprecated methods and objects in pysatMissions."""

import warnings

import pysat
from pysatMissions.instruments import missions_ephem


class TestDeprecation(object):
    """Unit tests for deprecations."""

    def setup_method(self):
        """Create a clean testing setup before each method."""

        warnings.simplefilter("always", DeprecationWarning)
        return

    def teardown_method(self):
        """Clean up test environment after each method."""
        return

    def test_ephem_deprecation(self):
        """Test that instatiating missions_ephem will give DeprecationWarning."""

        with warnings.catch_warnings(record=True) as war:
            pysat.Instrument(inst_module=missions_ephem)

        warn_msgs = ["`missions_ephem` has been deprecated"]

        pysat.utils.testing.eval_warnings(war, warn_msgs)
        return
