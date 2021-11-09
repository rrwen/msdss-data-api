from fastapi import HTTPException
from msdss_base_database import Database

DEFAULT_RESTRICTED_TABLES = ['user']

def _format_where_statements(where):
    """
    Format where statements and throw an exception if it does not match the expected format.
    
    Parameters
    ----------
    where : list(str)
        list of where statements the form of ``column operator value`` to further filter individual values or rows.
        
        * Operators are one of: ``=``, ``>``, ``>=``, ``>``, ``<``, ``<=``, ``!='', ``LIKE``
        * Example: ``'column_two < 3'``

    Returns
    -------
    list(list(str))
        List of where statements divided into column, operator, value format for each list of lists.
    
    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>
    
    Example
    -------
    .. jupyter-execute::

        from msdss_data_api.data import _format_where_statements

        where = ['col < 3', 'col = a']
        where_formatted = _format_where_statements(where)

        print(where_formatted)
    """
    out = [w.split() for w in where]
    where_has_wrong_len = any([len(w) != 3 for w in out])
    if where_has_wrong_len:
        raise HTTPException(status_code=400, detail='Parameter where is formatted incorrectly - should be in the form of "variable operator value" e.g. "col < 3"')
    return out

def handle_table_read(table, db=Database()):
    """
    Handle a table read, checking for existence and restrictions.
    
    Parameters
    ----------
    table : str
        Name of the table to check.
    db : :class:`msdss_base_database:msdss_base_database.core.Database`
        Database object to use for checking table.
    
    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>
    
    Example
    -------
    .. jupyter-execute::

        from msdss_base_database import Database
        from msdss_data_api.data import *
        
        # Setup database
        db = Database()

        # Check if the table exists and drop if it does
        if db.has_table("test_table"):
            db.drop_table("test_table")

        # Create sample data
        data = {
            'id': [1, 2, 3],
            'column_one': ['a', 'b', 'c'],
            'column_two': [2, 4, 6]
        }
        create_table('test_table', data, db=db)

        # Check table name
        # Should throw no errors
        handle_table_read('test_table', db=db)
    """
    if not db.has_table(table):
        raise HTTPException(status_code=404, detail='Data not found')

def handle_table_restrictions(table, restricted_tables=DEFAULT_RESTRICTED_TABLES, db=Database()):
    """
    Handle a table read, checking for existence and restrictions.
    
    Parameters
    ----------
    table : str
        Name of the table to check.
    restricted_tables : list(str)
        List of restricted table names that are not accessible. If any of these are accessed, a 401 unauthorized http exception will be thrown.
    db : :class:`msdss_base_database:msdss_base_database.core.Database`
        Database object to use for checking table.
    
    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>
    
    Example
    -------
    .. jupyter-execute::

        from msdss_base_database import Database
        from msdss_data_api.data import *
        
        # Setup database
        db = Database()

        # Check if the table exists and drop if it does
        if db.has_table("test_table"):
            db.drop_table("test_table")

        # Create sample data
        data = {
            'id': [1, 2, 3],
            'column_one': ['a', 'b', 'c'],
            'column_two': [2, 4, 6]
        }
        create_table('test_table', data, db=db)

        # Check table name
        # Should throw no errors
        handle_table_restrictions('test_table', db=db)
    """
    if table in restricted_tables:
        raise HTTPException(status_code=401)

def handle_table_write(table, db=Database()):
    """
    Handle a table write, checking for existence and restrictions.
    
    Parameters
    ----------
    table : str
        Name of the table to check.
    db : :class:`msdss_base_database:msdss_base_database.core.Database`
        Database object to use for checking table.
    
    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>
    
    Example
    -------
    .. jupyter-execute::

        from msdss_base_database import Database
        from msdss_data_api.data import *
        
        # Setup database
        db = Database()

        # Check if the table exists and drop if it does
        if db.has_table("test_table"):
            db.drop_table("test_table")

        # Check table name
        # Should throw no errors
        handle_table_write('test_table', db=db)
    """
    if db.has_table(table):
        raise HTTPException(status_code=400, detail='Name already exists')

def create_table(table, data, db=Database()):
    """
    Create a dataset.

    See :meth:`msdss_base_database:msdss_base_database.core.Database.insert`.
    
    Parameters
    ----------
    table : str
        Name of the table to hold the data.
    data : dict(list)
        Data to insert into the table. Should be a dictionary of lists, where each key is a column name and each list represents values in the order of rows of the table.
    db : :class:`msdss_base_database:msdss_base_database.core.Database`
        Database object to use for creating data.
    *args, **kwargs
        Additional arguments passed to :meth:`msdss_base_database.core.Database._write`. Except that ``if_exists`` is always set to ``append``.
    
    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>
    
    Example
    -------
    .. jupyter-execute::

        from msdss_base_database import Database
        from msdss_data_api.data import *
        
        # Setup database
        db = Database()

        # Check if the table exists and drop if it does
        if db.has_table("test_table"):
            db.drop_table("test_table")

        # Create sample data
        data = {
            'id': [1, 2, 3],
            'column_one': ['a', 'b', 'c'],
            'column_two': [2, 4, 6]
        }
        create_table('test_table', data, db=db)
    """
    db.insert(table, data)

