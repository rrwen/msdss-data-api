from msdss_base_database import Database

from .handlers import *
from .managers import *

def create_data_manager_func(database=Database(), restricted_tables=DEFAULT_RESTRICTED_TABLES):
    """
    Create a function yielding a :class:`msdss_data_api.managers.DataManager`.
    
    Parameters
    ----------
    database : :class:`msdss_base_database:msdss_base_database.core.Database`
        Database object to use for APIs.
    restricted_tables : list(str)
        List of restricted tables in the database to prevent access to.

    Returns
    -------
    func
        A function yielding a preconfigured :class:`msdss_data_api.managers.DataManager`.
    
    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>
    
    Example
    -------
    .. jupyter-execute::

        from msdss_base_database import Database
        from msdss_data_api.tools import *
        
        # Setup database
        db = Database()

        # Create a function yielding the data manager to use as a dependency
        get_data_manager = create_data_db_func(database=db)
    """
    data_handler = DataHandler(database=database, restricted_tables=restricted_tables)
    data_manager = DataManager(database=database, handler=data_handler)
    async def out():
        yield data_manager
    return out