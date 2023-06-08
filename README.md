<div align="left">
        <img height="0" width="0px">
        <img width="20%" src="https://raw.githubusercontent.com/pysat/pysatMissions/main/docs/figures/missions-draft-logo.jpeg" alt="pysat Missions logo - the python snakes dreaming of a spaceship" title="pysatMissions"</img>
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
- Import magnetic coordinates through apexpy and aacgmv2 (optional install)

Documentation
---------------------
[Full Documentation for main package](https://pysat.readthedocs.io/en/latest/)


# Installation

### Prerequisites

pysatMissions uses common Python modules, as well as modules developed by
and for the Space Physics community.  This module officially supports
Python 3.8+.  

| Common modules | Community modules | Optional modules |
| -------------- | ----------------- | ---------------- |
| numpy          | pysat>=3.0.4      | aacgmv2          |
| pandas         | pyEphem           | apexpy           |
|                | sgp4>=2.7         | OMMBV            |
|                | skyfield          |                  |


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
pip install .
```

Note: pre-1.0.0 version
-----------------------
pysatMissions is currently in an initial development phase and requires pysat
3.0.4.  

# Using with pysat

The instrument modules are portable and designed to be run like any pysat
instrument.

```
import pysat
from pysatMissions.instruments import missions_sgp4

sim_inst = pysat.Instrument(inst_module=missions_sgp4)
```
Another way to use the instruments in an external repository is to register the instruments.  This only needs to be done the first time you load an instrument.  Afterward, pysat will identify them using the `platform` and `name` keywords.

```
import pysat
import pysatMissions

pysat.utils.registry.register_by_module(pysatMissions.instruments)
sim_inst = pysat.Instrument('missions', 'sgp4')
```

# Optional modules

Magnetic vector coordinates through apexpy and aacgmv2 are set up as optional
installs. Both packages require fortran to install properly, and may require
additional configuration.  Both can be installed from pip, but may require the
`--no-binary` option depending on your system.

The instrument `missions_ephem` has been deprecated since pyEphem is no longer
maintained. This will be removed in v0.4.0.  Note that OMMBV is required for
this instrument to function correctly, but is not required for the core
pysatMissions package.  This has also been made optional to improve installation.  
Please use the `missions_sgp4` instrument for future needs.

The orbital trajectories can be calculated without any of the optional modules.
