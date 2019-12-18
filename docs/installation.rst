
Installation
============

**Starting from scratch**

----

Python and associated packages for science are freely available. Convenient science python package setups are available from `Enthought <https://store.enthought.com>`_ and `Continuum Analytics <http://continuum.io/downloads>`_. Enthought also includes an IDE, though there are a number of choices. Core science packages such as numpy, scipy, matplotlib, pandas and many others may also be installed directly via pip or your favorite package manager.

For educational users, an IDE from `Jet Brains <https://www.jetbrains.com/student/>`_ is available for free.


**pysatMissionPlanning**

----

PysatMissionPLanning itself may be installed from a terminal command line via::

   pip install pysatMissionPlanning

Note that pysatMissionPlanning requires pysat to interact with the instruments and models here.  [Full Documentation for main package](http://pysat.readthedocs.io/en/latest/)

**Set up sgp4 with pysat**

----
The sgp4 instrument within pysatMissionPlanning is designed to be run like any pysat instrument.  To access, use

.. code:: python

  import pysat
  from pysatMissionPlanning.instruments import pysat_sgp4

  sgp4 = pysat.Instrument(inst_module=pysat_sgp4)

For pysat 3.0.0 or greater, invoking this the first time will permanently add this instrument to the user's library, and it can be accessed in the future simply by calling it like any pysat instrument without having to load the pysatMissionPlanning library separately.

.. code:: python

  import pysat
  sgp4 = pysat.Instrument(platform='pysat', name='sgp4')
