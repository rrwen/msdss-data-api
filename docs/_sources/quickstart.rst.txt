Quick Start
===========

Without Users
-------------

After installing the package, set up database environment variables using ``msdss-dotenv`` in a command line terminal:

.. code::

    msdss-dotenv set MSDSS_DATABASE_DRIVER postgresql
    msdss-dotenv set MSDSS_DATABASE_USER msdss
    msdss-dotenv set MSDSS_DATABASE_PASSWORD msdss123
    msdss-dotenv set MSDSS_DATABASE_HOST localhost
    msdss-dotenv set MSDSS_DATABASE_PORT 5432
    msdss-dotenv set MSDSS_DATABASE_NAME msdss

In Python, use the package via :class:`msdss_data_api.core.DataAPI`:

.. jupyter-execute::

    from msdss_data_api import DataAPI

    # Create app using env vars
    app = DataAPI()

    # Run the app with app.start()
    # API is hosted at http://localhost:8000
    # Try API at http://localhost:8000/docs
    # app.start()

With Users
----------

After installing the package, set up user environment variables using ``msdss-dotenv`` in a command line terminal:

.. code::
   
   msdss-dotenv init
   msdss-dotenv set MSDSS_USERS_SECRET secret-phrase
   msdss-dotenv set MSDSS_USERS_JWT_SECRET secret-phrase-02

.. note::

    You can generate a strong ``secret-phrase`` and ``secret-phrase-02`` with: 
    
    .. code::

        openssl rand -hex 32

Then setup the database environment variables:

.. code::

    msdss-dotenv set MSDSS_DATABASE_DRIVER postgresql
    msdss-dotenv set MSDSS_DATABASE_USER msdss
    msdss-dotenv set MSDSS_DATABASE_PASSWORD msdss123
    msdss-dotenv set MSDSS_DATABASE_HOST localhost
    msdss-dotenv set MSDSS_DATABASE_PORT 5432
    msdss-dotenv set MSDSS_DATABASE_NAME msdss

In Python, use the package via :class:`msdss_data_api.core.DataAPI`:

.. jupyter-execute::

    from msdss_data_api import DataAPI

    # Create app using env vars
    app = DataAPI(enable_users=True)

    # Run the app with app.start()
    # API is hosted at http://localhost:8000
    # Try API at http://localhost:8000/docs
    # app.start()