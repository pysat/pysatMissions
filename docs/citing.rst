Citations in the pysat ecosystem
================================

When referring to this software package, please cite the original paper by Stoneback et al [2018] https://doi.org/10.1029/2018JA025297 as well as the package https://doi.org/10.5281/zenodo.3475498. Note that this doi will always point to the latest version of the code.  A list of dois for all versions can be found at the [zenodo page](https://zenodo.org/record/3475499).

Example for citation in BibTex for a generalized version:

.. code::

  @misc{pysatMissions,
    author       = {Stoneback, R.A. and
                    Klenzing, J.H. and
                    Burrell, A.G. and
                    Depew, M. and
                    Spence, C.},
    title        = {Pysat Mission Planning Toolkit (pysatMissions) vX.Y.Z},
    month        = oct,
    year         = 2019,
    doi          = {10.5281/zenodo.3475499},
    url          = {https://doi.org/10.5281/zenodo.3475499}
  }

Citing the publication:

.. code::

  @article{Stoneback2018,
    author    = {Stoneback, R. A. and
                 Burrell, A. G. and
                 Klenzing, J. and
                 Depew, M. D.},
    doi       = {10.1029/2018JA025297},
    issn      = {21699402},
    journal   = {Journal of Geophysical Research: Space Physics},
    number    = {6},
    pages     = {5271--5283},
    title     = {{PYSAT: Python Satellite Data Analysis Toolkit}},
    volume    = {123},
    year      = {2018}
  }

To aid in scientific reproducibility, please include the version number in publications that use this code.  This can be found by invoking `pysatMissions.__version__ `.
