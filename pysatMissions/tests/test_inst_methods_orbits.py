"""Unit tests for `pysatMissions.instruments.methods.orbits`."""

import pytest
import pysatMissions.instruments.methods.orbits as mm_orbits


class TestBasics():
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
        assert abs(ecc - self.orbit['eccentricity']) / ecc < 1.e-6
        assert abs(mm - self.orbit['mean_motion']) / mm < 1.e-6
        return

    def test_convert_from_keplerian(self):
        """Test conversion from keplerian elements."""
        per, apo, = mm_orbits.convert_from_keplerian(self.orbit['eccentricity'],
                                                     self.orbit['mean_motion'],)
        assert abs(per - self.orbit['perigee']) / per < 1.e-6
        assert abs(apo - self.orbit['apogee']) / apo < 1.e-6
        return
