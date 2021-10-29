"""Unit and Integration Tests for each instrument module.

Note
----
Imports test methods from pysat.tests.instrument_test_class

"""

import datetime as dt
import numpy as np
import tempfile
import warnings

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
        self.stime = pysatMissions.instruments.missions_sgp4._test_dates['']['']
        return

    def teardown_class(self):
        """Clean up downloaded files and parameters from tests."""

        pysat.params.data['data_dirs'] = self.saved_path
        self.tempdir.cleanup()
        del self.inst_loc, self.saved_path, self.tempdir, self.stime
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

        self.test_inst.load(date=self.stime)
        cadence = np.diff(self.test_inst.data.index.to_pydatetime())
        assert np.all(cadence == dt.timedelta(seconds=output))
        return

    @pytest.mark.parametrize(
        "kw_dict",
        [{'one_orbit': True},
         {'inclination': 13, 'alt_periapsis': 400, 'alt_apoapsis': 850,
          'bstar': 0, 'arg_periapsis': 0., 'raan': 0., 'mean_anomaly': 0.},
         {'TLE1': '1 25544U 98067A   18135.61844383  .00002728  00000-0  48567-4 0  9998',
          'TLE2': '2 25544  51.6402 181.0633 0004018  88.8954  22.2246 15.54059185113452'}
         ])
    def test_sgp4_options(self, kw_dict):
        """Test optional keywords for sgp4."""

        target = 'Fake Data to be cleared'
        self.test_inst = pysat.Instrument(
            inst_module=pysatMissions.instruments.missions_sgp4,
            **kw_dict)
        self.test_inst.data = [target]
        self.test_inst.load(date=self.stime)
        # If target is cleared, load has run successfully
        assert target not in self.test_inst.data
        return

    @pytest.mark.parametrize(
        "kw_dict",
        [{'inclination': 13, 'alt_apoapsis': 850},
         {'TLE1': '1 25544U 98067A   18135.61844383  .00002728  00000-0  48567-4 0  9998'}
         ])
    def test_sgp4_options_errors(self, kw_dict):
        """Test optional keyword combos for sgp4 that generate errors."""

        with pytest.raises(KeyError) as kerr:
            self.test_inst = pysat.Instrument(
                inst_module=pysatMissions.instruments.missions_sgp4,
                **kw_dict)
        assert str(kerr).find('Insufficient kwargs') >= 0
        return

    @pytest.mark.parametrize(
        "kw_dict",
        [{'inclination': 13, 'alt_periapsis': 400, 'alt_apoapsis': 850,
          'bstar': 0, 'arg_periapsis': 0., 'raan': 0., 'mean_anomaly': 0.,
          'TLE1': '1 25544U 98067A   18135.61844383  .00002728  00000-0  48567-4 0  9998',
          'TLE2': '2 25544  51.6402 181.0633 0004018  88.8954  22.2246 15.54059185113452'}
         ])
    def test_sgp4_options_warnings(self, kw_dict):
        """Test optional keyword combos for sgp4 that generate warnings."""

        with warnings.catch_warnings(record=True) as war:
            self.test_inst = pysat.Instrument(
                inst_module=pysatMissions.instruments.missions_sgp4,
                **kw_dict)
        assert len(war) >= 1
        categories = [war[j].category for j in range(0, len(war))]
        assert UserWarning in categories
        return
