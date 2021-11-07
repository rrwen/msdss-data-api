from fastapi import APIRouter, Depends, HTTPException, Query
from msdss_base_database import Database
from msdss_users_api import UsersAPI
from typing import List, Optional

from .tools import create_data_db_func

def get_data_router(
    get_data_db = create_data_db_func(),
    prefix='/data',
    tags=['data'],
    use_query_route=True,
    query_route_kwargs={},
    query_route_path='/query/{table}',
    query_route_restricted_tables=['user'],
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
    enable_query_route : bool
        Whether to enable the query path for this router or not.
    query_route_kwargs : str
        Additional arguments passed to :meth:`fastapi:fastapi.FastAPI.get` for the query route.
    query_route_path : str
        Path for the query route in this router. The full path will include the param ``prefix``. For example if ``query_route_path`` is ``/query/{table}`` and ``prefix`` is ``/data``, then the full path is ``/data/query/{table}``.
    query_route_restricted_tables : list(str)
        List of restricted table names that are not accessible on this router. If any of these are accessed, a 401 unauthorized http exception will be thrown.
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

    # (get_data_router_create) Create api router for data routes
    out = APIRouter(
        prefix=prefix,
        tags=tags,
        *args, **kwargs
    )

    # (get_data_router_query) Add query route to data router
    if use_query_route:
        @out.get(query_route_path, **query_route_kwargs)
        async def query_data(
            table: str,
            select: Optional[List[str]] = Query(None),
            where_left: Optional[List[str]] = Query(None, alias='where-left'),
            where_op: Optional[List[str]] = Query(None, alias='where-op'),
            where_right: Optional[List[str]] = Query(None, alias='where-right'),
            group_by: Optional[List[str]] = Query(None, alias='group-by'),
            aggregate: Optional[List[str]] = Query(None),
            aggregate_func: Optional[List[str]] = Query(None, alias='aggregate-func'),
            order_by: Optional[List[str]] = Query(None, alias='order-by'),
            order_by_sort: Optional[List[str]] = Query(None, alias='order-by-sort'),
            limit: Optional[int] = None,
            where_boolean: Optional[str] = Query('AND', alias='where-boolean'),
            db = Depends(get_data_db)):

            # (get_data_router_query_table) Check if database has table or if table is restricted
            if not db.has_table(table):
                raise HTTPException(status_code=404, detail='Table not found')
            if table in query_route_restricted_tables:
                raise HTTPException(status_code=401)

            # (get_data_router_query_where) Format where statements for query
            where_lists = [where_left, where_op, where_right]
            where_not_exists = all([w is None for w in where_lists])
            if where_not_exists:
                where = None
            elif where_left is None:
                raise HTTPException(status_code=400, detail='Missing parameter where-left')
            elif where_op is None:
                raise HTTPException(status_code=400, detail='Missing parameter where-op')
            elif where_right is None:
                raise HTTPException(status_code=400, detail='Missing parameter where-right')
            else:
                where_lens_not_equal = any([len(w) != len(where_left) for w in where_lists])
                if where_lens_not_equal:
                    raise HTTPException(status_code=400, detail='Parameters where-left, where-op, and where-right are not of equal length')
                where = [statement for statement in zip(where_left, where_op, where_right)]

            # (get_data_router_query_return) Return the response data
            response = db.select(
                table=table,
                select=select,
                where=where,
                group_by=group_by,
                aggregate=aggregate,
                aggregate_func=aggregate_func,
                order_by=order_by,
                order_by_sort=order_by_sort,
                limit=limit,
                where_boolean=where_boolean
            ).to_dict(orient='records')
            return response
    return out
