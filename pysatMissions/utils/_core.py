"""Utilities for pysatMissions."""

from functools import wraps
import warnings


def package_check(package_name):
    """Throw a warning if optional package is not installed.

    Some systems are having issues installing OMMBV and apexpy.
    This allows these packages to be optionally installed.

    Parameters
    ----------
    package_name : str
        Name of the package to check in a given function.  If not present, a
        warning is raised and the original function is skipped.

    """

    def decorator(func):
        """Pass the function through to the wrapper."""

        @wraps(func)
        def wrapper(*args, **kwargs):
            """Wrap functions that use the decorator function."""

            message_warn = ' '.join(['{:} must be installed'.format(package_name),
                                     'to use {:}.'.format(func.__name__),
                                     'See instructions at',
                                     'https://github.com/pysat/pysatMissions'])
            try:
                func(*args, **kwargs)
            except NameError as nerr:
                # Triggered if call is made to package that is not installed
                if package_name in str(nerr):
                    warnings.warn(message_warn, stacklevel=2)
                else:
                    # Error is unrelated to optional package, raise original.
                    raise nerr

        return wrapper

    return decorator
