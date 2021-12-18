Quick Start
===========

Without Users
-------------

After installing the package, set up database environment variables using ``msdss-dotenv`` in a command line terminal:

.. code::

    msdss-dotenv init --key_path <KEY_PATH>
    msdss-dotenv set MSDSS_DATABASE_DRIVER postgresql --key_path <KEY_PATH>
    msdss-dotenv set MSDSS_DATABASE_USER msdss --key_path <KEY_PATH>
    msdss-dotenv set MSDSS_DATABASE_PASSWORD msdss123 --key_path <KEY_PATH>
    msdss-dotenv set MSDSS_DATABASE_HOST localhost --key_path <KEY_PATH>
    msdss-dotenv set MSDSS_DATABASE_PORT 5432 --key_path <KEY_PATH>
    msdss-dotenv set MSDSS_DATABASE_NAME msdss --key_path <KEY_PATH>

.. note::

    Set the ``<KEY_PATH>`` to a secure location (preferable outside of the project directory) as you will need this to unlock your created ``.env`` file

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
   
    msdss-dotenv init --key_path <KEY_PATH>
    msdss-dotenv set MSDSS_USERS_COOKIE_SECRET cookie-secret --key_path <KEY_PATH>
    msdss-dotenv set MSDSS_USERS_JWT_SECRET jwt-secret --key_path <KEY_PATH>
    msdss-dotenv set MSDSS_USERS_RESET_PASSWORD_TOKEN_SECRET reset-phrase --key_path <KEY_PATH>
    msdss-dotenv set MSDSS_USERS_VERIFICATION_TOKEN_SECRET verification-phrase --key_path <KEY_PATH>

.. note::

    The variables above (e.g. ``cookie-secret``, ``jwt-secret``, etc) should be a strong passphrase - you can generate strong phrases with:
    
    .. code::

        openssl rand -hex 32

Then setup the database environment variables:

.. code::

    msdss-dotenv set MSDSS_DATABASE_DRIVER postgresql --key_path <KEY_PATH>
    msdss-dotenv set MSDSS_DATABASE_USER msdss --key_path <KEY_PATH>
    msdss-dotenv set MSDSS_DATABASE_PASSWORD msdss123 --key_path <KEY_PATH>
    msdss-dotenv set MSDSS_DATABASE_HOST localhost --key_path <KEY_PATH>
    msdss-dotenv set MSDSS_DATABASE_PORT 5432 --key_path <KEY_PATH>
    msdss-dotenv set MSDSS_DATABASE_NAME msdss --key_path <KEY_PATH>

.. note::

    Set the ``<KEY_PATH>`` to a secure location (preferable outside of the project directory) as you will need this to unlock your created ``.env`` file

Finally, create a ``superuser`` with the ``msdss-users`` command line interface:

.. code::

    msdss-users register --superuser

In Python, use the package via :class:`msdss_data_api.core.DataAPI`:

.. jupyter-execute::

    from msdss_data_api import DataAPI
    from msdss_users_api import UsersAPI

    # Create a users app
    users_api = UsersAPI()

    # Create app with users
    app = DataAPI(users_api)

    # Run the app with app.start()
    # API is hosted at http://localhost:8000
    # Try API at http://localhost:8000/docs
    # app.start()