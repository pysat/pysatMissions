
Tutorial
========

**Set up sgp4 with pysat**

The sgp4 instrument within pysatMissions is designed to be run like any pysat
instrument.  To access, use

.. code:: python

  import pysat
  from pysatMissions.instruments import pysat_sgp4

  sgp4 = pysat.Instrument(inst_module=pysat_sgp4)

For pysat 3.0.0 or greater, this can be permanently added via the instrument
registry.

.. code:: python

  import pysat
  import pysatMissions
  pysat.utils.registry.register('pysatMissions.instruments.pysat_sgp4')

or, to register all modules in pysat

.. code:: python

  import pysat
  import pysatMissions
  pysat.utils.registry.register_by_module(pysatMissions.instruments)


**Orbital Propagators**

Currently, two orbital propagators are included with pysatMissions. The
pysat_sgp4 instrument uses the wgs72 gravity model to provide satellite position
and velocity in ECI co-ordinates.  The pysat_ephem instrument uses the ephem
pysat package to calculate an orbit in lat/lon/alt and ECEF co-ordinates.  As
an example, it also loads a series of empirical models to provide simulated
magnetic data as an aid for mission planning.

The orbital propagators are activated by the load command, similar to any
pysat instrument.  To generate a simulated hour of orbital information with a
one-second cadence, run

.. code:: python

  sgp4 = pysat.Instrument('pysat', 'sgp4', num_samples=3600)
  sgp4.load(2019, 1)



**Empirical Models**

A number of methods are included to invoke several python wrappers for empirical
models.  This includes the aacgmv2, apexpy, and pysatMagVect models.  These
methods can be added to any pysat instrument using the `custom` functions in
pysat.

.. code:: python

  import pysat
  from pysatMissions.methods import magcoord

  ivm = pysat.Instrument(platform='cnofs', name='ivm')
  ivm.custom_attach(magcoord.add_aacgm_coordinates,
                    kwargs={'glat_label': 'glat',
                            'glong_label': 'glon',
                            'alt_label': 'altitude'})

Note that the latitude, longitude, and altitude variable names  of the
instrument must be specified since they are not identical to the default names
in the function.
