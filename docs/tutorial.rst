
Tutorial
========

**Set up sgp4 with pysat**

The sgp4 instrument within pysatMissions is designed to be run like any pysat instrument.  To access, use

.. code:: python

  import pysat
  from pysatMissions.instruments import pysat_sgp4

  sgp4 = pysat.Instrument(inst_module=pysat_sgp4)

For pysat 3.0.0 or greater, this can be permanently added via the instrument registry.

.. code:: python

  import pysat
  import pysatMissions
  pysat.utils.registry.register('pysatMissions.instruments.pysat_sgp4')

**Orbital Propagators**

Currently, two orbital propagators are included with pysatMissions. The pysat_sgp4 instrument uses the wgs72 gravity model to provide satellite position and velocity in ECI co-ordinates.  The pysat_ephem instrument uses the ephem pysat package to calculate an orbit in lat/lon/alt and ECEF co-ordinates.  As an example, it also loads a series of empirical models to provide simulated ionospheric, thermospheric, and magnetic data as an aid for mission planning.

**Empirical Models**

A number of methods are included to invoke several python wrappers for empirical models.  This includes the aacgmv2, apexpy, and pyglow models.  These methods can be added to any pysat instrument in order to compare.  These can be added using the `custom` functions in pysat.

.. code:: python

  import pysat
  from pysatMissions.methods import empirical

  ivm = pysat.Instrument(platform='cnofs', name='ivm')
  ivm.custom.attach(empirical.add_iri_thermal_plasma, 'modify', 'end', glat_label='glat', glong_label='glon', alt_label='altitude')

Note that in this case, the latitude, longitude, and altitude variable names of the instrument must be specified since they are not identical to the default names in the function.

**References**

`aacgmv2 <https://github.com/aburrell/aacgmv2>`_ is a python library for accessing the Altitude-Adjusted Corrected Geomagnetic (AACGM) coordinates.

* Baker, K. B., & Wing, S. (1989). A new magnetic coordinate system for conjugate studies at high latitudes. Journal ofGeophysical Research, 94, 9139–9143.
* Shepherd, S. G. (2014). Altitude−adjusted corrected geomagnetic coordinates: Definition and functional approximations. Journal of Geophysical Research: Space Physics, 119, 7501–7521. https://doi.org/10.1002/2014JA020264

`apexpy <https://github.com/aburrell/apexpy>`_ is a python library for calculating magnetic apex coordinates.

* Richmond, A. D. (1995). Ionospheric electrodynamics using magnetic apex coordinates. Journal ofGeomagnetism and Geoelectricity, 47(2), 191–212.
* Emmert, J. T., Richmond, A. D., & Drob, D. P. (2010). A computationally compact representation of magnetic-apex and quasi-dipole coordinates with smooth base vectors. Journal ofGeophysical Research, 115, A08322. https://doi.org/10.1029/2010JA015326
* Laundal, K. M., & Richmond, A. D. (2017). Magnetic coordinate systems. Space Science Reviews, 206, 27–59

`pyglow <https://github.com/timduly4/pyglow>`_ is a python package wrapping multiple empirical models:

Horizontal Wind Model (HWM)

* Hedin, A. E., Schmidlin, F. J., Fleming, E. L., Avery, S. K., Manson, A. H., & Franke, S. J. (1993). Empirical wind model for the middle and lower atmosphere—Part 1: Local time average. https://ntrs.nasa.gov/archive/nasa/casi.ntrs.nasa.gov/19930015971.pdf
* Hedin, A. E., Fleming, E. L., Manson, A. H., Schmidlin, F. J., Avery, S. K., Clark, R. R., et al. (1993). Empirical wind model for the middle and lower atmosphere—Part 2: Local time variations (NASA Technical Memorandum 104592) Greenbelt, MD: Goddard Space Flight Center. https://ntrs.nasa.gov/archive/nasa/casi.ntrs.nasa.gov/19940017389.pdf
* Drob, D. P., Emmert, J. T., Crowley, G., Picone, J. M., Shepherd, G. G., Skinner, W., et al. (2008). An empirical model of the Earth’s horizontal wind fields: HWM07. Journal ofGeophysical Research, 113, A12304. https://doi.org/10.1029/2008JA013668
* Drob, D. P., Emmert, J. T., Meriwether, J. W., Makela, J. J., Doornbos, E., Conde, M., et al. (2015). An update to the Horizontal Wind Model (HWM): The quiet time thermosphere. Earth and Space Science, 2, 301–319. https://doi.org/10.1002/2014EA000089

International Geomagnetic Reference Field (IGRF)

* Thébault, E., Finlay, C. C., & Toh, H. (2015). Special issue “international geomagnetic reference field—The twelfth generation”. Earth, Planets and Space, 67(1), 158. https://doi.org/10.1186/s40623-015-0313-0

International Reference Ionosphere (IRI)

* Bilitza, D., Altadill, D., Truhlik, V., Shubin, V., Galkin, I., Reinisch, B., & Huang, X. (2017). International Reference Ionosphere 2016: From ionospheric climate to real-time weather predictions. Space Weather, 15, 418–429. https://doi.org/10.1002/2016SW001593
* Bilitza, D., Altadill, D., Zhang, Y., Mertens, C., Truhlik, V., Richards, P., et al. (2014). The International Reference Ionosphere 2012—A model of international collaboration. Journal ofSpace Weather and Space Climate, 4, A07.

Naval Research Laboratory Mass Spectrometer Incoherent Scatter radar Exobase (NRLMSISE)

* Picone, J. M. (2002). NRLMSISE-00 empirical model of the atmosphere: Statistical comparisons and scientific issues. Journal ofGeophysical Research, 107(A12), 1468–SIA 15–16.
