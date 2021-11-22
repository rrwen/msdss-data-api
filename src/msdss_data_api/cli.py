import argparse
import inspect

from msdss_data_api.defaults import DEFAULT_RESTRICTED_TABLES

from .core import DataAPI
from .defaults import *

try:
    from msdss_users_api import UsersAPI
except ImportError:
    pass

def _get_parser():
    """
    Builds an ``argparse`` parser for the ``msdss-data`` command line tool.

    Returns
    -------
    :class:`argparse.ArgumentParser`
        An ``argparse`` parser for ``msdss-data``.

    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>

    Example
    -------

    .. jupyter-execute::
        :hide-output:

        from msdss_data_api.cli import _get_parser

        parser = _get_parser()
        parser.print_help()
    """

    # (_get_parser_parsers) Create main parser and sub parsers
    parser = argparse.ArgumentParser(description='Manages data with a database')
    subparsers = parser.add_subparsers(title='commands', dest='command')
    
    # (_get_parser_register) Add register command
    register_parser = subparsers.add_parser('register', help='register a user')
    register_parser.add_argument('email', type=str, nargs='?', help='email for user')
    register_parser.add_argument('password', type=str, nargs='?', help='password for user')
    register_parser.add_argument('--superuser', dest='superuser', action='store_true', help='register a superuser')
    register_parser.set_defaults(superuser=False)

    # (_get_parser_get) Add get command
    get_parser = subparsers.add_parser('get', help='get user attributes')
    get_parser.add_argument('email', type=str, help='email for user')

    # (_get_parser_delete) Add delete command
    delete_parser = subparsers.add_parser('delete', help='delete a user')
    delete_parser.add_argument('email', type=str, help='email of user to delete')

    # (_get_parser_reset) Add reset command
    reset_parser = subparsers.add_parser('reset', help='reset user password')
    reset_parser.add_argument('email', type=str, help='email of user to reset')
    reset_parser.add_argument('password', type=str, nargs='?', help='new password to use')

    # (_get_parser_update) Add update command
    update_parser = subparsers.add_parser('update', help='update a user\'s attribute')
    update_parser.add_argument('email', type=str, help='email of user')
    update_parser.add_argument('--is_active', type=bool, default=None, help='set is_active attribute')
    update_parser.add_argument('--is_superuser', type=bool, default=None, help='set is_superuser attribute')
    update_parser.add_argument('--is_verified', type=bool, default=None, help='set is_verified attribute')

    # (_get_parser_start) Add start command
    start_parser = subparsers.add_parser('start', help='start a users api server')
    start_parser.add_argument('--host', type=str, default='127.0.0.1', help='address to host server')
    start_parser.add_argument('--port', type=int, default=8000, help='port to host server')
    start_parser.add_argument('--log_level', type=str, default='info', help='level of verbose messages to display')
    start_parser.add_argument('--data_prefix', type=str, default='/data', help='path prefix for data routes')
    start_parser.add_argument('--auth_prefix', type=str, default='/auth', help='path prefix for auth routes')
    start_parser.add_argument('--users_prefix', type=str, default='/users', help='path prefix for users routes')
    start_parser.add_argument('--auth_lifetime', type=int, default=3600, help='token/cookie lifetime before expiry in secs')
    start_parser.add_argument('--disable_data_router', dest='enable_data_router', action='store_false', help='disable data router')
    start_parser.add_argument('--enable_users', dest='enable_users', action='store_true', help='enable users authentication')
    start_parser.add_argument('--restricted_tables', type=str, default=','.join(DEFAULT_RESTRICTED_TABLES), help='restricted data table names separated by ,')
    start_parser.add_argument('--disable_create_route', dest='enable_create_route', action='store_false', help='disable data create route')
    start_parser.add_argument('--disable_delete_route', dest='enable_delete_route', action='store_false', help='disable data delete route')
    start_parser.add_argument('--disable_id_route', dest='enable_id_route', action='store_false', help='disable data id route')
    start_parser.add_argument('--disable_insert_route', dest='enable_insert_route', action='store_false', help='disable data insert route')
    start_parser.add_argument('--disable_metadata_route', dest='enable_metadata_route', action='store_false', help='disable metadata GET route')
    start_parser.add_argument('--disable_metadata_update_route', dest='enable_metadata_update_route', action='store_false', help='disable metadata UPDATE route')
    start_parser.add_argument('--disable_query_route', dest='enable_query_route', action='store_false', help='disable data query route')
    start_parser.add_argument('--disable_search_route', dest='enable_search_route', action='store_false', help='disable data search route')
    start_parser.add_argument('--disable_update_route', dest='enable_update_route', action='store_false', help='disable data update route')
    start_parser.add_argument('--disable_create_superuser', dest='create_superuser', action='store_false', help='disable superuser req for create route')
    start_parser.add_argument('--disable_delete_superuser', dest='delete_superuser', action='store_false', help='disable superuser req for delete route')
    start_parser.add_argument('--enable_id_superuser', dest='id_superuser', action='store_true', help='enable superuser req for id route')
    start_parser.add_argument('--disable_insert_superuser', dest='insert_superuser', action='store_false', help='disable superuser req for insert route')
    start_parser.add_argument('--enable_metadata_superuser', dest='metadata_superuser', action='store_true', help='enable superuser req for metadata GET route')
    start_parser.add_argument('--disable_metadata_update_superuser', dest='metadata_update_superuser', action='store_false', help='disable superuser req for metadata PUT route')
    start_parser.add_argument('--enable_query_superuser', dest='query_superuser', action='store_true', help='enable superuser req for query route')
    start_parser.add_argument('--enable_search_superuser', dest='search_superuser', action='store_true', help='enable superuser req for search route')
    start_parser.add_argument('--disable_update_superuser', dest='update_superuser', action='store_false', help='disable superuser req for update route')
    start_parser.add_argument('--disable_register_superuser', dest='register_router_superuser', action='store_false', help='disable superuser requirement for register route')
    start_parser.add_argument('--disable_auth_router', dest='enable_auth_router', action='store_false', help='disable auth router')
    start_parser.add_argument('--disable_register_router', dest='enable_register_router', action='store_false', help='disable register router')
    start_parser.add_argument('--disable_verify_router', dest='enable_verify_router', action='store_false', help='disable verify router')
    start_parser.add_argument('--disable_reset_password_router', dest='enable_reset_password_router', action='store_false', help='disable reset password router')
    start_parser.add_argument('--disable_users_router', dest='enable_users_router', action='store_false', help='disable users router')
    start_parser.add_argument('--disable_jwt_auth', dest='enable_jwt_auth', action='store_false', help='disable jwt authentication')
    start_parser.add_argument('--disable_cookie_auth', dest='enable_cookie_auth', action='store_false', help='disable cookie authentication')
    start_parser.add_argument('--secret_key', type=str, default='MSDSS_USERS_SECRET', help='env var name for secret phrase')
    start_parser.add_argument('--jwt_secret_key', type=str, default='MSDSS_USERS_JWT_SECRET', help='env var name for jwt secret')
    start_parser.add_argument('--cookie_secret_key', type=str, default='MSDSS_USERS_COOKIE_SECRET', help='env var name for cookie secret')
    start_parser.add_argument('--reset_password_token_secret_key', type=str, default='MSDSS_USERS_RESET_PASSWORD_TOKEN_SECRET', help='env var name for reset password secret')
    start_parser.add_argument('--verification_token_secret_key', type=str, default='MSDSS_USERS_VERIFICATION_TOKEN_SECRET', help='env var name for verify token secret')
    start_parser.add_argument('--driver_key', type=str, default='MSDSS_DATABASE_DRIVER', help='env var name for db driver')
    start_parser.add_argument('--user_key', type=str, default='MSDSS_DATABASE_USER', help='env var name for db user')
    start_parser.add_argument('--password_key', type=str, default='MSDSS_DATABASE_PASSWORD', help='env var name for db user password')
    start_parser.add_argument('--host_key', type=str, default='MSDSS_DATABASE_HOST', help='env var name for db host')
    start_parser.add_argument('--port_key', type=str, default='MSDSS_DATABASE_PORT', help='env var name for db port')
    start_parser.add_argument('--database_key', type=str, default='MSDSS_DATABASE_NAME', help='env var name for db name')
    start_parser.set_defaults(
        enable_data_router=True,
        enable_users=False,
        enable_create_route=True,
        enable_delete_route=True,
        enable_id_route=True,
        enable_insert_route=True,
        enable_metadata_route=True,
        enable_metadata_update_route=True,
        enable_query_route=True,
        enable_search_route=True,
        enable_update_route=True,
        create_superuser=True,
        delete_superuser=True,
        id_superuser=False,
        insert_superuser=True,
        metadata_superuser=False,
        metadata_update_superuser=True,
        query_superuser=False,
        search_superuser=False,
        update_superuser=True,
        register_router_superuser=True,
        enable_auth_router=True,
        enable_register_router=True,
        enable_verify_router=True,
        enable_reset_password_router=True,
        enable_users_router=True,
        enable_jwt_auth=True,
        enable_cookie_auth=True
    )

    # (_get_parser_file_key) Add file and key arguments to all commands
    for p in [parser, register_parser, delete_parser, update_parser, get_parser, reset_parser, start_parser]:
        p.add_argument('--env_file', type=str, default='./.env', help='path of .env file')
        p.add_argument('--key_path', type=str, default=None, help='path of key file')
    
    # (_get_parser_out) Return the parser
    out = parser
    return out

