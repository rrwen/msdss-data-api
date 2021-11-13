from fastapi import HTTPException
from msdss_base_database import Database

from .defaults import *

class DataHandler:
    """
    Class to handle dataset events.
    
    Parameters
    ----------
    database : :class:`msdss_base_database:msdss_base_database.core.Database`
        Database object to use for managing datasets.
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
        data = {
            'id': [1, 2, 3],
            'column_one': ['a', 'b', 'c'],
            'column_two': [2, 4, 6]
        }
        dm.create('test_table', data)

        # Check table name
        # Should not raise exceptions
        handler.handle_read('test_table')

        # Check table restrictions
        # Should not raise exceptions
        handler.handle_restrictions('test_table')
    """
    def __init__(self, database=Database(), restricted_tables=DEFAULT_RESTRICTED_TABLES):
        self.database = database
        self.restricted_tables = restricted_tables

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
            data = {
                'id': [1, 2, 3],
                'column_one': ['a', 'b', 'c'],
                'column_two': [2, 4, 6]
            }
            dm.create('test_table', data)

            # Check table name
            # Should not raise exceptions
            handler.handle_read('test_table')
        """
        self.handle_restrictions(dataset)
        if not self.database.has_table(dataset):
            raise HTTPException(status_code=404, detail='Dataset not found')

    def handle_restrictions(self, dataset):
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
            data = {
                'id': [1, 2, 3],
                'column_one': ['a', 'b', 'c'],
                'column_two': [2, 4, 6]
            }
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

            from msdss_data_api.handlers import *

            handler = DataHandler(database=db)
            where_list = [['col', '<', '3'], ['col', '=', 'a']]

            # Should not raise exceptions
            handler.handle_where(where_list)
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

            # Create sample data
            data = {
                'id': [1, 2, 3],
                'column_one': ['a', 'b', 'c'],
                'column_two': [2, 4, 6]
            }
            dm.create('test_table', data)
        """
        self.handle_restrictions(dataset)
        if self.database.has_table(dataset):
            raise HTTPException(status_code=400, detail='Dataset already exists')