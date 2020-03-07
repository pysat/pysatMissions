from __future__ import print_function
from __future__ import absolute_import
import logging
import os

try:
    from pysatMissions import instruments
    from pysatMissions import methods
    from pysatMissions import plot
except ImportError as errstr:
    logging.exception('problem importing pysatMissions: ' + str(errstr))

__all__ = ['instruments', 'methods', 'plot']

# set version
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'version.txt')) as version_file:
    __version__ = version_file.read().strip()