def run():
    """
    Runs the ``msdss-data`` command.

    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>

    Example
    -------
    >>> msdss-data --help

    .. jupyter-execute::
        :hide-code:

        from msdss_data_api.cli import _get_parser

        parser = _get_parser()
        parser.print_help()

    Create a user interactively:

    >>> msdss-data register

    Get user attributes:

    >>> msdss-data get test@example.com

    Update user attributes:

    >>> msdss-data update test@example.com --is_verified True

    Reset user password:

    >>> msdss-data reset test@example.com

    Delete a user:

    >>> msdss-data delete test@example.com

    Start an API server:

    >>> msdss-data start
    """

    # (run_kwargs) Get arguments and command
    parser = _get_parser()
    kwargs = vars(parser.parse_args())
    command = kwargs.pop('command')

    # (run_command) Run commands
    if command == 'register':

        # (run_command_register) Execute user register
        pass
    elif command == 'get':

        # (run_command_get) Execute user get
        pass

    elif command == 'delete':

        # (run_command_delete) Execute user delete
        pass

    elif command == 'reset':

        # (run_command_reset) Reset password for user
        pass

    elif command == 'update':

        # (run_command_update) Execute user update
        pass

    elif command == 'start':

        # (run_command_start_data) Get data router args
        data_router_kwargs = dict(
            prefix=kwargs.pop('data_prefix'),
            enable_create_route=kwargs.pop('enable_create_route'),
            enable_delete_route=kwargs.pop('enable_delete_route'),
            enable_id_route=kwargs.pop('enable_id_route'),
            enable_insert_route=kwargs.pop('enable_insert_route'),
            enable_metadata_route=kwargs.pop('enable_metadata_route'),
            enable_metadata_update_route=kwargs.pop('enable_metadata_update_route'),
            enable_query_route=kwargs.pop('enable_query_route'),
            enable_search_route=kwargs.pop('enable_search_route'),
            enable_update_route=kwargs.pop('enable_update_route'),
            restricted_tables=[t.strip() for t in kwargs.pop('restricted_tables').split(',')]
        )
        
        # (run_command_start_get_user) Extract get user args
        get_current_user_kwargs = dict(
            create_get_current_user_kwargs=dict(superuser=kwargs.pop('create_superuser')),
            delete_get_current_user_kwargs=dict(superuser=kwargs.pop('delete_superuser')),
            id_get_current_user_kwargs=dict(superuser=kwargs.pop('id_superuser')),
            insert_get_current_user_kwargs=dict(superuser=kwargs.pop('insert_superuser')),
            metadata_get_current_user_kwargs=dict(superuser=kwargs.pop('metadata_superuser')),
            metadata_update_get_current_user_kwargs=dict(superuser=kwargs.pop('metadata_update_superuser')),
            query_get_current_user_kwargs=dict(superuser=kwargs.pop('query_superuser')),
            search_get_current_user_kwargs=dict(superuser=kwargs.pop('search_superuser')),
            update_get_current_user_kwargs=dict(superuser=kwargs.pop('update_superuser'))
        )

        # (run_command_start_user) Extract user api args
        users_kwargs = dict(
            secret_key=kwargs.pop('secret_key'),
            jwt_secret_key=kwargs.pop('jwt_secret_key'),
            cookie_secret_key=kwargs.pop('cookie_secret_key'),
            reset_password_token_secret_key=kwargs.pop('reset_password_token_secret_key'),
            verification_token_secret_key=kwargs.pop('verification_token_secret_key'),
            register_router_superuser=kwargs.pop('register_router_superuser'),
            enable_auth_router=kwargs.pop('enable_auth_router'),
            enable_register_router=kwargs.pop('enable_register_router'),
            enable_verify_router=kwargs.pop('enable_verify_router'),
            enable_reset_password_router=kwargs.pop('enable_reset_password_router'),
            enable_users_router=kwargs.pop('enable_users_router'),
            enable_jwt_auth=kwargs.pop('enable_jwt_auth'),
            enable_cookie_auth=kwargs.pop('enable_cookie_auth')
        )

        # (run_command_start_route) Extract route args
        auth_prefix = kwargs.pop('auth_prefix')
        users_prefix = kwargs.pop('users_prefix')
        auth_lifetime = kwargs.pop('auth_lifetime')

        # (run_command_start_serve) Extract server args
        app_kwargs = dict(
            host=kwargs.pop('host'),
            port=kwargs.pop('port'),
            log_level=kwargs.pop('log_level')
        )

        # (run_command_start_defaults) Get default parameters for data api
        defaults = inspect.signature(DataAPI).parameters
        for k, v in defaults.items():
            is_not_empty = v.default is not inspect.Parameter.empty 
            if k not in kwargs and is_not_empty:
                kwargs[k] = defaults[k].default

        # (run_command_start_merge_users) Merge get user args to standard args
        for k in get_current_user_kwargs:
            if kwargs[k]:
                kwargs[k].update(get_current_user_kwargs[k])

        # (run_command_start_merge_data) Merge data router args to standard args
        kwargs['data_router_kwargs'].update(data_router_kwargs)

        # (run_command_start_users) Add users kwargs if enabled
        if kwargs['enable_users']:

            # (run_command_start_users_merge) Merge single value users kwargs
            kwargs['users_kwargs'].update(users_kwargs)

            # (run_command_start_users_defaults) Set default parameters for users api
            users_defaults = inspect.signature(UsersAPI).parameters
            for k, v in users_defaults.items():
                is_not_empty = v.default is not inspect.Parameter.empty 
                if k not in kwargs['users_kwargs'] and is_not_empty:
                    kwargs['users_kwargs'][k] = users_defaults[k].default

            # (run_command_start_users_merge) Merge users args to standard args
            kwargs['users_kwargs']['auth_router_jwt_include_kwargs']['prefix'] = auth_prefix + '/jwt'
            kwargs['users_kwargs']['auth_router_cookie_include_kwargs']['prefix'] = auth_prefix
            kwargs['users_kwargs']['register_router_include_kwargs']['prefix'] = auth_prefix
            kwargs['users_kwargs']['verify_router_include_kwargs']['prefix'] = auth_prefix
            kwargs['users_kwargs']['reset_password_router_include_kwargs']['prefix'] = auth_prefix
            kwargs['users_kwargs']['users_router_include_kwargs']['prefix'] = users_prefix
            kwargs['users_kwargs']['cookie_kwargs']['lifetime_seconds'] = auth_lifetime
            kwargs['users_kwargs']['jwt_kwargs'].update(dict(
                lifetime_seconds=auth_lifetime,
                tokenUrl=auth_prefix[1:] + '/jwt/login'
            ))

        # (run_command_start) Execute users api server
        app = DataAPI(**kwargs)
        app.start(**app_kwargs)