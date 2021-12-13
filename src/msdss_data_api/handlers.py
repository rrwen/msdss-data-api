from fastapi import HTTPException
from msdss_base_database import Database
from msdss_base_database.defaults import DEFAULT_SUPPORTED_OPERATORS

from .defaults import *

class DataHandler:
    """
    Class to handle dataset events.
    
    Parameters
    ----------
    database : :class:`msdss_base_database:msdss_base_database.core.Database`
        Database object to use for managing datasets.
    permitted_tables : list(str)
        List of permitted table names that are only accessible. If any tables not in this list are accessed, a 401 unauthorized http exception will be thrown.
    restricted_tables : list(str)
        List of restricted table names that are not accessible. If any of these are accessed, a 401 unauthorized http exception will be thrown.
    
    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>
    
    Example
    -------
    .. jupyter-execute::

        from msdss_base_database import Database
        from msdss_data_api.handlers import *
        from msdss_data_api.managers import *
        
        # Setup objects
        db = Database()
        dm = DataManager(database=db)
        handler = DataHandler(database=db)

        # Check if the table exists and drop if it does
        if db.has_table('test_table'):
            db.drop_table('test_table')

        # Check table before writing
        # Should not raise exceptions
        handler.handle_write('test_table')

        # Create sample data
        data = [
            {'id': 1, 'column_one': 'a', 'column_two': 2},
            {'id': 2, 'column_one': 'b', 'column_two': 4},
            {'id': 3, 'column_one': 'c', 'column_two': 6},
        ]
        dm.create('test_table', data)

        # Check table name
        # Should not raise exceptions
        handler.handle_read('test_table')

        # Check table restrictions
        # Should not raise exceptions
        handler.handle_restrictions('test_table')
    """
    def __init__(self, database=Database(), permitted_tables=[], restricted_tables=DEFAULT_RESTRICTED_TABLES):
        self.database = database
        self.permitted_tables = permitted_tables
        self.restricted_tables = restricted_tables

    def handle_delete(self, dataset, where_list, delete_all):
        """
        Handle a table delete operation.
        
        Parameters
        ----------
        dataset : str
            Name of the table to check.
        where_list : list(list(str))
            list of where statements the form of ``['column', 'operator', 'value']`` to further filter individual values or rows.
            
            * Operators are one of:

                .. jupyter-execute::
                    :hide-code:

                    from msdss_base_database.defaults import DEFAULT_SUPPORTED_OPERATORS
                    for operator in DEFAULT_SUPPORTED_OPERATORS:
                        print(operator)

            * Example: ``['column_two', '<'. '3']'``

        delete_all : bool
            Whether to delete the entire table or not.
        
        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>
        
        Example
        -------
        .. jupyter-execute::

            from msdss_base_database import Database
            from msdss_data_api.handlers import *
            from msdss_data_api.managers import *
            
            # Setup objects
            db = Database()
            dm = DataManager(database=db)
            handler = DataHandler(database=db)

            # Check if the table exists and drop if it does
            if db.has_table('test_table'):
                db.drop_table('test_table')

            # Create sample data
            data = [
                {'id': 1, 'column_one': 'a', 'column_two': 2},
                {'id': 2, 'column_one': 'b', 'column_two': 4},
                {'id': 3, 'column_one': 'c', 'column_two': 6},
            ]
            dm.create('test_table', data)

            # Check table name
            # Should not raise exceptions
            handler.handle_delete('test_table', where=None, delete_all=True)
        """
        self.handle_read(dataset)
        if not delete_all and where_list is None:
            raise HTTPException(status_code=400, detail='Parameter where is required')
        else:
            self.handle_where(where_list)

    def handle_permissions(self, dataset):
        """
        Handle a permitted table access.
        
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
            from msdss_data_api.handlers import *
            from msdss_data_api.managers import *
            
            # Setup objects
            db = Database()
            dm = DataManager(database=db)
            handler = DataHandler(database=db)

            # Check if the table exists and drop if it does
            if db.has_table('test_table'):
                db.drop_table('test_table')

            # Create sample data
            data = [
                {'id': 1, 'column_one': 'a', 'column_two': 2},
                {'id': 2, 'column_one': 'b', 'column_two': 4},
                {'id': 3, 'column_one': 'c', 'column_two': 6},
            ]
            dm.create('test_table', data)

            # Check table name
            # Should not raise exceptions
            handler.handle_permissions('test_table')
        """
        if len(self.permitted_tables) > 0:
            if dataset not in self.permitted_tables:
                raise HTTPException(status_code=401)

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
            from msdss_data_api.handlers import *
            from msdss_data_api.managers import *
            
            # Setup objects
            db = Database()
            dm = DataManager(database=db)
            handler = DataHandler(database=db)

            # Check if the table exists and drop if it does
            if db.has_table('test_table'):
                db.drop_table('test_table')

            # Create sample data
            data = [
                {'id': 1, 'column_one': 'a', 'column_two': 2},
                {'id': 2, 'column_one': 'b', 'column_two': 4},
                {'id': 3, 'column_one': 'c', 'column_two': 6},
            ]
            dm.create('test_table', data)

            # Check table name
            # Should not raise exceptions
            handler.handle_read('test_table')
        """
        self.handle_restrictions(dataset)
        self.handle_permissions(dataset)
        if not self.database.has_table(dataset):
            raise HTTPException(status_code=404, detail='Dataset not found')

    def handle_restrictions(self, dataset):
        """
        Handle restricted table access.
        
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
            from msdss_data_api.handlers import *
            from msdss_data_api.managers import *
            
            # Setup objects
            db = Database()
            dm = DataManager(database=db)
            handler = DataHandler(database=db)

            # Check if the table exists and drop if it does
            if db.has_table('test_table'):
                db.drop_table('test_table')

            # Create sample data
            data = [
                {'id': 1, 'column_one': 'a', 'column_two': 2},
                {'id': 2, 'column_one': 'b', 'column_two': 4},
                {'id': 3, 'column_one': 'c', 'column_two': 6},
            ]
            dm.create('test_table', data)

            # Check table name
            # Should not raise exceptions
            handler.handle_restrictions('test_table')
        """
        if dataset in self.restricted_tables:
            raise HTTPException(status_code=401)

    def handle_where(self, where_list):
        """
        Throw an exception if where statements do not match the expected format.
        
        Parameters
        ----------
        table : str
            Table name to apply where to.
        where_list : list(list(str))
            list of where statements the form of ``['column', 'operator', 'value']`` to further filter individual values or rows.
            
            * Operators are one of:

                .. jupyter-execute::
                    :hide-code:

                    from msdss_base_database.defaults import DEFAULT_SUPPORTED_OPERATORS
                    for operator in DEFAULT_SUPPORTED_OPERATORS:
                        print(operator)

            * Example: ``['column_two', '<'. '3']'``
        
        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>
        
        Example
        -------
        .. jupyter-execute::

            from msdss_data_api.handlers import *

            handler = DataHandler(database=db)
            where_list = [['col', '<', '3'], ['col', '=', 'a']]

            # Should not raise exceptions
            handler.handle_where(where_list)
        """
        if where_list:

            # (DataHandler_handle_where_len) Handle wrong length
            where_has_wrong_len = any([len(w) != 3 for w in where_list])
            if where_has_wrong_len:
                raise HTTPException(status_code=400, detail='Parameter where is formatted incorrectly - should be in the form of "column operator value" e.g. "col < 3"')

            # (DataHandler_handle_where_op) Handle unsupported operator
            for w in where_list:
                if w[1].upper() not in DEFAULT_SUPPORTED_OPERATORS:
                    raise HTTPException(status_code=400, detail='Operator \'' + w[1] + '\' is not supported - supported operators are: ' + ', '.join(DEFAULT_SUPPORTED_OPERATORS))

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
            from msdss_data_api.handlers import *
            from msdss_data_api.managers import *
            
            # Setup objects
            db = Database()
            dm = DataManager(database=db)
            handler = DataHandler(database=db)

            # Check if the table exists and drop if it does
            if db.has_table('test_table'):
                db.drop_table('test_table')

            # Check table name
            # Should not raise exceptions
            handler.handle_write('test_table')
        """
        self.handle_restrictions(dataset)
        self.handle_permissions(dataset)
        if self.database.has_table(dataset):
            raise HTTPException(status_code=400, detail='Dataset already exists')

    def handle_update(self, dataset, data, where_list=None):
        """
        Handle a table update, checking for existence and restrictions.
        
        Parameters
        ----------
        dataset : str
            Name of the table to check.
        data : dict
            Dictionary of update values to check. Each key should represent a column name in the table.
        where_list : list(list(str))
            list of where statements the form of ``['column', 'operator', 'value']`` to further filter individual values or rows.
            
            * Operators are one of:

                .. jupyter-execute::
                    :hide-code:

                    from msdss_base_database.defaults import DEFAULT_SUPPORTED_OPERATORS
                    for operator in DEFAULT_SUPPORTED_OPERATORS:
                        print(operator)

            * Example: ``['column_two', '<'. '3']'``
        
        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>
        
        Example
        -------
        .. jupyter-execute::

            from msdss_base_database import Database
            from msdss_data_api.handlers import *
            from msdss_data_api.managers import *
            
            # Setup objects
            db = Database()
            dm = DataManager(database=db)
            handler = DataHandler(database=db)

            # Check if the table exists and drop if it does
            if db.has_table('test_table'):
                db.drop_table('test_table')

            # Create sample data
            data = [
                {'id': 1, 'column_one': 'a', 'column_two': 2},
                {'id': 2, 'column_one': 'b', 'column_two': 4},
                {'id': 3, 'column_one': 'c', 'column_two': 6},
            ]
            dm.create('test_table', data)

            # Handle update
            # Should not throw any exceptions
            newdata = {'id': 2, 'column_one': 'UPDATED'}
            handler.handle_update('test_table', newdata)
        """
        self.handle_restrictions(dataset)
        self.handle_permissions(dataset)
        self.handle_read(dataset)
        self.handle_where(where_list)
        columns = self.database._get_table(dataset).c
        for k in data.keys():
            if k not in columns:
                raise HTTPException(status_code=400, detail='column \'' + k + '\' not found')