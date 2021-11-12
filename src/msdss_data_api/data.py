from fastapi import HTTPException
from msdss_base_database import Database

DEFAULT_RESTRICTED_TABLES = ['data', 'user']

class Datasets:
    """
    Class to manage datasets in a database.
    
    Parameters
    ----------
    database : :class:`msdss_base_database:msdss_base_database.core.Database`
        Database object to use for creating data.
    handler : :class:`msdss_data_api.data.DatasetsHandler` or None
        Handler for handling dataset events. If ``None``, one will be created using the ``database`` parameter.
    
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
        ds = Datasets(database=db)

        # Check if the table exists and drop if it does
        if db.has_table("test_table"):
            db.drop_table("test_table")

        # Create sample data
        data = {
            'id': [1, 2, 3],
            'column_one': ['a', 'b', 'c'],
            'column_two': [2, 4, 6]
        }
        ds.create('test_table', data)

        # Query sample data
        result = ds.get('test_table')

        # Update sample data
        new_data = {'column_one': 'UPDATED'}
        ds.update('test_table', new_data, where=['id > 1'])

        # Delete sample data
        ds.delete('test_table', where=['id = 1'])

        # Delete the entire dataset
        ds.delete('test_table', delete_all=True)
    """
    def __init__(self, database=Database(), handler=None):
        self.database = database
        self.handler = handler if handler else DatasetsHandler(database=database)

    def create(self, dataset, data):
        """
        Create a dataset.

        See :meth:`msdss_base_database:msdss_base_database.core.Database.insert`.
        
        Parameters
        ----------
        dataset : str
            Name of the dataset or table to hold the data.
        data : dict(list)
            Data to insert into the table. Should be a dictionary of lists, where each key is a column name and each list represents values in the order of rows of the table.
        
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
            ds = Datasets(database=db)

            # Check if the table exists and drop if it does
            if db.has_table("test_table"):
                db.drop_table("test_table")

            # Create sample data
            data = {
                'id': [1, 2, 3],
                'column_one': ['a', 'b', 'c'],
                'column_two': [2, 4, 6]
            }
            ds.create('test_table', data)
        """
        self.handler.handle_write(dataset)
        self.database.insert(dataset, data)

    def delete(self, dataset, where=None, where_boolean='AND', delete_all=False):
        """
        Delete a dataset.

        See :meth:`msdss_base_database:msdss_base_database.core.Database.delete`.
        
        Parameters
        ----------
        dataset : str
            Name of the dataset or table in the database to delete.
        where : list(str)
            list of where statements the form of ``column operator value`` to further filter individual values or rows for deleting.
            
            * Operators are one of: ``=``, ``>``, ``>=``, ``>``, ``<``, ``<=``, ``!='', ``LIKE``
            * Example: ``'column_two < 3'``

        where_boolean : str
            One of AND or OR to combine where statements with. Defaults to AND if not one of AND or OR.
        delete_all : bool
            Whether to remove the entire dataset or not.
        
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
            ds = Datasets(database=db)

            # Check if the table exists and drop if it does
            if db.has_table("test_table"):
                db.drop_table("test_table")

            # Create sample data
            data = {
                'id': [1, 2, 3],
                'column_one': ['a', 'b', 'c'],
                'column_two': [2, 4, 6]
            }
            ds.create('test_table', data)

            # Delete sample data
            ds.delete('test_table', where=['id = 1'])
            res = ds.get('test_table')
            print(res)

            # Delete the entire dataset
            ds.delete('test_table', delete_all=True)
        """
        self.handler.handle_read(dataset)
        if delete_all:
            self.database.drop_table(dataset)
        elif not delete_all and where is None:
            raise HTTPException(status_code=400, detail='Parameter where is required')
        else:
            where = [w.split() for w in where]
            self.handler.handle_where(where)
            self.database.delete(dataset, where=where, where_boolean=where_boolean)

    def get(
        self,
        dataset,
        select=None,
        where=None,
        group_by=None,
        aggregate=None,
        aggregate_func=None,
        order_by=None,
        order_by_sort=None,
        limit=None,
        where_boolean='AND'):
        """
        Query data from the database.

        See :meth:`msdss_base_database:msdss_base_database.core.Database.select`.
        
        Parameters
        ----------
        dataset : str
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
            
            # Setup objects
            db = Database()
            ds = Datasets(database=db)

            # Check if the table exists and drop if it does
            if db.has_table("test_table"):
                db.drop_table("test_table")

            # Create sample data
            data = {
                'id': [1, 2, 3],
                'column_one': ['a', 'b', 'c'],
                'column_two': [2, 4, 6]
            }
            ds.create('test_table', data)

            # Query the data from the database
            result = ds.get('test_table')
            print(result)
        """
        self.handler.handle_read(dataset)
        where = [w.split() for w in where]
        self.handler.handle_where(where)
        out = self.database.select(
            table=dataset,
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

    def update(self, dataset, data, where):
        """
        Update data from the database.

        See :meth:`msdss_base_database:msdss_base_database.core.Database.update`.
        
        Parameters
        ----------
        dataset : str
            Name of the table to update.
        data : dict
            Dictionary representing values to update if they match the ``where`` parameter requirements. Each key is a column and the value is the updated new value.
        where : list(str)
            list of where statements the form of ``column operator value`` to further filter individual values or rows.
            
            * Operators are one of: ``=``, ``>``, ``>=``, ``>``, ``<``, ``<=``, ``!='', ``LIKE``
            * Example: ``'column_two < 3'``
        
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
            ds = Datasets(database=db)

            # Check if the table exists and drop if it does
            if db.has_table("test_table"):
                db.drop_table("test_table")

            # Create sample data
            data = {
                'id': [1, 2, 3],
                'column_one': ['a', 'b', 'c'],
                'column_two': [2, 4, 6]
            }
            ds.create('test_table', data)

            # Update the data from the database
            new_data = {'column_one': 'UPDATED'}
            ds.update('test_table', new_data, where=['id > 1'])

            # See updated data
            result = ds.get('test_table', db)
            print(result)
        """
        self.handler.handle_read(dataset)
        where = [w.split() for w in where]
        self.handler.handle_where(where)
        self.database.update(table=dataset, where=where, values=data)

class DatasetsHandler:
    """
    Class to handle dataset events.
    
    Parameters
    ----------
    database : :class:`msdss_base_database:msdss_base_database.core.Database`
        Database object to use for managing datasets.
    
    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>
    
    Example
    -------
    .. jupyter-execute::

        from msdss_base_database import Database
        from msdss_data_api.data import *
        
        # Setup objects
        db = Database()
        ds = Datasets(database=db)
        ds_handler = DatasetsHandler(database=db)

        # Check if the table exists and drop if it does
        if db.has_table('test_table'):
            db.drop_table('test_table')

        # Check table before writing
        # Should raise no exceptions
        ds_handler.handle_write('test_table')

        # Create sample data
        data = {
            'id': [1, 2, 3],
            'column_one': ['a', 'b', 'c'],
            'column_two': [2, 4, 6]
        }
        ds.create('test_table', data)

        # Check table name
        # Should raise no exceptions
        ds_handler.handle_read('test_table')

        # Check table restrictions
        # Should raise no exceptions
        ds_handler.handle_restrictions('test_table')
    """
    def __init__(self, database=Database()):
        self.database = database

    def handle_read(self, dataset):
        """
        Handle a table read, checking for existence and restrictions.
        
        Parameters
        ----------
        dataset : str
            Name of the table to check.
        
        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>
        
        Example
        -------
        .. jupyter-execute::

            from msdss_base_database import Database
            from msdss_data_api.data import *
            
            # Setup objects
            db = Database()
            ds = Datasets(database=db)
            ds_handler = DatasetsHandler(database=db)

            # Check if the table exists and drop if it does
            if db.has_table('test_table'):
                db.drop_table('test_table')

            # Create sample data
            data = {
                'id': [1, 2, 3],
                'column_one': ['a', 'b', 'c'],
                'column_two': [2, 4, 6]
            }
            ds.create('test_table', data)

            # Check table name
            # Should raise no exceptions
            ds_handler.handle_read('test_table')
        """
        if not self.database.has_table(dataset):
            raise HTTPException(status_code=404, detail='Dataset not found')

    def handle_restrictions(self, dataset, restricted_tables=DEFAULT_RESTRICTED_TABLES):
        """
        Handle a table read, checking for existence and restrictions.
        
        Parameters
        ----------
        dataset : str
            Name of the table to check.
        restricted_tables : list(str)
            List of restricted table names that are not accessible. If any of these are accessed, a 401 unauthorized http exception will be thrown.
        
        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>
        
        Example
        -------
        .. jupyter-execute::

            from msdss_base_database import Database
            from msdss_data_api.data import *
            
            # Setup objects
            db = Database()
            ds = Datasets(database=db)
            ds_handler = DatasetsHandler(database=db)

            # Check if the table exists and drop if it does
            if db.has_table('test_table'):
                db.drop_table('test_table')

            # Create sample data
            data = {
                'id': [1, 2, 3],
                'column_one': ['a', 'b', 'c'],
                'column_two': [2, 4, 6]
            }
            ds.create('test_table', data)

            # Check table name
            # Should raise no exceptions
            ds_handler.handle_restrictions('test_table')
        """
        if dataset in restricted_tables:
            raise HTTPException(status_code=401)

    def handle_where(self, where_list):
        """
        Throw an exception if where statements do not match the expected format.
        
        Parameters
        ----------
        where_list : list(list(str))
            list of where statements the form of ``['column', 'operator', 'value']`` to further filter individual values or rows.
            
            * Operators are one of: ``=``, ``>``, ``>=``, ``>``, ``<``, ``<=``, ``!='', ``LIKE``
            * Example: ``['column_two', '<'. '3']'``
        
        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>
        
        Example
        -------
        .. jupyter-execute::

            from msdss_data_api.data import *

            ds_handler = DatasetsHandler(database=db)
            where_list = [['col', '<', '3'], ['col', '=', 'a']]

            # Should raise no exceptions
            ds_handler.handle_where(where_list)
        """
        if where_list:
            where_has_wrong_len = any([len(w) != 3 for w in where_list])
            if where_has_wrong_len:
                raise HTTPException(status_code=400, detail='Parameter where is formatted incorrectly - should be in the form of "variable operator value" e.g. "col < 3"')


    def handle_write(self, dataset):
        """
        Handle a table write, checking for existence and restrictions.
        
        Parameters
        ----------
        dataset : str
            Name of the table to check.
        
        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>
        
        Example
        -------
        .. jupyter-execute::

            from msdss_base_database import Database
            from msdss_data_api.data import *
            
            # Setup objects
            db = Database()
            ds = Datasets(database=db)
            ds_handler = DatasetsHandler(database=db)

            # Check if the table exists and drop if it does
            if db.has_table('test_table'):
                db.drop_table('test_table')

            # Check table name
            # Should raise no exceptions
            ds_handler.handle_write('test_table')

            # Create sample data
            data = {
                'id': [1, 2, 3],
                'column_one': ['a', 'b', 'c'],
                'column_two': [2, 4, 6]
            }
            ds.create('test_table', data)
        """
        if self.database.has_table(dataset):
            raise HTTPException(status_code=400, detail='Dataset already exists')
