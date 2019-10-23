from __future__ import print_function
from __future__ import absolute_import

import os
from pysatMissionPlanning import instruments

__all__ = ['instruments']

# set version
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'version.txt')) as version_file:
    __version__ = version_file.read().strip()
