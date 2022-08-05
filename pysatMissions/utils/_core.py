"""Utilities for pysatMissions."""

from importlib import import_module
import warnings


def package_check(package_name):
    """Throw a warning if package is not installed.

    Some systems are having issues installing OMMBV and apexpy.
    This allows these packages to be optionally installed.

    """

    def decorator(func):
        """Pass the function through to the wrapper."""

        def wrapper(*args, **kwargs):
            """Wrap functions that use the decorator function."""

            message_warn = ' '.join(['{:} must be installed'.format(package_name),
                                     'to use {:}.'.format(func.__name__),
                                     'See instructions at',
                                     'https://github.com/pysat/pysatMissions'])
            try:
                import_module(package_name)
            except ModuleNotFoundError:
                # Triggered if package is not installed
                warnings.warn(message_warn, stacklevel=2)

        return wrapper

    return decorator
