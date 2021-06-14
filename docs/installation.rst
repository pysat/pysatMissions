
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
Python 3.7+ and pysat 3.0.0+.

 ================ ==================
 Common  modules   Community modules
 ================ ==================
  numpy            apexpy
  pandas           aacgmv2
  pyEphem          OMMBV
  sgp4             pysat>=3.0
 ================ ==================


 Installation Options
 --------------------

 1. Clone the git repository
 ::


    git clone https://github.com/pysat/pysatMissions.git


 2. Install pysatMissions:
    Change directories into the repository folder and run the setup.py file.
    There are a few ways you can do this:

    A. Install on the system (root privileges required)::


         sudo python setup.py install

    B. Install at the user level::


         python setup.py install --user

    C. Install with the intent to develop locally::


         python setup.py develop --user
