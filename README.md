<div align="left">
        <img height="0" width="0px">
        <img width="20%" src="/poweredbypysat.png" alt="pysat" title="pysat"</img>
</div>

# pysatMissionPlanning
[![Build Status](https://travis-ci.org/pysat/pysatMissionPlanning.svg?branch=master)](https://travis-ci.org/pysat/pysatMissionPlanning)
[![Coverage Status](https://coveralls.io/repos/github/pysat/pysatMissionPlanning/badge.svg?branch=master)](https://coveralls.io/github/pysat/pysatMissionPlanning?branch=master)
[![DOI](https://zenodo.org/badge/209358908.svg)](https://zenodo.org/badge/latestdoi/209358908)

pysatMissionPlanning allows users to run build simulated satellites for TLE info and add empirical data.  It includes the pysat_sgp4 instrument module which can be imported into pysat.

Main Features
-------------
- Simulate satellite orbits from TLEs and add data from empirical models
- Import ionosphere and thermosphere values through pyglow
- Import coordidnates through apexpy

Documentation
---------------------
[Full Documentation for main package](http://pysat.readthedocs.io/en/latest/)


# Installation

First, checkout the repository:

```
  git clone https://github.com/pysat/pysatMissionPlanning.git
```

Change directories into the repository folder and run the setup.py file.  For
a local install use the "--user" flag after "install".

```
  cd pysatMissionPlanning/
  python setup.py install
```

# Using with pysat

The module is portable and designed to be run like any pysat instrument.

```
import pysat
from pysatMissionPlanning.instruments import pysat_sgp4

sgp4 = pysat.Instrument(inst_module=pysat_sgp4)
```
