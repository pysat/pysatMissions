
Tutorial
========

**Set up sgp4 with pysat**

----
The sgp4 instrument within pysatMissionPlanning is designed to be run like any pysat instrument.  To access, use

.. code:: python

  import pysat
  from pysatMissionPlanning.instruments import pysat_sgp4

  sgp4 = pysat.Instrument(inst_module=pysat_sgp4)

For pysat 3.0.0 or greater, this can be permanently added via the instrument registry.

.. code:: python

  import pysat
  import pysatMissionPlanning
  pysat.utils.registry.register('pysatMissionPlanning.instruments.pysat_sgp4')

**Orbital Propagators***

---
Currently, two orbital propagators are included with pysatMissionPlanning. The pysat_sgp4 instrument uses the wgs72 gravity model to provide satellite position and velocity in ECI co-ordinates.  The pysat_ephem instrument uses the ephem pysat package to calculate an orbit in lat/lon/alt and ECEF co-ordinates.  As an example, it also loads a series of empirical models to provide simulated ionospheric, thermospheric, and magnetic data as an aid for mission planning.

**Empirical Models**

---
A number of methods are included to invoke several python wrappers for empirical models.  This includes the aacgmv2, apexpy, and pyglow models.  These methods can be added to any pysat instrument in order to compare.  These can be added using the `custom` functions in pysat.

.. code:: python

  import pysat
  from pysatMissionPlanning.methods import pyglow as methglow

  ivm = pysat.Instrument(platform='cnofs', name='ivm')
  ivm.custom.add(methglow.add_iri_thermal_plasma, 'modify', 'end', 'glat', 'glon', 'altitude')

Note that in this case, the latitude, longitude, and altitude variable names of the instrument must be specified since they are not identical to the default names in the function.
