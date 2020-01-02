<div align="left">
        <img height="0" width="0px">
        <img width="20%" src="/poweredbypysat.png" alt="pysat" title="pysat"</img>
</div>

# pysatMissionPlanning
[![Build Status](https://travis-ci.org/pysat/pysatMissionPlanning.svg?branch=master)](https://travis-ci.org/pysat/pysatMissionPlanning)
[![Documentation Status](https://readthedocs.org/projects/pysatMissionPlanning/badge/?version=latest)](http://pysatMissionPlanning.readthedocs.io/en/latest/?badge=latest)
[![Coverage Status](https://coveralls.io/repos/github/pysat/pysatMissionPlanning/badge.svg?branch=master)](https://coveralls.io/github/pysat/pysatMissionPlanning?branch=master)
[![DOI](https://zenodo.org/badge/209358908.svg)](https://zenodo.org/badge/latestdoi/209358908)

[![Maintainability](https://api.codeclimate.com/v1/badges/f795422173ac04203b24/maintainability)](https://codeclimate.com/github/pysat/pysatMissionPlanning/maintainability)

pysatMissionPlanning allows users to run build simulated satellites for TLE info and add empirical data.  It includes the pysat_ephem and pysat_sgp4 instrument modules which can be imported into pysat.

Main Features
-------------
- Simulate satellite orbits from TLEs and add data from empirical models
- Import ionosphere and thermosphere values through pyglow
- Import coordinates through apexpy
- Import magnetic coordinates through aacgmv2

Documentation
---------------------
[Full Documentation for main package](http://pysat.readthedocs.io/en/latest/)


# Installation

One way to install is through pip.  Just type

```
pip install pysatMissionPlanning
```
into the terminal.

Or, if you prefer to work directly from github, checkout the repository:

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

The instrument modules are portable and designed to be run like any pysat instrument.

```
import pysat
from pysatMissionPlanning.instruments import pysat_ephem

simInst = pysat.Instrument(inst_module=pysat_ephem)
```

The methods that run empirical models can also be exported to any pysat instrument. For instance, to add thermal plasma predictions from the IRI model to the C/NOFS IVM instrument, one can invoke

```
import pysat
import pysatMissionPlanning.methods.pyglow as methglow

ivm = pysat.Instrument(platform='cnofs', name='ivm')
ivm.custom.add(methglow.add_iri_thermal_plasma, 'modify')
```
Once the custom function is added, the model will automatically be run when the dataset is loaded.
