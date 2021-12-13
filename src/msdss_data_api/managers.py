from datetime import datetime
from fastapi import HTTPException
from msdss_base_database import Database
from shlex import split

from .defaults import *
from .handlers import *

class DataManager:
    """
    Class to manage datasets in a database.
    
    Parameters
    ----------
    database : :class:`msdss_base_database:msdss_base_database.core.Database`
        Database object to use for creating data.
    handler : :class:`msdss_data_api.data.DataHandler` or None
        Handler for handling dataset events.
        If ``None``, dataset events will not be handled.
        Sets the handler database to be the parameter ``database``.
    
    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>
    
    Example
    -------
    .. jupyter-execute::

        from msdss_base_database import Database
        from msdss_data_api.managers import *
        
        # Setup database
        db = Database()
        dm = DataManager(database=db)

        # Check if the table exists and drop if it does
        if db.has_table("test_table"):
            db.drop_table("test_table")

        # Create sample data
        data = {
            'id': [1, 2, 3],
            'column_one': ['a', 'b', 'c'],
            'column_two': [2, 4, 6]
        }
        dm.create('test_table', data)

        # Query sample data
        result = dm.get('test_table')

        # Update sample data
        new_data = {'column_one': 'updated_at'}
        dm.update('test_table', new_data, where=['id > 1'])

        # Delete sample data
        dm.delete('test_table', where=['id = 1'])

        # Delete the entire dataset
        dm.delete('test_table', delete_all=True)
    """
    def __init__(self, database=Database(), handler=DataHandler()):
        self.database = database
        self.handler = handler
        if self.handler:
            self.handler.database = database

    def create(self, dataset, data):
        """
        Create a dataset.

        See :meth:`msdss_base_database:msdss_base_database.core.Database.insert`.
        
        Parameters
        ----------
        dataset : str
            Name of the dataset or table to hold the data.
        data : list(dict)
            Data to insert into the table. Should be a list of dictionaries with the same keys, where each key in each dict is a column name.
        
        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>
        
        Example
        -------
        .. jupyter-execute::

            from msdss_base_database import Database
            from msdss_data_api.managers import *
            
            # Setup database
            db = Database()
            dm = DataManager(database=db)

            # Check if the table exists and drop if it does
            if db.has_table("test_table"):
                db.drop_table("test_table")

            # Create sample data
            data = [
                {'id': 1, 'column_one': 'a', 'column_two': 2},
                {'id': 2, 'column_one': 'b', 'column_two': 4},
                {'id': 3, 'column_one': 'c', 'column_two': 6},
            ]
            dm.create('test_table', data)
        """
        if self.handler:
            self.handler.handle_restrictions(dataset)
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
            
            * Operators are one of

                .. jupyter-execute::
                    :hide-code:

                    from msdss_base_database.defaults import DEFAULT_SUPPORTED_OPERATORS
                    for operator in DEFAULT_SUPPORTED_OPERATORS:
                        print(operator)

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
            from msdss_data_api.managers import *
            
            # Setup database
            db = Database()
            dm = DataManager(database=db)

            # Check if the table exists and drop if it does
            if db.has_table("test_table"):
                db.drop_table("test_table")

            # Create sample data
            data = [
                {'id': 1, 'column_one': 'a', 'column_two': 2},
                {'id': 2, 'column_one': 'b', 'column_two': 4},
                {'id': 3, 'column_one': 'c', 'column_two': 6},
            ]
            dm.create('test_table', data)

            # Delete sample data
            dm.delete('test_table', where=['id = 1'])
            res = dm.get('test_table')
            print(res)

            # Delete the entire dataset
            dm.delete('test_table', delete_all=True)
        """

        # (DataManager_delete_handle) Handle delete operation on data
        where = [split(w) for w in where] if where else where
        if self.handler:
            self.handler.handle_delete(dataset, where, delete_all)

        # (DataManager_delete_run) Delete data
        if delete_all:
            self.database.drop_table(dataset)
        else:
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
        offset=None,
        where_boolean='AND',
        *args, **kwargs):
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
            
            * Operators are one of

                .. jupyter-execute::
                    :hide-code:

                    from msdss_base_database.defaults import DEFAULT_SUPPORTED_OPERATORS
                    for operator in DEFAULT_SUPPORTED_OPERATORS:
                        print(operator)

            * Example: ``'column_two < 3'``
        
        group_by : list(str) or None
            Single or list of column names to group by. This should be used with ``aggregate`` and ``aggregate_func``.
        aggregate : list(str) or None
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
        offset : int or None
            Number of rows to skip.
        where_boolean : str
            One of ``AND`` or ``OR`` to combine ``where`` statements with. Defaults to ``AND`` if not one of ``AND`` or ``OR``.
        *args, **kwargs
            Additional arguments passed to :meth:`msdss_base_database:msdss_base_database.core.Database.select`.
        
        Returns
        -------
        list(dict)
            A list of dicts where each key is the column name.

        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>

        Example
        -------
        .. jupyter-execute::

            from msdss_base_database import Database
            from msdss_data_api.managers import *
            
            # Setup objects
            db = Database()
            dm = DataManager(database=db)

            # Check if the table exists and drop if it does
            if db.has_table("test_table"):
                db.drop_table("test_table")

            # Create sample data
            data = [
                {'id': 1, 'column_one': 'a', 'column_two': 2},
                {'id': 2, 'column_one': 'b', 'column_two': 4},
                {'id': 3, 'column_one': 'c', 'column_two': 6},
            ]
            dm.create('test_table', data)

            # Query the data from the database
            result = dm.get('test_table')
            print(result)
        """

        # (DataManager_get_handle) Handle get operation on data
        where = [split(w) for w in where] if where else where
        if self.handler:
            self.handler.handle_read(dataset)
            self.handler.handle_where(where)

        # (DataManager_get_run) Query the database
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
            offset=offset,
            where_boolean=where_boolean,
            *args, **kwargs
        ).to_dict(orient='records')
        return out

    def get_columns(self, dataset):
        """
        Get number of columns for a dataset.

        See :meth:`msdss_base_database:msdss_base_database.core.Database.columns`.
        
        Parameters
        ----------
        dataset : str
            Name of the dataset or table in the database.

        Returns
        -------
        int
            Number of columns for the dataset.
        
        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>
        
        Example
        -------
        .. jupyter-execute::

            from msdss_base_database import Database
            from msdss_data_api.managers import *
            
            # Setup database
            db = Database()
            dm = DataManager(database=db)

            # Check if the table exists and drop if it does
            if db.has_table("test_table"):
                db.drop_table("test_table")

            # Create sample data
            data = [
                {'id': 1, 'column_one': 'a', 'column_two': 2},
                {'id': 2, 'column_one': 'b', 'column_two': 4},
                {'id': 3, 'column_one': 'c', 'column_two': 6},
            ]
            dm.create('test_table', data)

            # Get num of cols
            columns = dm.get_columns('test_table')
            print(f'columns: {columns}')
        """
        if self.handler:
            self.handler.handle_read(dataset)
        out = self.database.columns(dataset)
        return out

    def get_rows(self, dataset):
        """
        Get number of rows for a dataset.

        See :meth:`msdss_base_database:msdss_base_database.core.Database.rows`.
        
        Parameters
        ----------
        dataset : str
            Name of the dataset or table in the database.

        Returns
        -------
        int
            Number of rows for the dataset.
        
        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>
        
        Example
        -------
        .. jupyter-execute::

            from msdss_base_database import Database
            from msdss_data_api.managers import *
            
            # Setup database
            db = Database()
            dm = DataManager(database=db)

            # Check if the table exists and drop if it does
            if db.has_table("test_table"):
                db.drop_table("test_table")

            # Create sample data
            data = [
                {'id': 1, 'column_one': 'a', 'column_two': 2},
                {'id': 2, 'column_one': 'b', 'column_two': 4},
                {'id': 3, 'column_one': 'c', 'column_two': 6},
            ]
            dm.create('test_table', data)

            # Get num of rows
            rows = dm.get_rows('test_table')
            print(f'rows: {rows}')
        """
        if self.handler:
            self.handler.handle_read(dataset)
        out = self.database.rows(dataset)
        return out

    def insert(self, dataset, data):
        """
        Create a dataset.

        See :meth:`msdss_base_database:msdss_base_database.core.Database.insert`.
        
        Parameters
        ----------
        dataset : str
            Name of the dataset or table to hold the data.
        data : list(dict)
            Data to insert into the table. Should be a list of dictionaries with the same keys, where each key in each dict is a column name.
        
        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>
        
        Example
        -------
        .. jupyter-execute::

            from msdss_base_database import Database
            from msdss_data_api.managers import *
            
            # Setup database
            db = Database()
            dm = DataManager(database=db)

            # Check if the table exists and drop if it does
            if db.has_table("test_table"):
                db.drop_table("test_table")

            # Create sample data
            data = [
                {'id': 1, 'column_one': 'a', 'column_two': 2},
                {'id': 2, 'column_one': 'b', 'column_two': 4},
                {'id': 3, 'column_one': 'c', 'column_two': 6},
            ]
            dm.create('test_table', data)

            # Insert more data
            more_data = [
                {'id': 4, 'column_one': 'e', 'column_two': 8},
                {'id': 5, 'column_one': 'f', 'column_two': 10},
                {'id': 6, 'column_one': 'g', 'column_two': 12},
            ]
            dm.insert('test_table', more_data)
        """
        if self.handler:
            self.handler.handle_restrictions(dataset)
            self.handler.handle_read(dataset)
        self.database.insert(dataset, data)

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
            
            * Operators are one of

                .. jupyter-execute::
                    :hide-code:

                    from msdss_base_database.defaults import DEFAULT_SUPPORTED_OPERATORS
                    for operator in DEFAULT_SUPPORTED_OPERATORS:
                        print(operator)
                            
            * Example: ``'column_two < 3'``
        
        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>

        Example
        -------
        .. jupyter-execute::

            from msdss_base_database import Database
            from msdss_data_api.managers import *
            
            # Setup database
            db = Database()
            dm = DataManager(database=db)

            # Check if the table exists and drop if it does
            if db.has_table("test_table"):
                db.drop_table("test_table")

            # Create sample data
            data = [
                {'id': 1, 'column_one': 'a', 'column_two': 2},
                {'id': 2, 'column_one': 'b', 'column_two': 4},
                {'id': 3, 'column_one': 'c', 'column_two': 6},
            ]
            dm.create('test_table', data)

            # Update the data from the database
            new_data = {'column_one': 'updated_at'}
            dm.update('test_table', new_data, where=['id > 1'])

            # See updated data
            result = dm.get('test_table')
            print(result)
        """
        where = [split(w) for w in where]
        if self.handler:
            self.handler.handle_update(dataset, data, where)
        self.database.update(table=dataset, where=where, values=data)

class MetadataManager:
    """
    Class to manage metadata in a database.
    
    Parameters
    ----------
    data_manager : :class:`msdss_data_api.managers.DataManager`
        Data manager object for managing datasets in a database.
        The restricted tables for the handler will be set to ``[]`` while the only permitted table will be the table name of the parameter ``table``.
    table : str
        The name of the table to store the metadata.
    columns : list(dict) or list(list)
        List of dict (kwargs) or lists (positional args) that are passed to sqlalchemy.schema.Column. See parameter ``columns`` in :meth:`msdss_base_database:msdss_base_database.core.create_table`.
        This defines the table to store the metadata, where the default is:

        .. jupyter-execute::
            :hide-code:

            from msdss_data_api.defaults import *
            from pprint import pprint

            pprint(DEFAULT_METADATA_COLUMNS)

    Attributes
    ----------
    table : str
        The name of the metadata table.
    data_manager : :class:`msdss_data_api.managers.DataManager`
        Same as parameter ``data_manager``.
    
    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>
    
    Example
    -------
    .. jupyter-execute::

        from datetime import datetime
        from msdss_base_database import Database
        from msdss_data_api.managers import *
        from msdss_data_api.defaults import *
        
        # Setup database
        db = Database()

        # Check if the metadata table exists and drop if it does
        if db.has_table(DEFAULT_METADATA_TABLE):
            db.drop_table(DEFAULT_METADATA_TABLE)

        # Setup metadata manager
        data_manager = DataManager(database=db)
        mdm = MetadataManager(data_manager)

        # Add metadata
        metadata = [{
            'title': 'Testing Data',
            'description': 'Data used for testing',
            'source': 'Automatically generated from Python',
            'created_by': 'msdss',
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }]
        mdm.create('test_data', metadata)

        # Get metadata
        metadata_get = mdm.get('test_data')
        
        # Search metadata
        search_results = mdm.search(where=['title = "Testing Data"'])

        # Update metadata
        mdm.update('test_data', {'description': 'NEW DESCRIPTION'})

        # Delete metadata
        mdm.delete('test_data')
    """
    def __init__(
        self,
        data_manager=DataManager(),
        table=DEFAULT_METADATA_TABLE,
        columns=DEFAULT_METADATA_COLUMNS):
        
        # (MetadataManager_table) Create table if not exists
        if not data_manager.database.has_table(table):
            data_manager.database.create_table(table, columns)
        
        # (MetadataManager_attr) Set attributes
        self.table = table

        # (MetadataManager_manager) Setup data manager
        self.data_manager = data_manager
        self.data_manager.handler.permitted_tables = [self.table]
        self.data_manager.handler.restricted_tables = []

    def create(self, dataset, data):
        """
        Create a metadata entry.

        See :meth:`msdss_data_api.managers.DataManager.delete`.
        
        Parameters
        ----------
        dataset : str
            Name of the dataset to add metadata for.
        data : list(dict) or dict
            Metadata to insert into the table, where each key represents a metadata descriptor. The default key names are:

            .. jupyter-execute::
                :hide-code:

                from msdss_data_api.defaults import *
                from pprint import pprint

                pprint(DEFAULT_METADATA_COLUMNS)

        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>

        Example
        -------
        .. jupyter-execute::

            from datetime import datetime
            from pprint import pprint
            from msdss_base_database import Database
            from msdss_data_api.managers import *
            from msdss_data_api.defaults import *
            
            # Setup database
            db = Database()

            # Check if the metadata table exists and drop if it does
            if db.has_table(DEFAULT_METADATA_TABLE):
                db.drop_table(DEFAULT_METADATA_TABLE)

            # Setup metadata manager
            data_manager = DataManager(database=db)
            mdm = MetadataManager()

            # Add metadata
            metadata = [{
                'title': 'Testing Data',
                'description': 'Data used for testing',
                'source': 'Automatically generated from Python',
                'created_by': 'msdss',
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }]
            mdm.create('test_data', metadata)

            # Print results
            tb = mdm.search()
            pprint(tb)
        """
        data = [data] if isinstance(data, dict) else data
        data[0]['dataset'] = dataset
        self.data_manager.insert(self.table, data)

    def delete(self, dataset):
        """
        Delete a metadata entry.

        See :meth:`msdss_data_api.managers.DataManager.delete`.
        
        Parameters
        ----------
        dataset : str
            Name of the dataset to delete metadata for.

        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>

        Example
        -------
        .. jupyter-execute::

            from datetime import datetime
            from pprint import pprint
            from msdss_base_database import Database
            from msdss_data_api.managers import *
            from msdss_data_api.defaults import *
            
            # Setup database
            db = Database()

            # Check if the metadata table exists and drop if it does
            if db.has_table(DEFAULT_METADATA_TABLE):
                db.drop_table(DEFAULT_METADATA_TABLE)

            # Setup metadata manager
            data_manager = DataManager(database=db)
            mdm = MetadataManager()

            # Add metadata
            metadata = [{
                'dataset': 'test_data',
                'title': 'Testing Data',
                'description': 'Data used for testing',
                'source': 'Automatically generated from Python',
                'created_by': 'msdss',
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }]
            mdm.create('test_data', metadata)
            before_delete = mdm.search()

            # Delete metadata
            mdm.delete('test_data')
            after_delete = mdm.search()

            # Print results
            print('before_delete:\\n')
            pprint(before_delete)
            print('\\nafter_delete:\\n')
            pprint(after_delete)
        """
        where = [f'dataset = {dataset}']
        self.data_manager.delete(self.table, where=where)

    def get(self, dataset):
        """
        Search metadata entries.

        See :meth:`msdss_data_api.managers.DataManager.get`.
        
        Parameters
        ----------
        dataset : str
            Name of the dataset to get metadata for.

        Returns
        -------
        list(dict)
            A list of dicts where each key is the column name.

        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>

        Example
        -------
        .. jupyter-execute::

            from datetime import datetime
            from pprint import pprint
            from msdss_base_database import Database
            from msdss_data_api.managers import *
            from msdss_data_api.defaults import *
            
            # Setup database
            db = Database()

            # Check if the metadata table exists and drop if it does
            if db.has_table(DEFAULT_METADATA_TABLE):
                db.drop_table(DEFAULT_METADATA_TABLE)

            # Setup metadata manager
            data_manager = DataManager(database=db)
            mdm = MetadataManager()

            # Add metadata
            metadata = [{
                'title': 'Testing Data',
                'description': 'Data used for testing',
                'source': 'Automatically generated from Python',
                'created_by': 'msdss',
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }]
            mdm.create('test_data', metadata)

            # Get metadata
            metadata_get = mdm.get('test_data')
            pprint(metadata_get)
        """
        where = [f'dataset = {dataset}']
        out = self.data_manager.get(self.table, where=where)
        return out

    def search(self, *args, **kwargs):
        """
        Search metadata entries.

        See :meth:`msdss_data_api.managers.DataManager.get`.
        
        Parameters
        ----------
        *args, **kwargs
            Additional arguments passed to :meth:`msdss_data_api.managers.DataManager.get` except for parameter ``table``.

        Returns
        -------
        list(dict)
            A dict of lists where each key is the column name and each list contains the values for columns in the order of the rows of the table.

        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>

        Example
        -------
        .. jupyter-execute::

            from datetime import datetime
            from pprint import pprint
            from msdss_base_database import Database
            from msdss_data_api.managers import *
            from msdss_data_api.defaults import *
            
            # Setup database
            db = Database()

            # Check if the metadata table exists and drop if it does
            if db.has_table(DEFAULT_METADATA_TABLE):
                db.drop_table(DEFAULT_METADATA_TABLE)

            # Setup metadata manager
            data_manager = DataManager(database=db)
            mdm = MetadataManager()

            # Add metadata
            metadata = [{
                'title': 'Testing Data',
                'description': 'Data used for testing',
                'source': 'Automatically generated from Python',
                'created_by': 'msdss',
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }]
            mdm.create('test_data', metadata)

            # Search metadata
            results = mdm.search(where=['title = "Testing Data"'])
            pprint(results)
        """
        out = self.data_manager.get(self.table, *args, **kwargs)
        return out

    def update(self, dataset, data):
        """
        Update metadata entry.

        See :meth:`msdss_data_api.managers.DataManager.update`.
        
        Parameters
        ----------
        dataset : str
            Name of the dataset to update.
        data : dict
            Dictionary representing values to update.
        
        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>

        Example
        -------
        .. jupyter-execute::

            from datetime import datetime
            from pprint import pprint
            from msdss_base_database import Database
            from msdss_data_api.managers import *
            from msdss_data_api.defaults import *
            
            # Setup database
            db = Database()

            # Check if the metadata table exists and drop if it does
            if db.has_table(DEFAULT_METADATA_TABLE):
                db.drop_table(DEFAULT_METADATA_TABLE)

            # Setup metadata manager
            data_manager = DataManager(database=db)
            mdm = MetadataManager()

            # Add metadata
            metadata = [{
                'title': 'Testing Data',
                'description': 'Data used for testing',
                'source': 'Automatically generated from Python',
                'created_by': 'msdss',
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }]
            mdm.create('test_data', metadata)
            before_update = mdm.get('test_data')

            # Update metadata
            mdm.update('test_data', {'description': 'NEW DESCRIPTION'})
            after_update = mdm.get('test_data')

            # Print results
            print('before_update:\\n')
            pprint(before_update)
            print('\\nafter_update:\\n')
            pprint(after_update)
        """
        where = [f'dataset = {dataset}']
        self.data_manager.update(self.table, data, where=where)

    def updated_at(self, dataset, dt=None):
        """
        Set last updated entry for a dataset.

        See :meth:`msdss_data_api.managers.MetadataManager.update`.
        
        Parameters
        ----------
        dataset : str
            Name of the dataset to update.
        dt : :class:`datetime.datetime` or None
            Datetime object representing the last updated time. If ``None``, will be set to now.
        
        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>

        Example
        -------
        .. jupyter-execute::

            from datetime import datetime
            from pprint import pprint
            from msdss_base_database import Database
            from msdss_data_api.managers import *
            from msdss_data_api.defaults import *
            
            # Setup database
            db = Database()

            # Check if the metadata table exists and drop if it does
            if db.has_table(DEFAULT_METADATA_TABLE):
                db.drop_table(DEFAULT_METADATA_TABLE)

            # Setup metadata manager
            data_manager = DataManager(database=db)
            mdm = MetadataManager()

            # Add metadata
            metadata = [{
                'title': 'Testing Data',
                'description': 'Data used for testing',
                'source': 'Automatically generated from Python',
                'created_by': 'msdss',
                'created_at': datetime.now(),
            }]
            mdm.create('test_data', metadata)
            before_update = mdm.get('test_data')

            # Update metadata
            mdm.updated_at('test_data', datetime.now())
            after_update = mdm.get('test_data')

            # Print results
            print('before_update:\\n')
            pprint(before_update)
            print('\\nafter_update:\\n')
            pprint(after_update)
        """
        data = {'updated_at': dt if dt else datetime.now()}
        self.update(dataset, data)