from fastapi import APIRouter, Body, Depends, HTTPException, Query
from typing import Any, Dict, List, Optional

from .managers import *
from .tools import *

async def _no_current_user():
    return None

def get_data_router(
    prefix='/data',
    tags=['data'],
    database=Database(),
    get_current_user=_no_current_user,
    restricted_tables=DEFAULT_RESTRICTED_TABLES,
    enable_create_route=True,
    enable_delete_route=True,
    enable_id_route=True,
    enable_query_route=True,
    enable_update_route=True,
    create_route_path='/',
    create_route_kwargs={},
    create_route_restricted_tables=None,
    create_get_current_user=None,
    delete_route_path='/',
    delete_route_kwargs={},
    delete_route_restricted_tables=None,
    delete_get_current_user=None,
    id_route_path='/{dataset}/{id}',
    id_route_kwargs={},
    id_route_restricted_tables=None,
    id_get_current_user=None,
    query_route_path='/{dataset}',
    query_route_kwargs={},
    query_route_restricted_tables=None,
    query_get_current_user=None,
    update_route_path='/{dataset}',
    update_route_kwargs={},
    update_route_restricted_tables=None,
    update_get_current_user=None,
    *args, **kwargs):
    """
    Get a data router.
    
    Parameters
    ----------
    prefix : str
        Prefix path to all routes belonging to this router.
    tags : list(str)
        Tags for all routes in this router.
    database : :class:`msdss_base_database:msdss_base_database.core.Database`
        A :class:`msdss_base_database:msdss_base_database.core.Database` object.
    get_current_user : func
        A function to get the current user. See `FastAPI get_current_user <https://fastapi.tiangolo.com/tutorial/security/get-current-user/>`_.
    restricted_tables : list(str)
        List of restricted table names that are not accessible on this router. If any of these are accessed, a 401 unauthorized http exception will be thrown. See :func:`msdss_data_api.data.handle_table_restrictions`.
    enable_create_route : bool
        Whether to enable the create path for this router or not.
    enable_delete_route : bool
        Whether to enable the delete path for this router or not.
    enable_id_route : bool
        Whether to enable the id path for this router or not.
    enable_query_route : bool
        Whether to enable the query path for this router or not.
    enable_update_route : bool
        Whether to enable the update path for this router or not.
    create_route_path : str
        Path for the create route in this router. The full path will include the param ``prefix``.
    create_route_kwargs : dict
        Additional arguments passed to :meth:`fastapi:fastapi.FastAPI.get` for the create route.
    create_route_restricted_tables : list(str) or None
        Same as parameter ``restricted_tables`` except router specific. If ``None``, will default to parameter ``restricted_tables``.
    create_get_current_user : func
        A function to get the current user, but route specific. See `FastAPI get_current_user <https://fastapi.tiangolo.com/tutorial/security/get-current-user/>`_.
        If ``None``, it will default to parameter ``get_current_user``.
    delete_route_path : str
        Path for the delete route in this router. The full path will include the param ``prefix``.
    delete_route_kwargs : dict
        Additional arguments passed to :meth:`fastapi:fastapi.FastAPI.get` for the delete route.
    delete_route_restricted_tables : list(str) or None
        Same as parameter ``restricted_tables`` except router specific. If ``None``, will default to parameter ``restricted_tables``.
    delete_get_current_user : func
        A function to get the current user, but route specific. See `FastAPI get_current_user <https://fastapi.tiangolo.com/tutorial/security/get-current-user/>`_.
        If ``None``, it will default to parameter ``get_current_user``.
    id_route_path : str
        Path for the id route in this router. The full path will include the param ``prefix``.
    id_route_kwargs : dict
        Additional arguments passed to :meth:`fastapi:fastapi.FastAPI.get` for the id route.
    id_route_restricted_tables : list(str) or None
        Same as parameter ``restricted_tables`` except router specific. If ``None``, will default to parameter ``restricted_tables``.
    id_get_current_user : func
        A function to get the current user, but route specific. See `FastAPI get_current_user <https://fastapi.tiangolo.com/tutorial/security/get-current-user/>`_.
        If ``None``, it will default to parameter ``get_current_user``.
    query_route_path : str
        Path for the query route in this router. The full path will include the param ``prefix``.
    query_route_kwargs : dict
        Additional arguments passed to :meth:`fastapi:fastapi.FastAPI.get` for the query route.
    query_route_restricted_tables : list(str)
        Same as parameter ``restricted_tables`` except router specific. If ``None``, will default to parameter ``restricted_tables``.
    query_get_current_user : func
        A function to get the current user, but route specific. See `FastAPI get_current_user <https://fastapi.tiangolo.com/tutorial/security/get-current-user/>`_.
        If ``None``, it will default to parameter ``get_current_user``.
    update_route_path : str
        Path for the update route in this router.
    update_route_kwargs : dict
        Additional arguments passed to :meth:`fastapi:fastapi.FastAPI.get` for the update route.
    update_route_restricted_tables : list(str) or None
        Same as parameter ``restricted_tables`` except router specific. If ``None``, will default to parameter ``restricted_tables``.
    update_get_current_user : func
        A function to get the current user, but route specific. See `FastAPI get_current_user <https://fastapi.tiangolo.com/tutorial/security/get-current-user/>`_.
        If ``None``, it will default to parameter ``get_current_user``.
    *args, **kwargs
        Additional arguments to accept any extra parameters passed to :class:`fastapi:fastapi.routing.APIRouter`.
    
    Returns
    -------
    :class:`fastapi:fastapi.routing.APIRouter`
            A router object used for organizing larger applications and for modularity. See `FastAPI bigger apps <https://fastapi.tiangolo.com/tutorial/bigger-applications/>`_

    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>

    Example
    -------
    .. jupyter-execute::

        from msdss_base_api import API
        from msdss_data_api.routers import get_data_router
        
        # Create an app
        app = API()

        # Add the data router
        router = get_data_router()
        app.add_router(router)

        # Host app at https://localhost:8000
        # Try it at https://localhost:8000/docs
        # app.start()
    """

    # (get_data_router_restricted) Set defaults for restricted tables
    create_route_restricted_tables = create_route_restricted_tables if create_route_restricted_tables else restricted_tables
    delete_route_restricted_tables = delete_route_restricted_tables if delete_route_restricted_tables else restricted_tables
    id_route_restricted_tables = id_route_restricted_tables if id_route_restricted_tables else restricted_tables
    query_route_restricted_tables = query_route_restricted_tables if query_route_restricted_tables else restricted_tables
    update_route_restricted_tables = update_route_restricted_tables if update_route_restricted_tables else restricted_tables

    # (get_data_router_user) Set defaults for current user func
    create_get_current_user = create_get_current_user if create_get_current_user else get_current_user
    delete_get_current_user = delete_get_current_user if delete_get_current_user else get_current_user
    id_get_current_user = id_get_current_user if id_get_current_user else get_current_user
    query_get_current_user = query_get_current_user if query_get_current_user else get_current_user
    update_get_current_user = update_get_current_user if update_get_current_user else get_current_user

    # (get_data_router_create) Create api router for data routes
    out = APIRouter(prefix=prefix, tags=tags, *args, **kwargs)

    # (get_data_router_manager) Create data manager func
    get_data_manager = create_data_manager_func(database=database, restricted_tables=restricted_tables)

    # (get_data_router_create) Add create route to data router
    if enable_create_route:
        @out.post(create_route_path, **create_route_kwargs)
        async def create_data(
            dataset: str = Query(..., description='Name of the dataset to create - the request body is used to upload JSON data in the form of "[{col: val, col2: val2, ...}, {col: val, col2: val2, ...}]", where each key represents a variable and its corresponding value. Objects in this list should have the same keys.'),
            data: List[Dict[str, Any]] = Body(...),
            data_manager = Depends(get_data_manager),
            user = Depends(create_get_current_user)
        ):
            data_manager.create(dataset=dataset, data=data)

    # (get_data_router_delete) Add delete route to data router
    if enable_delete_route:
        @out.delete(delete_route_path, **delete_route_kwargs)
        async def delete_data(
            dataset: str = Query(..., description='Name of the dataset to delete data from'),
            where: Optional[List[str]] = Query(None, description='Where statements to filter data to remove in the form of "variable operator value" (e.g. "var < 3") - valid operators are: =, >, >=, >, <, <=, !=, LIKE'),
            where_boolean: Optional[str] = Query('AND', alias='where-boolean', description='Either "AND" or "OR" to combine where statements'),
            delete_all: Optional[bool] = Query(False, description='Whether to remove the entire dataset or not'),
            data_manager = Depends(get_data_manager),
            user = Depends(delete_get_current_user)
        ):
            data_manager.delete(dataset=dataset, where=where, where_boolean=where_boolean, delete_all=delete_all)

    # (get_data_router_id) Add id route to data router
    if enable_id_route:
        @out.get(id_route_path, **id_route_kwargs)
        async def get_data_by_id(
            dataset: str = Query(..., description='Name of the dataset'),
            id: str = Query(..., description='Identifier value to retrieve a specific document in the dataset'),
            id_variable: Optional[str] =  Query('id', description='Identifier variable name for the dataset'),
            data_manager = Depends(get_data_manager),
            user = Depends(id_get_current_user)
        ):
            where = [f'{id_variable} = {id}']
            response = data_manager.get(dataset=dataset, where=where)
            return response

    # (get_data_router_query) Add query route to data router
    if enable_query_route:
        @out.get(query_route_path, **query_route_kwargs)
        async def query_data(
            dataset: str = Query(..., description='Name of the dataset to query'),
            select: Optional[List[str]] = Query(None, description='Variables to include'),
            where: Optional[List[str]] = Query(None, description='Where statements to filter data in the form of "variable operator value" (e.g. "var < 3") - valid operators are: =, >, >=, >, <, <=, !=, LIKE'),
            group_by: Optional[List[str]] = Query(None, alias='group-by', description='Variable names to group by - should be used with aggregate and aggregate_func parameters'),
            aggregate: Optional[List[str]] = Query(None, description='Variable names to aggregate with the same order as the aggregate_func parameter'),
            aggregate_func: Optional[List[str]] = Query(None, alias='aggregate-func', description='Aggregate functions in the same order as the aggregate parameter'),
            order_by: Optional[List[str]] = Query(None, alias='order-by', description='Variable names to order by in the same order as parameter order_by_sort'),
            order_by_sort: Optional[List[str]] = Query(None, alias='order-by-sort', description='Either "asc" for ascending or "desc" for descending order in the same order as parameter order_by'),
            limit: Optional[int] = Query(None, description='Number of items to return'),
            where_boolean: Optional[str] = Query('AND', alias='where-boolean', description='Either "AND" or "OR" to combine where statements'),
            data_manager = Depends(get_data_manager),
            user = Depends(query_get_current_user)
        ):
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
                where_boolean=where_boolean
            )
            return response
    
    # (get_data_router_update) Add update route to data router
    if enable_update_route:
        @out.put(update_route_path, **update_route_kwargs)
        async def update_data(
            dataset: str = Query(..., description='Name of the dataset to update - the request body is used to upload JSON data in the form of "{key: value, key2: value2, ... }" where each key is a variable name and each value is the new value to use (matching the where parameter)'),
            data: Dict[str, Any] = Body(...),
            where: List[str] = Query(..., description='Where statements to filter data to update in the form of "variable operator value" (e.g. "var < 3") - valid operators are: =, >, >=, >, <, <=, !=, LIKE'),
            data_manager = Depends(get_data_manager),
            user = Depends(update_get_current_user)
        ):
            data_manager.update(dataset=dataset, data=data, where=where)
    return out
