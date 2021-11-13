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
        query_get_current_user_kwargs=None,
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
                'query_get_current_user': query_get_current_user_kwargs,
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
        