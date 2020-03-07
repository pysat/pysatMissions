# Change Log
All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).

## [0.2.0] - 2020-03-07
- Renamed as pysatMissions
- Added method files to access aacgmv2, apexpy, pyglow for any pysat instrument
- Added method for spacecraft to handle attitude and coordinates
- Added method for plotting simulated data
- Added support for readthedocs
- Updates to testing environment
- Split pysat_sgp4 into pysat_sgp4 and pysat_ephem to allow different propagators
- Removed basemap
- Added numeric strings as options for sat_id
- Added `_get_times` to streamline time steps for simulated instruments
- Bugs
  - Fixed wrong metadata name for mlt in apexpy

## [0.1.1] - 2019-10-22
- pypi compatibility
- Add DOI badge

## [0.1.0] - 2019-10-07
- Initial release
