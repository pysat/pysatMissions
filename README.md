<div align="left">
        <img height="0" width="0px">
        <img width="20%" src="/poweredbypysat.png" alt="pysat" title="pysat"</img>
</div>

# pysatMissions
[![Documentation Status](https://readthedocs.org/projects/pysatMissions/badge/?version=latest)](http://pysatMissions.readthedocs.io/en/latest/?badge=latest)
[![DOI](https://zenodo.org/badge/209358908.svg)](https://zenodo.org/badge/latestdoi/209358908)

[![Build Status](https://travis-ci.org/pysat/pysatMissions.svg?branch=master)](https://travis-ci.org/pysat/pysatMissions)
[![Coverage Status](https://coveralls.io/repos/github/pysat/pysatMissions/badge.svg?branch=master)](https://coveralls.io/github/pysat/pysatMissions?branch=master)
[![Maintainability](https://api.codeclimate.com/v1/badges/f795422173ac04203b24/maintainability)](https://codeclimate.com/github/pysat/pysatMissions/maintainability)

pysatMissions allows users to run build simulated satellites for TLE info and add empirical data.  It includes the pysat_ephem and pysat_sgp4 instrument modules which can be imported into pysat.

Main Features
-------------
- Simulate satellite orbits from TLEs and add data from empirical models
- Import ionosphere and thermosphere values through pyglow
- Import coordinates through apexpy
- Import magnetic coordinates through aacgmv2
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

A note on empirical models
--------------------------
pysatMissions allows users to interact with a number of upper atmospheric empirical models through the [pyglow](https://github.com/timduly4/pyglow) package.  However, pyglow currently requires manual install through git.  While pysatMissions can be installed and used without pyglow, it should be installed by the user to access the pyglow methods.  Please follow the install instructions at https://github.com/timduly4/pyglow.

# Using with pysat

The instrument modules are portable and designed to be run like any pysat instrument.

```
import pysat
from pysatMissions.instruments import pysat_ephem

simInst = pysat.Instrument(inst_module=pysat_ephem)
```

The methods that run empirical models can also be exported to any pysat instrument. For instance, to add thermal plasma predictions from the IRI model to the C/NOFS IVM instrument, one can invoke

```
import pysat
import pysatMissions.methods.pyglow as mm_glow

ivm = pysat.Instrument(platform='cnofs', name='ivm')
ivm.custom.add(mm_glow.add_iri_thermal_plasma, 'modify', glat_label='glat',
               glong_label='glon', alt_label='altitude')
```
Once the custom function is added, the model will automatically be run when the dataset is loaded.
