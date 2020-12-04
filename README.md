<div align="left">
        <img height="0" width="0px">
        <img width="20%" src="/poweredbypysat.png" alt="pysat" title="pysat"</img>
</div>

# pysatMissions
[![Documentation Status](https://readthedocs.org/projects/pysatMissions/badge/?version=latest)](http://pysatMissions.readthedocs.io/en/latest/?badge=latest)
[![DOI](https://zenodo.org/badge/209358908.svg)](https://zenodo.org/badge/latestdoi/209358908)

[![Build Status](https://travis-ci.com/pysat/pysatMissions.svg?branch=main)](https://travis-ci.com/pysat/pysatMissions)
[![Coverage Status](https://coveralls.io/repos/github/pysat/pysatMissions/badge.svg?branch=main)](https://coveralls.io/github/pysat/pysatMissions?branch=main)
[![Maintainability](https://api.codeclimate.com/v1/badges/83011911691b9d2076e9/maintainability)](https://codeclimate.com/github/pysat/pysatMissions/maintainability)

pysatMissions allows users to run build simulated satellites for Two-Line Elements (TLE) and add empirical data.  It includes the pysat_ephem and pysat_sgp4 instrument modules which can be imported into pysat.

Main Features
-------------
- Simulate satellite orbits from TLEs and add data from empirical models
- Import ionosphere and thermosphere model values through pyglow
- Import magnetic coordinates through apexpy and aacgmv2
- Import geomagnetic basis vectors through pysatMagVect

Documentation
---------------------
[Full Documentation for main package](http://pysat.readthedocs.io/en/latest/)


# Installation

One way to install is through pip.  Just type

```
pip install pysatMissions
```
into the terminal.

Or, if you prefer to work directly from github, checkout the repository:

```
git clone https://github.com/pysat/pysatMissions.git
```

Change directories into the repository folder and run the setup.py file.  For
a local install use the "--user" flag after "install".

```
cd pysatMissions/
python setup.py install
```

Note: pre-1.0.0 version
------------------
pysatMissions is currently in an initial development phase.  Much of the API is being built off of the upcoming pysat 3.0.0 software in order to streamline the usage and test coverage.  This version of pysat is planned for release later this year.  Currently, you can access the develop version of this through github:
```
git clone https://github.com/pysat/pysat.git
cd pysat
git checkout develop-3
python setup.py install
```
It should be noted that this is a working branch and is subject to change.

# Using with pysat

The instrument modules are portable and designed to be run like any pysat instrument.

```
import pysat
from pysatMissions.instruments import pysat_ephem

simInst = pysat.Instrument(inst_module=pysat_ephem)
```
