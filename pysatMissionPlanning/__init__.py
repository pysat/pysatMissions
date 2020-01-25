from __future__ import print_function
from __future__ import absolute_import

import os
from pysatMissionPlanning import instruments
from pysatMissionPlanning import methods
from pysatMissionPlanning import plot

__all__ = ['instruments', 'methods', 'plot']

# set version
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'version.txt')) as version_file:
    __version__ = version_file.read().strip()