def query_table(
    table,
    select=None,
    where=None,
    group_by=None,
    aggregate=None,
    aggregate_func=None,
    order_by=None,
    order_by_sort=None,
    limit=None,
    where_boolean='AND',
    db=Database()):
    """
    Query data from the database.

    See :meth:`msdss_base_database:msdss_base_database.core.Database.select`.
    
    Parameters
    ----------
    table : str
        Name of the database table to query from.
    select : list(str) or None
        List of column names or a single column name to filter or select from the table. If ``None`` then all columns will be selected.
    where : list(str)
        list of where statements the form of ``column operator value`` to further filter individual values or rows.
        
        * Operators are one of: ``=``, ``>``, ``>=``, ``>``, ``<``, ``<=``, ``!='', ``LIKE``
        * Example: ``'column_two < 3'``
    
    group_by : slist(str) or None
        Single or list of column names to group by. This should be used with ``aggregate`` and ``aggregate_func``.
    aggregate : slist(str) or None
        Single or list of column names to aggregate using the ``aggregate_func``. This should be used with ``group_by`` and ``aggregate_func``.
    aggregate_func : list(str)
        Function name (such as 'count' or 'sum') from :class:`sqlalchemy:sqlalchemy.sql.functions.Function` for aggregating records from each ``aggregate`` column.
        If a list of str, then it must have the same number of elements as ``aggregate`` or else only the shortest length list will be used.
    order_by : list(str) or None
        Single or list of column names to order or sort by.
    order_by_sort : list(str)
        Sort the records in increasing or decreasing order by each column in ``order_by``, where the value can be one of 'asc' for ascending or 'desc' for descending'.
        If a list of str, then it must have the same number of elements as ``order_by`` or else only the shortest length list will be used.
    limit : int or None
        Integer number to limit the number of rows returned.
    where_boolean : str
        One of ``AND`` or ``OR`` to combine ``where`` statements with. Defaults to ``AND`` if not one of ``AND`` or ``OR``.
    db : :class:`msdss_base_database:msdss_base_database.core.Database`
        Database object to use for querying data.
    
    Returns
    -------
    dict(list)
        A dict of lists where each key is the column name and each list contains the values for column in the order of the rows of the table.

    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>

    Example
    -------
    .. jupyter-execute::

        from msdss_base_database import Database
        from msdss_data_api.data import *
        
        # Setup database
        db = Database()

        # Check if the table exists and drop if it does
        if db.has_table("test_table"):
            db.drop_table("test_table")

        # Create sample data
        data = {
            'id': [1, 2, 3],
            'column_one': ['a', 'b', 'c'],
            'column_two': [2, 4, 6]
        }
        create_table('test_table', data, db=db)

        # Query the data from the database
        df = query_table('test_table', db=db)
        print(df)
    """

    # (query_table_where) Format where statements for query
    if where:
        where = _format_where_statements(where)

    # (query_table_return) Return the response data
    out = db.select(
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
    ).to_dict(orient='list')
    return out

def update_table(table, data, where, db=Database()):
    """
    Update data from the database.

    See :meth:`msdss_base_database:msdss_base_database.core.Database.update`.
    
    Parameters
    ----------
    table : str
            Name of the table to update.
    data : dict
        Dictionary representing values to update if they match the ``where`` parameter requirements. Each key is a column and the value is the updated new value.
    where : list(str)
        list of where statements the form of ``column operator value`` to further filter individual values or rows.
        
        * Operators are one of: ``=``, ``>``, ``>=``, ``>``, ``<``, ``<=``, ``!='', ``LIKE``
        * Example: ``'column_two < 3'``
    db : :class:`msdss_base_database:msdss_base_database.core.Database`
        Database object to use for querying data.
    
    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>

    Example
    -------
    .. jupyter-execute::

        from msdss_base_database import Database
        from msdss_data_api.data import *
        
        # Setup database
        db = Database()

        # Check if the table exists and drop if it does
        if db.has_table("test_table"):
            db.drop_table("test_table")

        # Create sample data
        data = {
            'id': [1, 2, 3],
            'column_one': ['a', 'b', 'c'],
            'column_two': [2, 4, 6]
        }
        create_table('test_table', data, db=db)

        # Query the data from the database
        new_data = {'column_one': 'UPDATED'}
        update_table('test_table', new_data, where=['id > 1'], db=db)

        # See updated data
        df = query_table('test_table', db=db)
        print(df)
    """
    if where:
        where = _format_where_statements(where)
    db.update(table=table, where=where, values=data)