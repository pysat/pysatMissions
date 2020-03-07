
Installation
============

**Starting from scratch**

----

Python and associated packages for science are freely available. Convenient science python package setups are available from https://www.python.org/ and `Anaconda <https://www.anaconda.com/distribution/>`_. Anaconda also includes a developer environment. Core science packages such as numpy, scipy, matplotlib, pandas and many others may also be installed directly via pip or your favorite package manager.

For educational users, developer environments from `Jet Brains <https://www.jetbrains.com/student/>`_ are available for free.


**pysatMissions**

----

pysatMissions itself may be installed from a terminal command line via:

.. code-block:: console

   pip install pysatMissions

Note that pysatMissions requires pysat to interact with the instruments and models here.  [Full Documentation for main package](http://pysat.readthedocs.io/en/latest/)


**Note: pre-1.0.0 version**

----

pysatMissions is currently in an initial development phase.  Much of the API is being built off of the upcoming pysat 3.0.0 software in order to streamline the usage and test coverage.  This version of pysat is planned for release later this year.  Currently, you can access the develop version of this through github:

.. code-block:: console

   git clone https://github.com/pysat/pysat.git
   cd pysat
   git checkout develop-3
   python setup.py install

It should be noted that this is a working branch and is subject to change.

**A note on empirical models**

----

pysatMissions allows users to interact with a number of upper atmospheric empirical models through the pyglow package. However, pyglow currently requires manual install through git. While pysatMissions can be installed and used without pyglow, it should be installed by the user to access the pyglow methods. Please follow the install instructions at https://github.com/timduly4/pyglow.
