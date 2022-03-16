"""Core library for pysatMissions.

pysatMissions allows users to run build simulated satellites for Two-Line
Elements (TLE) and add empirical data.  It includes the `missions_ephem` and
`mission_sgp4` instrument modules which can be imported into pysat.

Main Features
-------------
- Simulate satellite orbits from TLEs and add data from empirical models
- Import magnetic coordinates through apexpy and aacgmv2
- Import geomagnetic basis vectors through OMMBV

"""

import logging
import os

try:
    from pysatMissions import instruments
    from pysatMissions import methods
except ImportError as errstr:
    logging.exception('problem importing pysatMissions: ' + str(errstr))

__all__ = ['instruments', 'methods']

# set version
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'version.txt')) as version_file:
    __version__ = version_file.read().strip()
