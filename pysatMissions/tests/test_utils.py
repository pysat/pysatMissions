"""Unit tests for pysatMissions utilitis."""

from importlib import import_module
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
    def test_package_check_warns(self, package_name, num_warns):
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
            """Try importing a package, simulate a NameError if not found."""
            try:
                import_module(package_name)
            except ModuleNotFoundError:
                raise NameError('{:} not found'.format(package_name))
            return

        with warnings.catch_warnings(record=True) as war:
            dummy_func()

        assert len(war) == num_warns
        if len(war) > 0:
            assert package_name in str(war[0])

        return

    def test_package_check_error(self):
        """Test that package_check raises error for unrelated errors."""

        @package_check('nonsense')
        def dummy_func():
            """Simulate an unrelated NameError."""
            raise NameError('A sensible error has occurred')
            return

        with pytest.raises(NameError) as nerr:
            dummy_func()

        assert 'sensible' in str(nerr)

        return
