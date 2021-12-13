import inspect
import os

from fastapi import FastAPI
from msdss_base_api import API
from msdss_base_database import Database
from msdss_base_dotenv import env_exists, load_env_file

from .routers import *
from .handlers import *

try:
    from msdss_users_api import UsersAPI
except ImportError:
    pass

class DataAPI(API):
    """
    Class for creating Data APIs.
    
    Parameters
    ----------
    users_api : :class:`msdss_users_api:msdss_users_api.core.UsersAPI` or None
        Users API object to enable user authentication for data routes.
        If ``None``, user authentication will not be used for data routes.
    database : :class:`msdss_base_database:msdss_base_database.core.Database`
        A :class:`msdss_base_database:msdss_base_database.core.Database` object for managing data.
    data_router_settings : dict
        Additional arguments passed to :func:`msdss_data_api.routers.get_data_router` except ``database``.
    api : :class:`fastapi:fastapi.FastAPI`
        API object for creating routes.
    *args, **kwargs
        Additional arguments passed to :class:`msdss_base_api:msdss_base_api.core.API`.

    Attributes
    ----------
    data_api_database : :class:`msdss_base_datbase:msdss_base_database.core.Database`
        Database object used for the data API.

    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>
    
    Example
    -------
    Create Data API without users:

    .. jupyter-execute::

        from msdss_base_database import Database
        from msdss_data_api import DataAPI
        from msdss_users_api import UsersAPI

        # Create database object
        database = Database(
            driver='postgresql',
            user='msdss',
            password='msdss123',
            host='localhost',
            port='5432',
            database='msdss'
        )

        # Create a data api without users
        app = DataAPI(database=database)

    Create Data API with users:

    .. jupyter-execute::

        from msdss_base_database import Database
        from msdss_data_api import DataAPI
        from msdss_users_api import UsersAPI

        # Create database object
        database = Database(
            driver='postgresql',
            user='msdss',
            password='msdss123',
            host='localhost',
            port='5432',
            database='msdss'
        )

        # Create a data api with users
        # CHANGE SECRETS TO STRONG PHRASES
        users_api = UsersAPI(
            'cookie-secret',
            'jwt-secret',
            'reset-secret',
            'verification-secret',
            database=database
        )
        app = DataAPI(users_api, database=database)

        # Add users routes
        app.add_apps(users_api)

        # Run the app with app.start()
        # Try API at http://localhost:8000/docs
        # app.start()
    """
    def __init__(
        self,
        users_api=None,
        database=Database(),
        data_router_settings={},
        api=FastAPI(
            title='MSDSS Data API',
            version='0.2.5'
        ),
        *args, **kwargs):
        super().__init__(api=api, *args, **kwargs)

        # (DataAPI_settings) Setup router params
        data_router_settings['database'] = database
        
        # (DataAPI_users) Add users app if specified
        if users_api:
            data_router_settings['users_api'] = users_api
        
        # (DataAPI_router_data) Add data router
        data_router = get_data_router(**data_router_settings)
        self.add_router(data_router)

        # (DataAPI_attr) Set attributes
        self.data_api_database = database
        