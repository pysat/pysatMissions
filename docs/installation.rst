
Installation
============

**Starting from scratch**

----

Python and associated packages for science are freely available. Convenient science python package setups are available from `Enthought <https://store.enthought.com>`_ and `Continuum Analytics <http://continuum.io/downloads>`_. Enthought also includes an IDE, though there are a number of choices. Core science packages such as numpy, scipy, matplotlib, pandas and many others may also be installed directly via pip or your favorite package manager.

For educational users, an IDE from `Jet Brains <https://www.jetbrains.com/student/>`_ is available for free.


**pysatMissions**

----

pysatMissions itself may be installed from a terminal command line via::

   pip install pysatMissions

Note that pysatMissions requires pysat to interact with the instruments and models here.  [Full Documentation for main package](http://pysat.readthedocs.io/en/latest/)

pysatMissions allows users to interact with a number of upper atmospheric empirical models through the pyglow package. However, pyglow currently requires manual install through git. While pysatMissions can be installed and used without pyglow, it should be installed by the user to access the pyglow methods. Please follow the install instructions at https://github.com/timduly4/pyglow.
