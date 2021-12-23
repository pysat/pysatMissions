"""Unit tests for deprecated methods an objects in pysatMissions."""

import warnings

import pysat
from pysatMissions.instruments import missions_ephem


class TestDeprecation(object):
    """Unit tests for deprecations."""

    def setup(self):
        """Create a clean testing setup before each method."""

        warnings.simplefilter("always", DeprecationWarning)
        return

    def teardown(self):
        """Clean up test environment after each method."""
        return

    def eval_deprecation(self, warns, check_msgs):
        """Evaluate whether message is contained in DeprecationWarning.

        Parameters
        ----------
        warns : list
            List of warnings.WarningMessage objects
        check_msgs : list
            List of strings containing the expected warning messages

        """

        # Ensure the minimum number of warnings were raised
        assert len(warns) >= len(check_msgs)

        # Test the warning messages, ensuring each attribute is present
        pysat.utils.testing.eval_warnings(warns, check_msgs)
        return

    def test_ephem_deprecation(self):
        """Test that instatiating missions_ephem will give DeprecationWarning."""

        with warnings.catch_warnings(record=True) as war:
            pysat.Instrument(inst_module=missions_ephem)

        warn_msgs = ["`missions_ephem` has been deprecated"]

        self.eval_deprecation(war, warn_msgs)
        return
