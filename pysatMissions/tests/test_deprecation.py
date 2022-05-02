"""Unit tests for deprecated methods and objects in pysatMissions."""

import numpy as np
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

    def eval_deprecation(self, warns, check_msgs, warn_type=DeprecationWarning):
        """Evaluate whether message is contained in DeprecationWarning.

        Parameters
        ----------
        warns : list
            List of warnings.WarningMessage objects
        check_msgs : list
            List of strings containing the expected warning messages
        warn_type : type
            Type for the warning messages (default=DeprecationWarning)

        """

        # TODO(#82): Remove when pysat 3.0.2 is released.  Replace with
        # pysat.utils.testing.eval_warnings

        # Ensure the minimum number of warnings were raised
        assert len(warns) >= len(check_msgs)

        # Initialize the output
        found_msgs = [False for msg in check_msgs]

        # Test the warning messages, ensuring each attribute is present
        for iwar in warns:
            for i, msg in enumerate(check_msgs):
                if str(iwar.message).find(msg) >= 0:
                    assert iwar.category == warn_type, \
                        "bad warning type for message: {:}".format(msg)
                    found_msgs[i] = True

        assert np.all(found_msgs), "did not find {:d} expected {:}".format(
            len(found_msgs) - np.sum(found_msgs), repr(warn_type))
        return

    def test_ephem_deprecation(self):
        """Test that instatiating missions_ephem will give DeprecationWarning."""

        with warnings.catch_warnings(record=True) as war:
            pysat.Instrument(inst_module=missions_ephem)

        warn_msgs = ["`missions_ephem` has been deprecated"]

        # TODO(#82): Replace with pysat.utils.testing.eval_warnings when pysat
        # 3.0.2 is released.

        self.eval_deprecation(war, warn_msgs)
        return
