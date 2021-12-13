import argparse
import ast
import os
import pandas

from datetime import datetime
from msdss_base_database import Database
from msdss_base_database.env import DatabaseDotEnv
from msdss_base_database.defaults import DEFAULT_SUPPORTED_OPERATORS

from .core import DataAPI
from .defaults import *
from .managers import *

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

    # (_get_parser_create) Add create command
    create_parser = subparsers.add_parser('create', help='create a dataset')
    create_parser.add_argument('dataset', type=str, help='dataset name')
    create_parser.add_argument('data', type=str, help='file path for data to create - supports .csv, .xlsx, .json, .xml')
    create_parser.add_argument('--metadata', metavar=('COL', 'VALUE'), nargs=2, action='append', help='metadata columns to set - e.g. title "Some Title", description "Some descr.."')

    # (_get_parser_delete) Add delete command
    delete_parser = subparsers.add_parser('delete', help='delete a dataset')
    delete_parser.add_argument('dataset', type=str, help='dataset name')
    delete_parser.add_argument('--where', action='append', help='where statement for filtering rows to delete in the form of "col operator value" (e.g. "col_a = 1") - operators supported are' + ', '.join(DEFAULT_SUPPORTED_OPERATORS))
    delete_parser.add_argument('--where_boolean', type=str, default='AND', help='bool to join multiple where statements')
    delete_parser.add_argument('--delete_all', dest='delete_all', action='store_true', help='flag to delete the entire dataset')
    delete_parser.set_defaults(delete_all=False)

    # (_get_parser_get) Add get command
    get_parser = subparsers.add_parser('get', help='query a dataset')
    get_parser.add_argument('dataset', type=str, help='dataset name')
    get_parser.add_argument('--select', action='append', help='column names to select')
    get_parser.add_argument('--where', action='append', help='where statement for filtering rows to get in the form of "col operator value" (e.g. "col_a = 1") - operators supported are' + ', '.join(DEFAULT_SUPPORTED_OPERATORS))
    get_parser.add_argument('--group_by', action='append', help='column names to group by')
    get_parser.add_argument('--aggregate', action='append', help='column names to aggregate')
    get_parser.add_argument('--aggregate_func', action='append', help='aggregate func name (e.g. sum, count) in the order of --aggregate')
    get_parser.add_argument('--order_by', action='append', help='column names to sort by')
    get_parser.add_argument('--order_by_sort', action='append', help='asc or desc for each col in --order_by')
    get_parser.add_argument('--limit', type=int, default=None, help='')
    get_parser.add_argument('--where_boolean', type=str, default='AND', help='bool to join multiple where statements')
    
    # (_get_parser_insert) Add insert command
    insert_parser = subparsers.add_parser('insert', help='insert data into a dataset')
    insert_parser.add_argument('dataset', type=str, help='dataset name')
    insert_parser.add_argument('data', type=str, help='data to insert - e.g. [ {"col_a": 1, "col_b": "a"}, {"col_a": 2, "col_b": "b"} ]')
    
    # (_get_parser_update) Add update command
    update_parser = subparsers.add_parser('update', help='update data in a dataset')
    update_parser.add_argument('--data', required=True, metavar=('COL', 'VALUE'), nargs=2, action='append', help='column names and values to update with')
    update_parser.add_argument('--where', action='append', help='where statement for filtering rows to update in the form of "col operator value" (e.g. "col_a = 1") - operators supported are' + ', '.join(DEFAULT_SUPPORTED_OPERATORS))

    # (_get_parser_get) Add get command
    search_parser = subparsers.add_parser('search', help='search datasets')
    search_parser.add_argument('--select', action='append', help='column names to select')
    search_parser.add_argument('--where', action='append', help='where statement for filtering rows to get in the form of "col operator value" (e.g. "col_a = 1") - operators supported are' + ', '.join(DEFAULT_SUPPORTED_OPERATORS))
    search_parser.add_argument('--group_by', action='append', help='column names to group by')
    search_parser.add_argument('--aggregate', action='append', help='column names to aggregate')
    search_parser.add_argument('--aggregate_func', action='append', help='aggregate func name (e.g. sum, count) in the order of --aggregate')
    search_parser.add_argument('--order_by', action='append', help='column names to sort by')
    search_parser.add_argument('--order_by_sort', action='append', help='asc or desc for each col in --order_by')
    search_parser.add_argument('--limit', type=int, default=None, help='')
    search_parser.add_argument('--where_boolean', type=str, default='AND', help='bool to join multiple where statements')

    # (_get_parser_start) Add start command
    start_parser = subparsers.add_parser('start', help='start a data api server')
    start_parser.add_argument('--host', type=str, default='127.0.0.1', help='address to host server')
    start_parser.add_argument('--port', type=int, default=8000, help='port to host server')
    start_parser.add_argument('--log_level', type=str, default='info', help='level of verbose messages to display')
    start_parser.add_argument('--set', metavar=('ROUTE', 'KEY', 'VALUE'), nargs=3, action='append', help='set route settings, where ROUTE is the route name (create, delete, metadata, etc), KEY is the setting name (e.g. path, _enable, etc), and VALUE is value for the setting')
    start_parser.add_argument('--enable_users', dest='enable_users', action='store_true', help='enable user auth for routes')
    start_parser.set_defaults(enable_users=False)

    # (_get_parser_file_key) Add file and key arguments to all commands
    for p in [parser, create_parser, delete_parser, get_parser, insert_parser, update_parser, search_parser, start_parser]:
        p.add_argument('--env_file', type=str, default='./.env', help='path of .env file')
        p.add_argument('--key_path', type=str, default=None, help='path of key file')
    
    # (_get_parser_out) Return the parser
    out = parser
    return out

