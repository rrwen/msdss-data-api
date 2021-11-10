from fastapi import HTTPException
from msdss_base_database import Database

from .data import *

DEFAULT_PERMISSIONS_TABLE = 'data'
DEFAULT_DATASET_COLUMN = 'dataset'
DEFAULT_PERMISSIONS_COLUMN = 'permissions'
DEFAULT_PUBLIC_KEYWORD = 'public'
DEFAULT_USER_KEYWORD_PREFIX = 'user:'
DEFAULT_PERMISSIONS_TABLE_SCHEMA = [
    dict(name='id', type_='Integer', primary_key=True),
    dict(name='dataset', type_='String', unique=True),
    ('permissions', 'String')
]

def handle_user_permissions(
    id,
    dataset,
    table=DEFAULT_PERMISSIONS_TABLE,
    dataset_column=DEFAULT_DATASET_COLUMN,
    permissions_column=DEFAULT_PERMISSIONS_COLUMN,
    enable_public=True,
    public_keyword=DEFAULT_PUBLIC_KEYWORD,
    user_keyword_prefix=DEFAULT_USER_KEYWORD_PREFIX,
    db=Database()):
    """
    Handle user permissions for a dataset.
    
    Parameters
    ----------
    id : str
        User id to check for permissions.
    dataset : name
        Name of the dataset to check for user permissions.
    table : str
        Table name holding the permissions information.
    dataset_column : str
        Column name for the dataset names.
    permissions_column : str
        Column name for the permissions per dataset.
    enable_public : bool
        Whether to allow all users to access datasets with public permissions or not.
    public_keyword : str
        Permissions keyword for public permissions.
    user_keyword_prefix : str
        Leading characters that appear before user ids in the permissions column.
    db : :class:`msdss_base_database:msdss_base_database.core.Database`
        Database object to use for checking permissions.
    
    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>
    
    Example
    -------
    .. jupyter-execute::

        from msdss_base_database import Database
        from msdss_data_api.users import *
        
        # Setup database
        db = Database()

        # Check if the table exists and drop if it does
        if db.has_table("test_table"):
            db.drop_table("test_table")
    """

    # (handle_user_permissions_get) Find permissions for dataset
    permissions = get_dataset_permissions(
        dataset=dataset,
        table=table,
        dataset_column=dataset_column,
        permissions_column=permissions_column,
        db=Database()
    )

    # (handle_user_permissions_deny) Throw unauthorized exception if user is not permitted
    if (enable_public and not public_keyword in permissions) or (f'{user_keyword_prefix}{id}' not in permissions):
        raise HTTPException(status_code=401)

def add_user_permissions(
    id,
    dataset,
    table=DEFAULT_PERMISSIONS_TABLE,
    dataset_column=DEFAULT_DATASET_COLUMN,
    permissions_column=DEFAULT_PERMISSIONS_COLUMN,
    user_keyword_prefix=DEFAULT_USER_KEYWORD_PREFIX,
    db=Database()):
    pass

def create_permissions_table(table=DEFAULT_PERMISSIONS_TABLE, schema=DEFAULT_PERMISSIONS_TABLE_SCHEMA, db=Database()):
    db.create_table(table=table, columns=schema)

def create_dataset_permissions(
    dataset,
    permissions=DEFAULT_PUBLIC_KEYWORD,
    table=DEFAULT_PERMISSIONS_TABLE,
    dataset_column=DEFAULT_DATASET_COLUMN,
    permissions_column=DEFAULT_PERMISSIONS_COLUMN,
    db=Database()):
    """
    Get permissions for a dataset.
    
    Parameters
    ----------
    dataset : name
        Name of the dataset to add permissions for.
    table : str
        Table name holding the permissions information.
    dataset_column : str
        Column name for the dataset names.
    permissions_column : str
        Column name for the permissions per dataset.
    db : :class:`msdss_base_database:msdss_base_database.core.Database`
        Database object to use for adding permissions.
    
    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>
    
    Example
    -------
    .. jupyter-execute::

        from msdss_base_database import Database
        from msdss_data_api.users import *
        
        # Setup database
        db = Database()

        # Check if the table exists and drop if it does
        if db.has_table("test_table"):
            db.drop_table("test_table")
    """
    data = {}
    data[dataset_column] = dataset
    data[permissions_column] = permissions
    db.insert(table, data)

def get_dataset_permissions(
    dataset,
    table=DEFAULT_PERMISSIONS_TABLE,
    dataset_column=DEFAULT_DATASET_COLUMN,
    permissions_column=DEFAULT_PERMISSIONS_COLUMN,
    db=Database()):
    """
    Get permissions for a dataset.
    
    Parameters
    ----------
    dataset : name
        Name of the dataset to check for user permissions.
    table : str
        Table name holding the permissions information.
    dataset_column : str
        Column name for the dataset names.
    permissions_column : str
        Column name for the permissions per dataset.
    db : :class:`msdss_base_database:msdss_base_database.core.Database`
        Database object to use for checking permissions.
    
    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>
    
    Example
    -------
    .. jupyter-execute::

        from msdss_base_database import Database
        from msdss_data_api.users import *
        
        # Setup database
        db = Database()

        # Check if the table exists and drop if it does
        if db.has_table("test_table"):
            db.drop_table("test_table")
    """
    where = f'{dataset_column} = {dataset}'
    out = query_table(
        table=table,
        where=where,
        where_boolean='AND',
        db=db)[permissions_column][0]
    return out