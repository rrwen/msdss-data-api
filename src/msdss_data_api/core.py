import inspect
import os

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
    driver : str
        The driver name of the database connection, which are commonly ``postgresql``, ``sqlite``, ``mysql``, ``oracle`` or ``mssql``.  (see `SQLAlchemy supported databases <https://docs.sqlalchemy.org/en/14/core/engines.html#supported-databases>`_).
    user : str
        User name for the connection.
    password : str
        Password for the user.
    host : str
        Host address of the connection.
    port : str
        Port number of the connection.
    database : str
        Database name of the connection.
    enable_data_router : bool
        Whether to include the data api router.
    enable_users : bool
        Whether to include the users router, which enables route protection for data routes. See :class:`msdss_users_api:msdss_users_api.core.UsersAPI`.
    data_router_kwargs : dict
        Additional arguments passed to :func:`msdss_data_api.routers.get_data_router`.
    users_kwargs : dict
        Additional arguments passed to :class:`msdss_users_api:msdss_users_api.core.UsersAPI` if ``enable_users`` is ``True``. 

        * Note that any arguments with the same names as :class:`msdss_users_api:msdss_users_api.core.UsersAPI` will also be passed to it - however anything defined in this parameter will take priority

    get_current_user_kwargs : dict
        Additional arguments passed to the :meth:`msdss_users_api.msdss_users_api.core.UsersAPI.get_current_user` function for all data routes if ``enable_users`` is ``True``.
    create_get_current_user_kwargs : dict
        Additional arguments passed to the :meth:`msdss_users_api.msdss_users_api.core.UsersAPI.get_current_user` function for the data create route if ``enable_users`` is ``True``. The default is to only allow superusers to access this route.
    delete_get_current_user_kwargs : dict
        Additional arguments passed to the :meth:`msdss_users_api.msdss_users_api.core.UsersAPI.get_current_user` function for the data delete route if ``enable_users`` is ``True``. The default is to only allow superusers to access this route.
    id_get_current_user_kwargs : dict
        Additional arguments passed to the :meth:`msdss_users_api.msdss_users_api.core.UsersAPI.get_current_user` function for the data id route if ``enable_users`` is ``True``. The default is to only allow users to access this route.
    insert_get_current_user_kwargs : dict
        Additional arguments passed to the :meth:`msdss_users_api.msdss_users_api.core.UsersAPI.get_current_user` function for the data insert route if ``enable_users`` is ``True``. The default is to only allow superusers to access this route.
    metadata_get_current_user_kwargs : dict
        Additional arguments passed to the :meth:`msdss_users_api.msdss_users_api.core.UsersAPI.get_current_user` function for the data insert route if ``enable_users`` is ``True``. The default is to only allow users to access this route.
    metadata_update_get_current_user_kwargs : dict
        Additional arguments passed to the :meth:`msdss_users_api.msdss_users_api.core.UsersAPI.get_current_user` function for the data insert route if ``enable_users`` is ``True``. The default is to only allow superusers to access this route.
    query_get_current_user_kwargs : dict
        Additional arguments passed to the :meth:`msdss_users_api.msdss_users_api.core.UsersAPI.get_current_user` function for the data query route if ``enable_users`` is ``True``. The default is to only allow users to access this route.
    search_get_current_user_kwargs : dict
        Additional arguments passed to the :meth:`msdss_users_api.msdss_users_api.core.UsersAPI.get_current_user` function for the data search route if ``enable_users`` is ``True``. The default is to only allow users to access this route.
    update_get_current_user_kwargs : dict
        Additional arguments passed to the :meth:`msdss_users_api.msdss_users_api.core.UsersAPI.get_current_user` function for the data update route if ``enable_users`` is ``True``. The default is to only allow users to access this route.
    load_env : bool
        Whether to load variables from a file with environmental variables at ``env_file`` or not.
    env_file : str
        The path of the file with environmental variables.
    key_path : str
        The path of the key file for the ``env_file``.
    driver_key : str
        The environmental variable name for ``driver``.
    user_key : str
        The environmental variable name for ``user``.
    password_key : str
        The environmental variable name for ``password``.
    host_key : str
        The environmental variable name for ``key``.
    port_key : str
        The environmental variable name for ``port``.
    database_key : str
        The environmental variable name for ``database``.

    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>
    
    Example
    -------
    .. jupyter-execute::

        from msdss_data_api import DataAPI

        # Create a data api without users
        app = DataAPI(
            driver='postgresql',
            user='msdss',
            password='msdss123',
            host='localhost',
            port='5432',
            database='msdss'
        )

        # Create a data api with users
        # NOTE: Change parameter secret to a more secure value
        app = DataAPI(
            driver='postgresql',
            user='msdss',
            password='msdss123',
            host='localhost',
            port='5432',
            database='msdss',
            enable_users=True,
            users_kwargs={
                'secret': 'CHANGE-THIS'
            }
        )

        # Run the app with app.start()
        # Try API at http://localhost:8000/docs
        # app.start()
    """
    def __init__(
        self,
        driver='postgresql',
        user='msdss',
        password='msdss123',
        host='localhost',
        port='5432',
        database='msdss',
        enable_data_router=True,
        enable_users=False,
        data_router_kwargs={},
        users_kwargs={},
        get_current_user_kwargs={},
        create_get_current_user_kwargs=dict(
            superuser=True
        ),
        delete_get_current_user_kwargs=dict(
            superuser=True
        ),
        id_get_current_user_kwargs=None,
        insert_get_current_user_kwargs=dict(
            superuser=True
        ),
        metadata_get_current_user_kwargs=None,
        metadata_update_get_current_user_kwargs=dict(
            superuser=True
        ),
        query_get_current_user_kwargs=None,
        search_get_current_user_kwargs=None,
        update_get_current_user_kwargs=dict(
            superuser=True
        ),
        load_env=True,
        env_file='./.env',
        key_path=None,
        driver_key='MSDSS_DATABASE_DRIVER',
        user_key='MSDSS_DATABASE_USER',
        password_key='MSDSS_DATABASE_PASSWORD',
        host_key='MSDSS_DATABASE_HOST',
        port_key='MSDSS_DATABASE_PORT',
        database_key='MSDSS_DATABASE_NAME',
        *args, **kwargs):
        super().__init__(*args, **kwargs)

        # (DataAPI_env) Load env vars
        has_env = env_exists(file_path=env_file, key_path=key_path)
        if load_env and has_env:
            load_env_file(file_path=env_file, key_path=key_path)
            driver = os.getenv(driver_key, driver)
            user = os.getenv(user_key, user)
            password = os.getenv(password_key, password)
            host = os.getenv(host_key, host)
            port = os.getenv(port_key, port)
            database = os.getenv(database_key, database)

        # (DataAPI_users) Enable user routes and app
        if enable_users:
            
            # (DataAPI_users) Get matching parameters to set defaults if applicable
            params = locals()
            users_param_names = inspect.getfullargspec(UsersAPI).args
            matching_params = {k:v for k, v in params.items() if k in users_param_names and k != 'self'}

            # (DataAPI_users_kwargs) Set default args if not set
            for k, v in matching_params.items():
                users_kwargs[k] = users_kwargs.get(k, v)

            # (DataAPI_users_attr) Set base api as users api
            self.users_app = UsersAPI(**users_kwargs)
            self.api = self.users_app.api

            # (DataAPI_users_depends) Add current user dependencies if not set
            get_current_user_mappings = {
                'get_current_user': get_current_user_kwargs,
                'create_get_current_user': create_get_current_user_kwargs,
                'delete_get_current_user': delete_get_current_user_kwargs,
                'id_get_current_user': id_get_current_user_kwargs,
                'insert_get_current_user': insert_get_current_user_kwargs,
                'metadata_get_current_user': metadata_get_current_user_kwargs,
                'metadata_update_get_current_user': metadata_update_get_current_user_kwargs,
                'query_get_current_user': query_get_current_user_kwargs,
                'search_get_current_user': search_get_current_user_kwargs,
                'update_get_current_user': update_get_current_user_kwargs
            }
            for k, v in get_current_user_mappings.items():
                v = v if v else get_current_user_kwargs
                data_router_kwargs[k] = data_router_kwargs.get(k, self.users_app.get_current_user(**v))
        
        # (DataAPI_router_data) Add data router
        if enable_data_router:
            db = Database(driver=driver, user=user, password=password, host=host, port=port, database=database)
            data_router = get_data_router(database=db, **data_router_kwargs)
            self.add_router(data_router)
        