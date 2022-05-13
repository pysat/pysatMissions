<div align="left">
        <img height="0" width="0px">
        <img width="20%" src="https://raw.githubusercontent.com/pysat/pysatMissions/docs/figures/missions-draft-logo.jpeg" alt="pysat Missions logo - the python snakes dreaming of a spaceship" title="pysatMissions"</img>
</div>

# pysatMissions
[![Documentation Status](https://readthedocs.org/projects/pysatmissions/badge/?version=latest)](https://pysatmissions.readthedocs.io/en/latest/?badge=latest)
[![DOI](https://zenodo.org/badge/209358908.svg)](https://zenodo.org/badge/latestdoi/209358908)

[![Build Status](https://github.com/github/docs/actions/workflows/main.yml/badge.svg)](https://github.com/github/docs/actions/workflows/main.yml/badge.svg)
[![Coverage Status](https://coveralls.io/repos/github/pysat/pysatMissions/badge.svg?branch=main)](https://coveralls.io/github/pysat/pysatMissions?branch=main)
[![Maintainability](https://api.codeclimate.com/v1/badges/83011911691b9d2076e9/maintainability)](https://codeclimate.com/github/pysat/pysatMissions/maintainability)

pysatMissions allows users to run build simulated satellites for Two-Line Elements (TLE) and add empirical data.  It includes the missions_ephem and mission_sgp4 instrument modules which can be imported into pysat.

Main Features
-------------
- Simulate satellite orbits from TLEs and add data from empirical models
- Import magnetic coordinates through apexpy and aacgmv2
- Import geomagnetic basis vectors through OMMBV

Documentation
---------------------
[Full Documentation for main package](https://pysat.readthedocs.io/en/latest/)


# Installation

### Prerequisites

pysatMissions uses common Python modules, as well as modules developed by
and for the Space Physics community.  This module officially supports
Python 3.8+.  

| Common modules | Community modules |
| -------------- | ----------------- |
| numpy          | aacgmv2           |
| pandas         | apexpy            |
| pyEphem        | OMMBV>=1.0        |
| sgp4>=2.7      | pysat>=3.0        |


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
-----------------------
pysatMissions is currently in an initial development phase and requires pysat 3.0.0.  

# Using with pysat

The instrument modules are portable and designed to be run like any pysat instrument.

```
import pysat
from pysatMissions.instruments import missions_ephem

simInst = pysat.Instrument(inst_module=missions_ephem)
```
Another way to use the instruments in an external repository is to register the instruments.  This only needs to be done the first time you load an instrument.  Afterward, pysat will identify them using the `platform` and `name` keywords.

```
import pysat
import pysatMissions

pysat.utils.registry.register_by_module(pysatMissions.instruments)
simInst = pysat.Instrument('missions', 'ephem')
```