def _parse_route_settings(cli_route_settings):
    """
    Parses ``--set`` route settings for the ``msdss-data`` command line tool.

    Parameters
    ----------
    cli_route_settings : list(tuple)
        List of tuples of length 3, representing the route, key setting and value setting in order.

    Returns
    -------
    dict
        A dictionary that can be passed to parameter ``route_settings`` in :func:`msdss_data_api.routers.get_data_router`

    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>

    Example
    -------

    .. jupyter-execute::
        :hide-output:

        from msdss_data_api.cli import _parse_route_settings
        from pprint import pprint

        cli_route_settings = [
            ('create', '_restricted_tables', '["user", "data"]'),
            ('create', '_enable', 'True'),
            ('create', '_get_user', '{"superuser": True}'),
            ('delete', 'path', '/{dataset}'),
            ('delete', 'tags', '["data"]')
        ]
        route_settings = _parse_route_settings(cli_route_settings)
        pprint(route_settings)
    """
    out = {route: {} for route, k, v in cli_route_settings}
    for route, key, value in cli_route_settings:
        if key in ('tags', '_restricted_tables', '_get_user', '_enable'):
            out[route][key] = ast.literal_eval(value)
        else:
            out[route][key] = value
    return out

def _read_data_file(data_path):
    """
    Reads a data file into a :class:`pandas:pandas.DataFrame` object.

    Parameters
    ----------
    data_path : str
        Path of the data file with extension. Supports ``.csv``, ``.xlsx``/``.xls``, ``.json``, and ``.xml``.

    Returns
    -------
    :class:`pandas:pandas.DataFrame`
        A dataframe object of the file data.

    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>

    Example
    -------

    .. code::

        from msdss_data_api.cli import _read_data_file

        data = _read_data_file('path/to/data.json')
    """
    data_ext = os.path.splitext(data_path)[1].lower()
    if data_ext == '.csv':
        out = pandas.read_csv(data_path)
    elif data_ext in ('.xlsx', '.xls'):
        out = pandas.read_excel(data_path)
    elif data_ext == '.json':
        out = pandas.read_json(data_path)
    elif data_ext == '.xml':
        out = pandas.read_xml(data_path)
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

    Create a dataset:

    >>> msdss-data create <data_name> <path/to/data.json> --metadata title "Test Data"

    Query dataset:

    >>> msdss-data get <data_name>

    Update dataset values:

    >>> msdss-data update <data_name> --data <col_name> <update_value> --where <col_name> = <value>

    Insert data into dataset:

    >>> msdss-data insert <data_name> "[{'col_a': 1, 'col_b': 'a'}]"

    Delete a dataset:

    >>> msdss-data delete <data_name> --delete_all

    Search datasets:

    >>> msdss-data search --where "dataset = <data_name>"

    Start an API server:

    >>> msdss-data start
    """

    # (run_kwargs) Get arguments and command
    parser = _get_parser()
    kwargs = vars(parser.parse_args())
    command = kwargs.pop('command')

    # (run_env) Get env vars
    env_kwargs = dict(
        env_file=kwargs.pop('env_file'),
        key_path=kwargs.pop('key_path')
    )

    # (run_database) Create database obj
    database = Database(env=DatabaseDotEnv(**env_kwargs))

    # (run_managers) Create data and metadata managers
    data_manager = DataManager(database=database)
    metadata_manager = MetadataManager(data_manager=data_manager)

    # (run_command) Run commands
    if command == 'create':

        # (run_command_create_metadata) Get metadata attrs 
        metadata = kwargs.pop('metadata', None)
        metadata = dict(metadata) if metadata else {}
        metadata['created_by'] = 'admin'
        metadata['created_at'] = datetime.now()
        metadata['updated_at'] = datetime.now()

        # (run_command_create_read) Read data from file
        kwargs['data'] = _read_data_file(kwargs.pop('data'))

        # (run_command_create_run) Create the dataset
        try:
            dataset = kwargs.get('dataset')
            data_manager.create(**kwargs)
            metadata_manager.create(dataset, metadata)
            print('Dataset created ' + dataset)
        except HTTPException as e:
            print(e.detail)

    elif command == 'delete':

        # (run_command_delete) Execute user delete
        try:
            dataset = kwargs.get('dataset')
            data_manager.delete(**kwargs)
            metadata_manager.delete(dataset)
            print('Dataset deleted ' + dataset)
        except HTTPException as e:
            print(e.detail)

    elif command == 'get':

        # (run_command_get) Query a dataset
        try:
            dataset = kwargs.get('dataset')
            data = data_manager.get(**kwargs)
            print(pandas.DataFrame(data))
        except HTTPException as e:
            print(e.detail)

    elif command == 'insert':

        # (run_command_insert) Insert data into a dataset
        try:
            kwargs['data'] = ast.literal_eval(kwargs['data'])
            dataset = kwargs.get('dataset')
            data_manager.insert(**kwargs)
            metadata_manager.updated_at(dataset)
            print('Dataset insert ' + dataset)
        except HTTPException as e:
            print(e.detail)

    elif command == 'update':

        # (run_command_update_data) Get data attrs 
        kwargs['data'] = dict(kwargs['data'])

        # (run_command_update_run) Update dataset data
        try:
            dataset = kwargs.get('dataset')
            data_manager.update(**kwargs)
            metadata_manager.updated_at(dataset)
            print('Dataset update ' + dataset)
        except HTTPException as e:
            print(e.detail)

    elif command == 'search':

        # (run_command_search_run) Search datasets
        try:
            data = metadata_manager.search(**kwargs)
            print(pandas.DataFrame(data))
        except HTTPException as e:
            print(e.detail)

    elif command == 'start':

        # (run_command_start_server) Extract server kwargs
        start_kwargs = dict(
            host=kwargs.pop('host'),
            port=kwargs.pop('port'),
            log_level=kwargs.pop('log_level')
        )

        # (run_command_start_env) Configure env database and users api
        kwargs['database'] = database
        enable_users = kwargs.pop('enable_users')
        if enable_users:
            from msdss_users_api import UsersAPI
            from msdss_users_api.env import UsersDotEnv
            kwargs['users_api'] = UsersAPI(env=UsersDotEnv(**env_kwargs))
        else:
            kwargs['users_api'] = None

        # (run_command_start_settings) Convert route settings
        cli_route_settings = kwargs.pop('set', None)
        kwargs['data_router_settings'] = dict(
            route_settings=_parse_route_settings(cli_route_settings) if cli_route_settings else {}
        )

        # (run_command_start) Execute users api server
        app = DataAPI(**kwargs)
        app.start(**start_kwargs)