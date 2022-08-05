"""Unit tests for pysatMissions utilitis."""

import warnings

import pytest

from pysatMissions.utils import package_check


class TestBasics(object):
    """Basic test for package utilities."""

    def setup(self):
        """Create a clean testing setup before each method."""

        warnings.simplefilter("always")
        return

    def teardown(self):
        """Clean up test environment after tests."""

        return

    @pytest.mark.parametrize("package_name, num_warns",
                             [('os', 0),
                              ('nonsense', 1)])
    def test_package_check(self, package_name, num_warns):
        """Test that package_check warns users if packages are not installed.

        Parameters
        ----------
        package_name : str
            Name of package to check for.
        num_warns : int
            Expected number of warnings to be generated.
        """

        @package_check(package_name)
        def dummy_func():
            """Pass through so that wrapper can be checked."""
            pass

        with warnings.catch_warnings(record=True) as war:
            dummy_func()

        assert len(war) == num_warns
        if len(war) > 0:
            assert package_name in str(war[0])

        return
