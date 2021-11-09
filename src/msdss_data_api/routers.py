from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional

from . import data
from .tools import *

def get_data_router(
    get_data_db = create_data_db_func(),
    prefix='/data',
    tags=['data'],
    restricted_tables=DEFAULT_RESTRICTED_TABLES,
    enable_create_route=True,
    enable_query_route=True,
    create_route_path='/create/{table}',
    create_route_kwargs={},
    create_route_restricted_tables=None,
    query_route_path='/query/{table}',
    query_route_kwargs={},
    query_route_restricted_tables=None,
    *args, **kwargs):
    """
    Get a data router.
    
    Parameters
    ----------
    get_data_db : func
        Function yielding a :class:`msdss_base_database:msdss_base_database.core.Database` object. See :func:`msdss_data_api.tools.create_data_db_func`.
    prefix : str
        Prefix path to all routes belonging to this router.
    tags : list(str)
        Tags for all routes in this router.
    restricted_tables : list(str)
        List of restricted table names that are not accessible on this router. If any of these are accessed, a 401 unauthorized http exception will be thrown.
    enable_query_route : bool
        Whether to enable the query path for this router or not.
    enable_create_route : bool
        Whether to enable the create path for this router or not.
    create_route_path : str
        Path for the create route in this router. The full path will include the param ``prefix``. For example if ``query_route_path`` is ``/create/{table}`` and ``prefix`` is ``/data``, then the full path is ``/data/create/{table}``.
    create_route_kwargs : dict
        Additional arguments passed to :meth:`fastapi:fastapi.FastAPI.get` for the create route.
    create_route_restricted_tables : list(str) or None
        Same as parameter ``restricted_tables`` except router specific. If ``None``, will default to parameter ``restricted_tables``.
    query_route_path : str
        Path for the query route in this router. The full path will include the param ``prefix``. For example if ``query_route_path`` is ``/query/{table}`` and ``prefix`` is ``/data``, then the full path is ``/data/query/{table}``.
    query_route_kwargs : dict
        Additional arguments passed to :meth:`fastapi:fastapi.FastAPI.get` for the query route.
    query_route_restricted_tables : list(str)
        Same as parameter ``restricted_tables`` except router specific. If ``None``, will default to parameter ``restricted_tables``.
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

    # (get_data_router_vars) Format vars
    create_route_restricted_tables = create_route_restricted_tables if create_route_restricted_tables else restricted_tables
    query_route_restricted_tables = query_route_restricted_tables if query_route_restricted_tables else restricted_tables

    # (get_data_router_create) Create api router for data routes
    out = APIRouter(
        prefix=prefix,
        tags=tags,
        *args, **kwargs
    )

    # (get_data_router_query) Add query route to data router
    if enable_query_route:
        @out.get(query_route_path, **query_route_kwargs)
        async def query_data(
            table: str = Query(..., description='Name of the dataset or table to query'),
            select: Optional[List[str]] = Query(None, description='Columns to include'),
            where: Optional[List[str]] = Query(None, description='Where statements to filter data in the form of "column operator value" (e.g. "col < 3") - valid operators are: =, >, >=, >, <, <=, !=, LIKE'),
            group_by: Optional[List[str]] = Query(None, alias='group-by', description='Column names to group by - should be used with aggregate and aggregate_func parameters'),
            aggregate: Optional[List[str]] = Query(None, description='Column names to aggregate with the same order as the aggregate_func parameter'),
            aggregate_func: Optional[List[str]] = Query(None, alias='aggregate-func', description='Aggregate functions in the same order as the aggregate parameter'),
            order_by: Optional[List[str]] = Query(None, alias='order-by', description='Column names to order by in the same order as parameter order_by_sort'),
            order_by_sort: Optional[List[str]] = Query(None, alias='order-by-sort', description='Either "asc" for ascending or "desc" for descending order in the same order as parameter order_by'),
            limit: Optional[int] = Query(None, description='Number of rows to return'),
            where_boolean: Optional[str] = Query('AND', alias='where-boolean', description='Either "AND" or "OR" to combine where statements'),
            db = Depends(get_data_db)):

            data._handle_table_name(table, restricted_tables=query_route_restricted_tables, db=db)
            response = data.query_data(
                table=table,
                select=select,
                where=where,
                group_by=group_by,
                aggregate=aggregate,
                aggregate_func=aggregate_func,
                order_by=order_by,
                order_by_sort=order_by_sort,
                limit=limit,
                where_boolean=where_boolean,
                db=db
            )
            return response
    
    # (get_data_router_create) Add create route to data router
    if enable_create_route:
        @out.get(create_route_path, **create_route_kwargs)
        async def create_data(
            table: str = Query(..., description='Name of the dataset or table to query'),
            data : dict = Query(..., description='Data'),
            db = Depends(get_data_db)):

            data._handle_table_name(table, restricted_tables=create_route_restricted_tables, db=db)
            data.create_data(table=table, data=data, db=db)
    return out
