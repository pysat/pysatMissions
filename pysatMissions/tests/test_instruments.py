"""Unit and Integration Tests for each instrument module.

Note
----
Imports test methods from pysat.tests.instrument_test_class

"""

import datetime as dt
import numpy as np
import tempfile

import pytest

import pysat
# Make sure to import your instrument package here
# e.g.,
import pysatMissions

# Import the test classes from pysat
from pysat.tests.instrument_test_class import InstTestClass
from pysat.utils import generate_instrument_list


saved_path = pysat.params['data_dirs']

# Developers for instrument libraries should update the following line to
# point to their own subpackage location
# e.g.,
# instruments = generate_instrument_list(inst_loc=mypackage.inst)
instruments = generate_instrument_list(inst_loc=pysatMissions.instruments)

# The following lines apply the custom instrument lists to each type of test
method_list = [func for func in dir(InstTestClass)
               if callable(getattr(InstTestClass, func))]
# Search tests for iteration via pytestmark, update instrument list
for method in method_list:
    if hasattr(getattr(InstTestClass, method), 'pytestmark'):
        # Get list of names of pytestmarks
        n_args = len(getattr(InstTestClass, method).pytestmark)
        names = [getattr(InstTestClass, method).pytestmark[j].name
                 for j in range(0, n_args)]
        # Add instruments from your library
        if 'all_inst' in names:
            mark = pytest.mark.parametrize("inst_name", instruments['names'])
            getattr(InstTestClass, method).pytestmark.append(mark)
        elif 'download' in names:
            mark = pytest.mark.parametrize("inst_dict", instruments['download'])
            getattr(InstTestClass, method).pytestmark.append(mark)
        elif 'no_download' in names:
            mark = pytest.mark.parametrize("inst_dict",
                                           instruments['no_download'])
            getattr(InstTestClass, method).pytestmark.append(mark)


class TestInstruments(InstTestClass):
    """Main class for instrument tests.

    Note
    ----
    Uses class level setup and teardown so that all tests use the same
    temporary directory. We do not want to geneate a new tempdir for each test,
    as the load tests need to be the same as the download tests.

    """

    def setup_class(self):
        """Initialize the testing setup once before all tests are run."""

        # Make sure to use a temporary directory so that the user's setup is not
        # altered
        self.tempdir = tempfile.TemporaryDirectory()
        self.saved_path = pysat.params['data_dirs']
        pysat.params.data['data_dirs'] = [self.tempdir.name]
        # Developers for instrument libraries should update the following line
        # to point to their own subpackage location, e.g.,
        # self.inst_loc = mypackage.instruments
        self.inst_loc = pysatMissions.instruments
        return

    def teardown_class(self):
        """Clean up downloaded files and parameters from tests."""

        pysat.params.data['data_dirs'] = self.saved_path
        self.tempdir.cleanup()
        del self.inst_loc, self.saved_path, self.tempdir
        return

    # Custom package unit tests can be added here

    @pytest.mark.parametrize("inst_dict", [x for x in instruments['download']])
    @pytest.mark.parametrize("kwarg,output", [(None, 1), ('10s', 10)])
    def test_inst_cadence(self, inst_dict, kwarg, output):
        """Test operation of cadence keyword, including default behavior."""

        if kwarg:
            self.test_inst = pysat.Instrument(
                inst_module=inst_dict['inst_module'], cadence=kwarg)
        else:
            self.test_inst = pysat.Instrument(
                inst_module=inst_dict['inst_module'])

        self.test_inst.load(2019, 1)
        cadence = np.diff(self.test_inst.data.index.to_pydatetime())
        assert np.all(cadence == dt.timedelta(seconds=output))
        return
