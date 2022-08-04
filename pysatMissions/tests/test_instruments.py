"""Unit and Integration Tests for each instrument module.

Note
----
Imports test methods from pysat.tests.instrument_test_class

"""

import datetime as dt
import numpy as np
import warnings

import pytest

import pysat
# Make sure to import your instrument package here
# e.g.,
import pysatMissions

# Import the test classes from pysat
from pysat.tests.classes import cls_instrument_library as clslib


# Developers for instrument libraries should update the following line to
# point to their own subpackage location
# e.g.,
# instruments = generate_instrument_list(inst_loc=mypackage.inst)
instruments = clslib.InstLibTests.initialize_test_package(
    clslib.InstLibTests, inst_loc=pysatMissions.instruments)


class TestInstruments(clslib.InstLibTests):
    """Main class for instrument tests.

    Note
    ----
    Uses class level setup and teardown so that all tests use the same
    temporary directory. We do not want to geneate a new tempdir for each test,
    as the load tests need to be the same as the download tests.

    """

    @pytest.mark.parametrize("kwargs",
                             [{},
                              {'inclination': 20, 'alt_periapsis': 400},
                              {'inclination': 80, 'alt_periapsis': 500,
                               'alt_apoapsis': 600,
                               'epoch': dt.datetime(2019, 1, 1)}])
    def test_sgp4_data_continuity(self, kwargs):
        """Test that data is continuous for sequential days.

        Parameters
        ----------
        kwargs : dict
            Optional kwargs to pass through.  If empty, instrument will be
            default TLEs.

        """

        # Define sat with custom Keplerian inputs
        sat = pysat.Instrument(
            inst_module=pysatMissions.instruments.missions_sgp4,
            **kwargs)

        # Get last 10 points of day 1
        sat.load(2018, 1)
        day1 = sat.data[-10:]

        # Get first 10 points of day 2
        sat.load(2018, 2)
        day2 = sat.data[:10]

        average_gradient = day1.diff().mean()
        std_gradient = day1.diff().std()
        gradient_between_days = day2.iloc[0] - day1.iloc[-1]

        # Check that the jump between days is within 3 sigma of average gradient
        del_g = np.abs(average_gradient - gradient_between_days)
        assert np.all(del_g < (3. * std_gradient)), \
            "Gap between days outside of 3 sigma"

        return

    @pytest.mark.parametrize("inst_dict", [x for x in instruments['download']])
    @pytest.mark.parametrize("in_cad,out_cad,num_samples",
                             [(None, 1, 86400), ('10s', 10, 8640)])
    def test_inst_cadence(self, inst_dict, in_cad, out_cad, num_samples):
        """Test operation of cadence keyword, including default behavior.

        Parameters
        ----------
        in_cad : pds.freq or NoneType
            Input cadence as a frequency string
        out_cad : int
            Expected output cadence in seconds
        num_samples : int
            Expected output num_samples.  Only valid for sgp4 instrument.

        """

        if in_cad:
            self.test_inst = pysat.Instrument(
                inst_module=inst_dict['inst_module'], cadence=in_cad)
        else:
            self.test_inst = pysat.Instrument(
                inst_module=inst_dict['inst_module'])

        self.test_inst.load(date=self.stime)
        cadence = np.diff(self.test_inst.data.index.to_pydatetime())
        assert np.all(cadence == dt.timedelta(seconds=out_cad))

        if self.test_inst.name == 'sgp4':
            assert len(self.test_inst.data) == num_samples

        return

    @pytest.mark.parametrize(
        "kw_dict",
        [{'one_orbit': True},
         {'inclination': 13, 'alt_periapsis': 400, 'alt_apoapsis': 850,
          'bstar': 0, 'arg_periapsis': 0., 'raan': 0., 'mean_anomaly': 0.},
         {'tle1': '1 25544U 98067A   18135.61844383  .00002728  00000-0  48567-4 0  9998',
          'tle2': '2 25544  51.6402 181.0633 0004018  88.8954  22.2246 15.54059185113452'}
         ])
    def test_sgp4_options(self, kw_dict):
        """Test optional keywords for sgp4.

        Parameters
        ----------
        kw_dict : dict
            Dictionary of kwargs to pass through to the sgp4 instrument.

        """

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
         {'tle1': '1 25544U 98067A   18135.61844383  .00002728  00000-0  48567-4 0  9998'}
         ])
    def test_sgp4_options_errors(self, kw_dict):
        """Test optional keyword combos for sgp4 that generate errors.

        Parameters
        ----------
        kw_dict : dict
            Dictionary of kwargs to pass through to the sgp4 instrument.

        """

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
          'tle1': '1 25544U 98067A   18135.61844383  .00002728  00000-0  48567-4 0  9998',
          'tle2': '2 25544  51.6402 181.0633 0004018  88.8954  22.2246 15.54059185113452'}
         ])
    def test_sgp4_options_warnings(self, kw_dict):
        """Test optional keyword combos for sgp4 that generate warnings.

        Parameters
        ----------
        kw_dict : dict
            Dictionary of kwargs to pass through to the sgp4 instrument.

        """

        with warnings.catch_warnings(record=True) as war:
            self.test_inst = pysat.Instrument(
                inst_module=pysatMissions.instruments.missions_sgp4,
                **kw_dict)
        assert len(war) >= 1
        categories = [war[j].category for j in range(0, len(war))]
        assert UserWarning in categories
        return
