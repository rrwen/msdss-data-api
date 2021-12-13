from copy import deepcopy
from datetime import datetime
from fastapi import APIRouter, Body, Depends, Query
from typing import Any, Dict, List, Literal, Optional

from .managers import *
from .models import *
from .tools import *

async def _no_current_user():
    return None

def get_data_router(
    users_api=None,
    database=Database(),
    route_settings=DEFAULT_DATA_ROUTE_SETTINGS,
    prefix='/data',
    tags=['data'],
    *args, **kwargs):
    """
    Get a data router.
    
    Parameters
    ----------
    users_api : :class:`msdss_users_api:msdss_users_api.core.UsersAPI` or None
        Users API object to enable user authentication for data routes.
        If ``None``, user authentication will not be used for data routes.
    database : :class:`msdss_base_database:msdss_base_database.core.Database`
        A :class:`msdss_base_database:msdss_base_database.core.Database` object for managing data.
    route_settings : dict
        Dictionary of settings for the data routes. Each route consists of the following keys:

        * ``path``: resource path for the route
        * ``tags``: tags for open api spec
        * ``_enable`` (bool): Whether this route should be included or not
        * ``_restricted_tables`` (list(str)): List of table names not accessible by this route
        * ``_get_user`` (dict or None): Additional arguments passed to the :meth:`msdss_users_api.msdss_users_api.core.UsersAPI.get_current_user` function for the route - only applies if parameter ``users_api`` is not ``None`` and this settings is not ``None``, otherwise no user authentication will be added for this route
        * ``**kwargs``: Additional arguments passed to :meth:`fastapi:fastapi.FastAPI.get` for the id route

        The default settings are:

        .. jupyter-execute::
            :hide-code:

            from msdss_data_api.defaults import DEFAULT_DATA_ROUTE_SETTINGS
            from pprint import pprint
            pprint(DEFAULT_DATA_ROUTE_SETTINGS)

        Any unspecified settings will be replaced by their defaults.
    prefix : str
        Prefix path to all routes belonging to this router.
    tags : list(str)
        Tags for all routes in this router.
    *args, **kwargs
        Additional arguments to accept any extra parameters passed to :class:`fastapi:fastapi.routing.APIRouter`.
    
    Returns
    -------
    :class:`fastapi:fastapi.routing.APIRouter`
        A router object used for data routes. See `FastAPI bigger apps <https://fastapi.tiangolo.com/tutorial/bigger-applications/>`_

    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>

    Example
    -------
    .. jupyter-execute::

        from msdss_base_database import Database
        from msdss_base_api import API
        from msdss_users_api import UsersAPI
        from msdss_data_api.routers import get_data_router

        # Create database object
        database = Database(
            driver='postgresql',
            user='msdss',
            password='msdss123',
            host='localhost',
            port='5432',
            database='msdss'
        )
        
        # Create an app
        app = API()

        # Add the data router
        router = get_data_router(database=database)
        app.add_router(router)

        # Add the data router with users
        # CHANGE SECRETS TO STRONG PHRASES
        app = API()
        users_api = UsersAPI(
            'cookie-secret',
            'jwt-secret',
            'reset-secret',
            'verification-secret',
            database=database
        )
        router = get_data_router(users_api, database=database)
        app.add_router(router)
        
        # Host app at https://localhost:8000
        # Try it at https://localhost:8000/docs
        # app.start()
    """ 

    # (get_data_router_defaults) Merge defaults and user params 
    get_user = {}
    settings = deepcopy(DEFAULT_DATA_ROUTE_SETTINGS)
    for k in settings:
        if k in route_settings:
            settings[k].update(route_settings[k])

    # (get_data_router_apply) Apply settings to obtain dependencies
    get_user = {}
    get_data_manager = {}
    enable = {}
    for k, v in settings.items():
        get_user[k] = users_api.get_current_user(**v['_get_user']) if users_api and '_get_user' in v else _no_current_user
        del v['_get_user']
        get_data_manager[k] = create_data_manager_func(database=database, restricted_tables=v.pop('_restricted_tables'))
        enable[k] = v.pop('_enable')

    # (get_data_router_metamanager) Create metadata manager func
    get_metadata_manager = create_metadata_manager_func(database=database)

    # (get_data_router_create) Create api router for data routes
    out = APIRouter(prefix=prefix, tags=tags, *args, **kwargs)

    # (get_data_router_columns) Add columns route to data router
    if enable['columns']:
        @out.get(**settings['columns'])
        async def get_columns(
            dataset: str = Query(..., description='Name of the dataset'),
            data_manager = Depends(get_data_manager['query']),
            user = Depends(get_user['columns'])
        ):
            response = data_manager.get_columns(dataset)
            return response

    # (get_data_router_create) Add create route to data router
    if enable['create']:
        @out.post(**settings['create'])
        async def create_data(
            dataset: str = Query(..., description='Name of the dataset to create - the request body is used to upload JSON data under the "data" key in the form of "[{col: val, col2: val2, ...}, {col: val, col2: val2, ...}]", where each key represents a column and its corresponding value. Objects in this list should have the same keys.'),
            body: DataCreate = Body(
                ...,
                example={
                    'title': 'Title for Dataset',
                    'description': 'Description for dataset...',
                    'source': 'Data source for dataset',
                    'data': [
                        {'col_one': 1, 'col_two': 'a'},
                        {'col_one': 2, 'col_two': 'b'},
                        {'col_one': 3, 'col_two': 'c'}
                    ]
                }
            ),
            data_manager = Depends(get_data_manager['create']),
            metadata_manager = Depends(get_metadata_manager),
            user = Depends(get_user['create'])
        ):
            # (get_data_router_create_data) Get data
            body = body.dict()
            data = body.pop('data')

            # (get_data_router_create_metadata) Format metadata
            metadata = body
            metadata['dataset'] = dataset
            metadata['created_at'] = datetime.now()
            metadata['updated_at'] = datetime.now()

            # (get_data_router_create_users) Add user operations if available
            if user:
                metadata['created_by'] = user.email

            # (get_data_router_create_run) Create dataset and metadata
            data_manager.create(dataset=dataset, data=data)
            metadata_manager.create(dataset=dataset, data=metadata)

    # (get_data_router_delete) Add delete route to data router
    if enable['delete']:
        @out.delete(**settings['delete'])
        async def delete_data(
            dataset: str = Query(..., description='Name of the dataset to delete data from'),
            where: Optional[List[str]] = Query(None, description='Where statements to filter data to remove in the form of "column operator value" (e.g. "var < 3") - valid operators are: =, !=, >, >=, >, <, <=, !=, LIKE, ILIKE, NOTLIKE, NOTILIKE, CONTAINS, STARTSWITH, ENDSWITH'),
            where_boolean: Literal['AND', 'OR'] = Query('AND', alias='where-boolean', description='Either "AND" or "OR" to combine where statements'),
            delete_all: Optional[bool] = Query(False, description='Whether to remove the entire dataset or not'),
            data_manager = Depends(get_data_manager['delete']),
            metadata_manager = Depends(get_metadata_manager),
            user = Depends(get_user['delete'])
        ):
            data_manager.delete(dataset=dataset, where=where, where_boolean=where_boolean, delete_all=delete_all)
            metadata_manager.updated_at(dataset=dataset)
            if delete_all:
                metadata_manager.delete(dataset=dataset)

    # (get_data_router_id) Add id route to data router
    if enable['id']:
        @out.get(**settings['id'])
        async def get_data_by_id(
            dataset: str = Query(..., description='Name of the dataset'),
            id: str = Query(..., description='Identifier value to retrieve a specific document in the dataset'),
            id_column: Optional[str] =  Query('id', description='Identifier column name for the dataset'),
            data_manager = Depends(get_data_manager['id']),
            user = Depends(get_user['id'])
        ):
            where = [f'{id_column} = {id}']
            response = data_manager.get(dataset=dataset, where=where)
            return response

    # (get_data_router_insert) Add insert route to data router
    if enable['insert']:
        @out.put(**settings['insert'])
        async def insert_data(
            dataset: str = Query(..., description='Name of the dataset to insert - the request body is used to upload JSON data in the form of "[{key: value, key2: value2, ... }, {key: value, key2: value2, ...}]" where each key is a column name'),
            data: List[Dict[str, Any]] = Body(...),
            data_manager = Depends(get_data_manager['insert']),
            metadata_manager = Depends(get_metadata_manager),
            user = Depends(get_user['insert'])
        ):
            data_manager.insert(dataset=dataset, data=data)
            metadata_manager.updated_at(dataset)

    # (get_data_router_metadata) Add metadata route to data router
    if enable['metadata']:
        @out.get(**settings['metadata'])
        async def get_metadata(
            dataset: str = Query(..., description='Name of the dataset to get metadata for'),
            metadata_manager = Depends(get_metadata_manager),
            user = Depends(get_user['metadata'])
        ):
            response = metadata_manager.get(dataset=dataset)
            return response

    # (get_data_router_metadata) Add metadata route to data router
    if enable['metadata_update']:
        @out.put(**settings['metadata_update'])
        async def update_metadata(
            dataset: str = Query(..., description='Name of the dataset to update metadata for. Upload user and creation/update times can not be updated.'),
            body: MetadataUpdate = Body(
                ...,
                example={
                    'title': 'New Title to Replace Existing',
                    'description': 'New description to replace existing...',
                    'source': 'New data source to replace existing'
                }
            ),
            metadata_manager = Depends(get_metadata_manager),
            user = Depends(get_user['metadata_update'])
        ):
            response = metadata_manager.update(dataset=dataset, data=body.dict())
            return response

    # (get_data_router_query) Add query route to data router
    if enable['query']:
        @out.get(**settings['query'])
        async def query_data(
            dataset: str = Query(..., description='Name of the dataset to query'),
            select: Optional[List[str]] = Query('*', description='columns to include - "*" means all columns and "None" means to omit selection (useful for aggregate queries)'),
            where: Optional[List[str]] = Query(None, description='Where statements to filter data in the form of "column operator value" (e.g. "var < 3") - valid operators are: =, !=, >, >=, >, <, <=, !=, LIKE, ILIKE, NOTLIKE, NOTILIKE, CONTAINS, STARTSWITH, ENDSWITH'),
            group_by: Optional[List[str]] = Query(None, alias='group-by', description='column names to group by - should be used with aggregate and aggregate_func parameters'),
            aggregate: Optional[List[str]] = Query(None, description='column names to aggregate with the same order as the aggregate_func parameter'),
            aggregate_func: Optional[List[str]] = Query(None, alias='aggregate-func', description='Aggregate functions in the same order as the aggregate parameter'),
            order_by: Optional[List[str]] = Query(None, alias='order-by', description='column names to order by in the same order as parameter order_by_sort'),
            order_by_sort: Optional[List[Literal['asc', 'desc']]] = Query(None, alias='order-by-sort', description='Either "asc" for ascending or "desc" for descending order in the same order as parameter order_by'),
            limit: Optional[int] = Query(None, description='Number of items to return'),
            offset: Optional[int] = Query(None, description='Number of items to skip'),
            where_boolean: Literal['AND', 'OR'] = Query('AND', alias='where-boolean', description='Either "AND" or "OR" to combine where statements'),
            data_manager = Depends(get_data_manager['query']),
            user = Depends(get_user['query'])
        ):
            select = None if select[0] == 'None' else select
            response = data_manager.get(
                dataset=dataset,
                select=select,
                where=where,
                group_by=group_by,
                aggregate=aggregate,
                aggregate_func=aggregate_func,
                order_by=order_by,
                order_by_sort=order_by_sort,
                limit=limit,
                offset=offset,
                where_boolean=where_boolean
            )
            return response

    # (get_data_router_rows) Add rows route to data router
    if enable['rows']:
        @out.get(**settings['rows'])
        async def get_rows(
            dataset: str = Query(..., description='Name of the dataset'),
            data_manager = Depends(get_data_manager['query']),
            user = Depends(get_user['rows'])
        ):
            response = data_manager.get_rows(dataset)
            return response
    
    # (get_data_router_search) Add search route to data router
    if enable['search']:
        @out.get(**settings['search'])
        async def search_data(
            select: Optional[List[str]] = Query('*', description='columns to include in search - "*" means all columns and "None" means to omit selection (useful for aggregate queries).'),
            where: Optional[List[str]] = Query(None, description='Where statements to filter data in the form of "column operator value" (e.g. "dataset = test_data") - valid operators are: =, !=, >, >=, >, <, <=, !=, LIKE, ILIKE, NOTLIKE, NOTILIKE, CONTAINS, STARTSWITH, ENDSWITH'),
            order_by: Optional[List[str]] = Query(None, alias='order-by', description='column names to order by in the same order as parameter order_by_sort'),
            order_by_sort: Optional[List[Literal['asc', 'desc']]] = Query(None, alias='order-by-sort', description='Either "asc" for ascending or "desc" for descending order in the same order as parameter order_by'),
            limit: Optional[int] = Query(None, description='Number of items to return'),
            offset: Optional[int] = Query(None, description='Number of items to skip'),
            where_boolean: Literal['AND', 'OR'] = Query('AND', alias='where-boolean', description='Either "AND" or "OR" to combine where statements'),
            metadata_manager = Depends(get_metadata_manager),
            user = Depends(get_user['search'])
        ):
            select = None if select[0] == 'None' else select
            response = metadata_manager.search(
                select=select,
                where=where,
                order_by=order_by,
                order_by_sort=order_by_sort,
                limit=limit,
                offset=offset,
                where_boolean=where_boolean
            )
            return response
    
    # (get_data_router_update) Add update route to data router
    if enable['update']:
        @out.put(**settings['update'])
        async def update_data(
            dataset: str = Query(..., description='Name of the dataset to update - the request body is used to upload JSON data in the form of "{key: value, key2: value2, ... }" where each key is a column name and each value is the new value to use (matching the where parameter)'),
            body: Dict[str, Any] = Body(
                ...,
                example={'col_one': 1, 'col_two': 'a'}
            ),
            where: List[str] = Query(..., description='Where statements to filter data to update in the form of "column operator value" (e.g. "var < 3") - valid operators are: =, !=, >, >=, >, <, <=, !=, LIKE, ILIKE, NOTLIKE, NOTILIKE, CONTAINS, STARTSWITH, ENDSWITH'),
            data_manager = Depends(get_data_manager['update']),
            metadata_manager = Depends(get_metadata_manager),
            user = Depends(get_user['update'])
        ):
            data_manager.update(dataset=dataset, data=body, where=where)
            metadata_manager.updated_at(dataset)
    return out
