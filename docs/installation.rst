
Installation
============

The following instructions will allow you to install pysatMissions.

Prerequisites
-------------

.. image:: figures/poweredbypysat.png
    :width: 150px
    :align: right
    :alt: powered by pysat Logo, blue planet with orbiting python and the logo superimposed


pysatMissions uses common Python modules, as well as modules developed by
and for the Space Physics community.  This module officially supports
Python 3.8+ and pysat 3.0.4+.

 ================ =================== ==================
 Common modules   Community modules   Optional Modules
 ================ =================== ==================
  numpy            pysat>=3.0.4        aacgmv2
  pandas           pyEphem             apexpy
                   sgp4>=2.7           OMMBV>=1.0
                   skyfield
 ================ =================== ==================


Installation Options
--------------------

 1. Clone the git repository
 ::


    git clone https://github.com/pysat/pysatMissions.git


 2. Install pysatMissions:
    Change directories into the repository folder and run the setup.py file.
    There are a few ways you can do this:

    A. Install on the system (root privileges required)::


         sudo pip install .

    B. Install at the user level::


         pip install --user .

    C. Install with the intent to develop locally::


         pip install -e --user .


.. _post-install:

Post Installation
-----------------

After installation, you may register the :py:mod:`pysatMissions`
:py:class:`Instrument` sub-modules with pysat.  If this is your first time using
pysat, check out the `quickstart guide
<https://pysat.readthedocs.io/en/latest/quickstart.html>`_ for pysat. Once pysat
is set up, you may choose to register the the :py:mod:`pysatMissions`
:py:class:`Instruments` sub-modules by:

.. code:: python


   import pysat
   import pysatMissions

   pysat.utils.registry.register_by_module(pysatMissions.instruments)

You may then use the pysat :py:attr:`platform` and :py:attr:`name` keywords to
initialize the model :py:class:`Instrument` instead of the
:py:attr:`inst_module` keyword argument.
