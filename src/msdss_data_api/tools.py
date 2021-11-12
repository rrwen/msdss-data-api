from msdss_base_database import Database

def create_data_db_func(db = Database()):
    """
    Create a function to use as an API dependency.
    
    Parameters
    ----------
    db : :class:`msdss_base_database:msdss_base_database.core.Database`
        Database object to use for APIs.

    Returns
    -------
    func
        A function yielding the ``db``.
    
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

        # Create a function yielding the database to use as a dependency
        create_data_db_func(db=db)
    """
    async def out():
        yield db
    return out