
Tutorial
========

Set up sgp4 with pysat
----------------------

The :ref:`missions_sgp4` instrument within pysatMissions is designed to be run
like any pysat instrument.  To access, use

.. code:: python

  import pysat
  from pysatMissions.instruments import missions_sgp4

  sgp4 = pysat.Instrument(inst_module=missions_sgp4)

This can be permanently added via the instrument registry.

.. code:: python

  import pysat
  import pysatMissions
  pysat.utils.registry.register('pysatMissions.instruments.missions_sgp4')

or, to register all modules in pysat

.. code:: python

  import pysat
  import pysatMissions
  pysat.utils.registry.register_by_module(pysatMissions.instruments)


For other instruments, simply replace the module name (in this case, missions_sgp4)
with the name of the desired instrument.

Orbital Propagators
-------------------

Currently, two orbital propagators are included with pysatMissions. The
:ref:`missions_sgp4` instrument uses the wgs72 gravity model to provide satellite
position and velocity in ECI coordinates.  The :ref:`missions_ephem` instrument
uses the ephem pysat package to calculate an orbit in lat/lon/alt and ECEF
coordinates.  As an example, it also loads a series of empirical models to
provide simulated magnetic data as an aid for mission planning.

The orbital propagators are activated by the load command, similar to any
pysat instrument.  To generate a simulated hour of orbital information with a
one-second cadence, run

.. code:: python

  sgp4 = pysat.Instrument(inst_module=missions_sgp4, num_samples=3600)
  sgp4.load(2019, 1)



Empirical Models
----------------

A number of methods are included to invoke several python wrappers for empirical
models.  This includes the aacgmv2, apexpy, and OMMBV models.  These
methods can be added to any pysat instrument using the `custom` functions in
pysat.  The example below adds the aacgmv2 coordinates to sgp4 instrument.

.. code:: python

  import pysat
  from pysatMissions.methods import magcoord

  sgp4 = pysat.Instrument(inst_module=missions_sgp4, num_samples=3600)
  sgp4.custom_attach(magcoord.add_aacgm_coordinates,
                     kwargs={'glat_label': 'geod_latitude',
                             'glong_label': 'geod_longitude',
                             'alt_label': 'geod_altitude'})
  sgp4.load(2019, 1)

Note that the latitude, longitude, and altitude variable names of the
instrument should be specified since the dataset may use different variable
names from those in the custom function.  The method to add these empirical
functions to a pysat instrument is identical across the pysat ecosystem.
