# Change Log
All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](https://semver.org/).

## [0.3.1] - 2022-05-18
* Include license in package manifest

## [0.3.0] - 2022-05-13
* Add Keplerian orbital inputs into missions_sgp4
* Update sgp4 interface to use new syntax for initialization from TLEs
* Include conversions to geodetic latitude / longitude / altitude for sgp4
* Improve metadata generation in missions_sgp4
* Update syntax to be compliant with OMMBV 1.0
* Documentation
  * Improve docstrings throughout
  * Added bypass for apexpy for readthedocs build
* Deprecations
  * Deprecated missions_ephem, as pyephem will no longer be updated
* Testing
  * Add style check for docstrings
  * Added checks for deprecation warnings
  * Improve checks in codeclimate

## [0.2.2] - 2021-06-18
* Migrate pyglow interface to pysatIncubator
* Style updates for consistency with pysat 3.0
  * Use `inst_id` instead of `sat_id`
  * Use `cadence` instead of `freq`
  * Use 'missions' as the platform name ('pysat' now reserved for core code)
* Migrate CI testing to Github Actions
* Use OMMBV instead of pysatMagVect

## [0.2.1] - 2020-07-29
* Use conda to manage Travis CI environment
* Updated style to be compliant with pandas 2.0 and pysat 3.0
  * Import datetime from datetime
  * import DataFrame and Series from pandas rather than pysat
* Rename default branch as `main`

## [0.2.0] - 2020-03-07
* Renamed as pysatMissions
* Added method files to access aacgmv2, apexpy, pyglow for any pysat instrument
* Added method for spacecraft to handle attitude and coordinates
* Added method for plotting simulated data
* Added support for readthedocs
* Updates to testing environment
* Split pysat_sgp4 into pysat_sgp4 and pysat_ephem to allow different propagators
* Removed basemap
* Added numeric strings as options for sat_id
* Added `_get_times` to streamline time steps for simulated instruments
* Bugs
  * Fixed wrong metadata name for mlt in apexpy

## [0.1.1] - 2019-10-22
* pypi compatibility
* Add DOI badge

## [0.1.0] - 2019-10-07
* Initial release
