Install
=======

Without Users
-------------

This package can be installed without user authentication support:

1. Install `Anaconda 3 <https://www.anaconda.com/>`_ for Python
2. Install `PostgreSQL <https://www.postgresql.org/>`_ or your preferred database
3. Install ``msdss-data-api`` via pip or through a conda environment

.. code::

   conda create -n msdss-data-api python=3.8
   conda activate msdss-data-api
   pip install msdss-data-api[postgresql]

.. note::

   Optionally, you can also install other databases supported by ``sqlalchemy``:

   .. code::

      pip install msdss-data-api[mysql]
      pip install msdss-data-api[sqlite]

With Users
----------

This package can be installed with user authentication support:

1. Install `Anaconda 3 <https://www.anaconda.com/>`_ for Python
2. Install `PostgreSQL <https://www.postgresql.org/>`_ or your preferred database
3. Install ``msdss-data-api`` via pip or through a conda environment

.. code::

   conda create -n msdss-data-api python=3.8
   conda activate msdss-data-api
   pip install msdss-data-api[users-postgresql]

.. note::

   Optionally, you can also install other databases supported by ``sqlalchemy``:

   .. code::

      pip install msdss-data-api[users-mysql]
      pip install msdss-data-api[users-sqlite]