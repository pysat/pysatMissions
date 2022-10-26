"""Core library for pysatMissions.

pysatMissions allows users to run build simulated satellites for Two-Line
Elements (TLE) and add empirical data.  It includes the `missions_ephem` and
`mission_sgp4` instrument modules which can be imported into pysat.

Main Features
-------------
- Simulate satellite orbits from TLEs and add data from empirical models
- Import magnetic coordinates through apexpy and aacgmv2

"""

import pkg_resources

from pysatMissions import instruments
from pysatMissions import methods
from pysatMissions import utils

__all__ = ['instruments', 'methods', 'utils']

# set version
__version__ = pkg_resources.get_distribution('pysatMissions').version
