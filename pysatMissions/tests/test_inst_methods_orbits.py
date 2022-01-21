"""Unit tests for `pysatMissions.instruments.methods.orbits`."""

import pysatMissions.instruments.methods.orbits as mm_orbits
import pytest


class TestBasics(object):
    """Unit tests for conversion to/from Keplerian elements."""

    def setup(self):
        """Create a clean testing setup before each method."""

        self.orbit = {'inclination': 13, 'apogee': 850, 'perigee': 400,
                      'eccentricity': 0.032160315599897085,
                      'mean_motion': 0.06474416985702029}
        return

    def teardown(self):
        """Clean up test environment after each method."""

        del self.orbit
        return

    def eval_output(self, value, label):
        """Evaluate output value from calculations."""

        assert abs(value - self.orbit[label]) / value < 1.e-6
        return

    def test_convert_wrong_planet(self):
        """Test conversion routines with an unsupported planet."""

        with pytest.raises(KeyError) as kerr:
            mm_orbits.convert_to_keplerian(self.orbit['perigee'],
                                           self.orbit['apogee'], 'Hwae')
        assert str(kerr).find("is not yet a supported planet!") >= 0
        return

    def test_convert_to_keplerian(self):
        """Test conversion to keplerian elements."""

        ecc, mm, = mm_orbits.convert_to_keplerian(self.orbit['perigee'],
                                                  self.orbit['apogee'],)
        self.eval_output(ecc, 'eccentricity')
        self.eval_output(mm, 'mean_motion')
        return

    def test_convert_from_keplerian(self):
        """Test conversion from keplerian elements."""

        per, apo, = mm_orbits.convert_from_keplerian(self.orbit['eccentricity'],
                                                     self.orbit['mean_motion'],)
        self.eval_output(per, 'perigee')
        self.eval_output(apo, 'apogee')
        return
