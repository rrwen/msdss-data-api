from fastapi import HTTPException
from msdss_base_database import Database

from .data import *

DEFAULT_PERMISSIONS_TABLE = 'data'
DEFAULT_DATASET_COLUMN = 'dataset'
DEFAULT_PERMISSIONS_COLUMN = 'permissions'
DEFAULT_PERMISSIONS_TABLE_COLUMNS = [
    dict(name='id', type_='Integer', primary_key=True),
    dict(name=DEFAULT_DATASET_COLUMN, type_='String', unique=True),
    (DEFAULT_PERMISSIONS_COLUMN, 'String')
]

class DatasetPermissions:
    """
    Class for managing data permissions for users.
    
    Parameters
    ----------
    table : str
        Table name holding the permissions information.
    columns : dict(dict) or dict(list)
        Column structure for the table. See parameter ``columns`` in :meth:`msdss_base_database:msdss_base_database.core.Database.create_table`.
        The default structure is:

        .. jupyter-execute::
            :hide-code:

            from msdss_data_api.users import *
            print(DEFAULT_PERMISSIONS_TABLE_COLUMNS)
    dataset_column : str
        Column name for the dataset names.
    permissions_column : str
        Column name for the permissions per dataset.
    user_prefix : str
        Leading characters (no spaces) indicating a user permission.
    database : :class:`msdss_base_database:msdss_base_database.core.Database`
        Database object for managing the permissions table.
    
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
        if db.has_table(DEFAULT_PERMISSIONS_TABLE):
            db.drop_table(DEFAULT_PERMISSIONS_TABLE)
        
        # Create permissions table
        data_permissions = DatasetPermissions(database=db)
    """
    def __init__(
        self,
        table=DEFAULT_PERMISSIONS_TABLE,
        columns=DEFAULT_PERMISSIONS_TABLE_COLUMNS,
        dataset_column=DEFAULT_DATASET_COLUMN,
        permissions_column=DEFAULT_PERMISSIONS_COLUMN,
        user_prefix='user',
        database=Database()):

        # (DatasetPermissions_create) Create permissions table in database
        database.create_table(table=table, columns=columns)

        # (DatasetPermissions_attr) Set attributes
        self.table = table
        self.dataset_column = dataset_column
        self.permissions_column = permissions_column
        self.user_prefix = user_prefix
        self.database = database
    
    def add(self, dataset, permissions=['users:*']):
        """
        Add a dataset to the permissions table.
        
        Parameters
        ----------
        dataset : name
            Name of the dataset to add permissions for.
        permissions : list(str)
            Initial permissions to add for the dataset.
        
        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>
        
        Example
        -------
        .. jupyter-execute::

            from msdss_base_database import Database
            from msdss_data_api.users import *
            from pprint import pprint
            
            # Setup database
            db = Database()

            # Check if permissions table exists and drop if it does
            if db.has_table(DEFAULT_PERMISSIONS_TABLE):
                db.drop_table(DEFAULT_PERMISSIONS_TABLE)
            
            # Create permissions table
            data_permissions = DatasetPermissions(database=db)

            # Check if dataset exists and drop if it does
            if db.has_table("test_table"):
                db.drop_table("test_table")

            # Create sample dataset
            data = {
                'id': [1, 2, 3],
                'column_one': ['a', 'b', 'c'],
                'column_two': [2, 4, 6]
            }
            create_table('test_table', data, db=db)

            # Add sample dataset to permissions
            data_permissions.add('test_table')

            # See permissions
            print('permissions_table_name: ' + DEFAULT_PERMISSIONS_TABLE)
            permissions_data = query_table(DEFAULT_PERMISSIONS_TABLE, db=db)
            pprint(permissions_data)
        """
        data = {}
        data[self.dataset_column] = dataset
        data[self.permissions_column] = permissions
        self.database.insert(self.table, data)
    
    def delete(self, dataset, permissions):
        
        # (DatasetPermissions_delete_new) Create new permissions from deletion
        old_permissions = self.get_dataset_permissions(dataset=dataset)
        new_permissions = old_permissions.replace(permissions, '').strip()
    
        # (DatasetPermissions_delete_update) Update the permissions table for the dataset
        data = {}
        data[self.permissions_column] = new_permissions
        where = f'{self.dataset_column} = {dataset}'
        update_table(table=self.table, data=data, where=where)
    
    def get(self, dataset):
        
        where = f'{dataset_column} = {dataset}'
        out = query_table(
            table=table,
            where=where,
            where_boolean='AND',
            db=db)[permissions_column][0]
        return out

def add_user_permissions(
    id,
    dataset,
    operations=['read'],
    table=DEFAULT_PERMISSIONS_TABLE,
    dataset_column=DEFAULT_DATASET_COLUMN,
    permissions_column=DEFAULT_PERMISSIONS_COLUMN,
    user_prefix=DEFAULT_USER_KEYWORD_PREFIX,
    db=Database()):
    
    permissions = get_dataset_permissions(
        dataset=dataset,
        table=table,
        dataset_column=dataset_column,
        permissions_column=permissions_column,
        db=db)

    user_keywords = [get_user_permissions_keyword(id, op, user_prefix) for op in operations]
    user_keywords = list(filter(lambda p: p not in permissions, user_keywords))
    user_keywords = ' '.join(user_keywords)

    new_permissions = f'{permissions} {user_keywords}'
    data = {}
    data[permissions_column] = new_permissions
    data[permissions_column] = new_permissions

    where = f'{dataset_column} = {dataset}'
    update_table(table=table, where=where)

def delete_permissions(
    dataset,
    permissions,
    table=DEFAULT_PERMISSIONS_TABLE,
    dataset_column=DEFAULT_DATASET_COLUMN,
    permissions_column=DEFAULT_PERMISSIONS_COLUMN,
    db=Database()):
    """
    Delete permissions for a dataset.
    
    Parameters
    ----------
    dataset : name
        Name of the dataset to add permissions for.
    permissions : str
        Permissions to delete for the dataset.
    table : str
        Table name holding the permissions information.
    dataset_column : str
        Column name for the dataset names.
    permissions_column : str
        Column name for the permissions per dataset.
    db : :class:`msdss_base_database:msdss_base_database.core.Database`
        Database object to use for deleting permissions.
    
    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>
    
    Example
    -------
    .. jupyter-execute::

        from msdss_base_database import Database
        from msdss_data_api.users import *
        from pprint import pprint
        
        # Setup database
        db = Database()

        # Check if permissions table exists and drop if it does
        if db.has_table(DEFAULT_PERMISSIONS_TABLE):
            db.drop_table(DEFAULT_PERMISSIONS_TABLE)
        
        # Create permissions table
        create_permissions_table(db=db)

        # Check if dataset exists and drop if it does
        if db.has_table("test_table"):
            db.drop_table("test_table")

        # Create sample dataset
        data = {
            'id': [1, 2, 3],
            'column_one': ['a', 'b', 'c'],
            'column_two': [2, 4, 6]
        }
        create_table('test_table', data, db=db)

        # Add sample dataset to permissions
        create_dataset_permissions('test_table')
        before_del = get_dataset_permissions('test_table')

        # Delete permissions
        delete_permissions('test_table', 'user:*')
        after_del = get_dataset_permissions('test_table')

        # Print results
        print('before_del:')
        pprint(before_del)
        print('after_del:')
        pprint(after_del)
    """
    
    # (delete_permissions_new) Create new permissions from deletion
    old_permissions = get_dataset_permissions(
        dataset=dataset,
        table=table,
        dataset_column=dataset_column,
        permissions_column=permissions_column,
        db=db)
    new_permissions = old_permissions.replace(permissions, '').strip()
    
    # (delete_permissions_update) Update the permissions table for the dataset
    data = {}
    data[permissions_column] = new_permissions
    where = f'{dataset_column} = {dataset}'
    update_table(table=table, data=data, where=where)

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
    
    Return
    ------
    str
        Text containing all permissions keywords for the dataset.

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

        # Check if permissions table exists and drop if it does
        if db.has_table(DEFAULT_PERMISSIONS_TABLE):
            db.drop_table(DEFAULT_PERMISSIONS_TABLE)
        
        # Create permissions table
        create_permissions_table(db=db)

        # Check if dataset exists and drop if it does
        if db.has_table("test_table"):
            db.drop_table("test_table")

        # Create sample dataset
        data = {
            'id': [1, 2, 3],
            'column_one': ['a', 'b', 'c'],
            'column_two': [2, 4, 6]
        }
        create_table('test_table', data, db=db)

        # Add sample dataset to permissions
        create_dataset_permissions('test_table')

        # Get the permissions for dataset
        permissions = get_dataset_permissions('test_table')
        print('Permissions for test_table:\\n' + permissions)
    """
    where = f'{dataset_column} = {dataset}'
    out = query_table(
        table=table,
        where=where,
        where_boolean='AND',
        db=db)[permissions_column][0]
    return out

def get_user_permissions_keyword(
    id,
    operation='read',
    user_prefix=DEFAULT_USER_KEYWORD_PREFIX):
    """
    Check if a user is permitted.
    
    Parameters
    ----------
    id : str
        User id to check for permissions.
    operation : str
        Operation permission type as a keyword.
    user_prefix : str
        Leading characters that appear before user ids in the permissions column.
    
    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>
    
    Example
    -------
    .. jupyter-execute::

        from msdss_data_api.users import *
        
        permissions = 'user:read:00123-msdss user:write:00345-msdss'
        user_keyword = get_user_permissions_keyword('00123-msdss', 'read')
        print(user_keyword)
    """
    out = f'{user_prefix}:{operation}:{id}'
    return out

def handle_user_permissions(
    id,
    dataset,
    operation='read',
    table=DEFAULT_PERMISSIONS_TABLE,
    dataset_column=DEFAULT_DATASET_COLUMN,
    permissions_column=DEFAULT_PERMISSIONS_COLUMN,
    enable_all_users=True,
    all_users_keyword=DEFAULT_ALL_USERS_KEYWORD,
    user_prefix=DEFAULT_USER_KEYWORD_PREFIX,
    db=Database()):
    """
    Handle user permissions for reading a dataset.
    
    Parameters
    ----------
    id : str
        User id to check for permissions.
    dataset : name
        Name of the dataset to check for user permissions.
    operation : str
        Permission operatation type (e.g. read, write, delete) to check for dataset and user.
    table : str
        Table name holding the permissions information.
    dataset_column : str
        Column name for the dataset names.
    permissions_column : str
        Column name for the permissions per dataset.
    enable_all_users : bool
        Whether to allow all users to access datasets specified for all users or not.
    all_users_keyword : str
        Permissions keyword for all users permissions.
    user_prefix : str
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

        # Check if permissions table exists and drop if it does
        if db.has_table(DEFAULT_PERMISSIONS_TABLE):
            db.drop_table(DEFAULT_PERMISSIONS_TABLE)
        
        # Create permissions table
        create_permissions_table(db=db)

        # Check if dataset exists and drop if it does
        if db.has_table("test_table"):
            db.drop_table("test_table")

        # Create sample dataset
        data = {
            'id': [1, 2, 3],
            'column_one': ['a', 'b', 'c'],
            'column_two': [2, 4, 6]
        }
        create_table('test_table', data, db=db)

        # Add sample dataset to permissions
        create_dataset_permissions('test_table', permissions='')
    """

    # (handle_user_permissions_get) Find permissions for dataset
    permissions = get_dataset_permissions(
        dataset=dataset,
        table=table,
        dataset_column=dataset_column,
        permissions_column=permissions_column,
        db=db
    )

    # (handle_user_permissions_deny) Throw unauthorized exception if user is not permitted
    has_permissions = has_user_permissions(
        id=id,
        permissions=permissions,
        operation_keyword_prefix=operation,
        enable_all_users=enable_all_users,
        all_users_keyword=all_users_keyword,
        user_prefix=user_prefix)
    if not has_permissions:
        raise HTTPException(status_code=401)

def handle_dataset_permissions_read(
    dataset,
    table=DEFAULT_PERMISSIONS_TABLE,
    dataset_column=DEFAULT_DATASET_COLUMN,
    db=Database()):
    """
    Handle requests to read dataset permissions.
    
    Parameters
    ----------
    dataset : name
        Name of the dataset to check for permissions.
    table : str
        Table name holding the permissions information.
    dataset_column : str
        Column name for the dataset names.
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

        # Check if permissions table exists and drop if it does
        if db.has_table(DEFAULT_PERMISSIONS_TABLE):
            db.drop_table(DEFAULT_PERMISSIONS_TABLE)
        
        # Create permissions table
        create_permissions_table(db=db)

        # Check if dataset exists and drop if it does
        if db.has_table("test_table"):
            db.drop_table("test_table")

        # Create sample dataset
        data = {
            'id': [1, 2, 3],
            'column_one': ['a', 'b', 'c'],
            'column_two': [2, 4, 6]
        }
        create_table('test_table', data, db=db)

        # Add sample dataset to permissions
        create_dataset_permissions('test_table')

        # Should run without exceptions
        handle_dataset_permissions_read('test_table', db=db)
    """
    dataset_exists = has_dataset_permissions(dataset=dataset, table=table, dataset_column=dataset_column, db=db)
    if not dataset_exists:
        raise HTTPException(status_code=404, detail='Dataset permissions not found')

def handle_dataset_permissions_write(
    dataset,
    table=DEFAULT_PERMISSIONS_TABLE,
    dataset_column=DEFAULT_DATASET_COLUMN,
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

        # Check if permissions table exists and drop if it does
        if db.has_table(DEFAULT_PERMISSIONS_TABLE):
            db.drop_table(DEFAULT_PERMISSIONS_TABLE)
        
        # Create permissions table
        create_permissions_table(db=db)

        # Check if dataset exists and drop if it does
        if db.has_table("test_table"):
            db.drop_table("test_table")

        # Create sample dataset
        data = {
            'id': [1, 2, 3],
            'column_one': ['a', 'b', 'c'],
            'column_two': [2, 4, 6]
        }
        create_table('test_table', data, db=db)

        # Should run without exceptions
        handle_dataset_permissions_write('test_table', db=db)
    """
    dataset_exists = has_dataset_permissions(dataset=dataset, table=table, dataset_column=dataset_column, db=db)
    if dataset_exists:
        raise HTTPException(status_code=400, detail='Dataset already exists')

def has_dataset_permissions(
    dataset,
    table=DEFAULT_PERMISSIONS_TABLE,
    dataset_column=DEFAULT_DATASET_COLUMN,
    db=Database()):
    """
    Check if a dataset has permissions set.
    
    Parameters
    ----------
    dataset : name
        Name of the dataset to check for permissions.
    table : str
        Table name holding the permissions information.
    dataset_column : str
        Column name for the dataset names.
    db : :class:`msdss_base_database:msdss_base_database.core.Database`
        Database object to use for checking permissions.
    
    Return
    ------
    bool
        Whether the dataset has permissions set or not.

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

        # Check if permissions table exists and drop if it does
        if db.has_table(DEFAULT_PERMISSIONS_TABLE):
            db.drop_table(DEFAULT_PERMISSIONS_TABLE)
        
        # Create permissions table
        create_permissions_table(db=db)

        # Check if dataset exists and drop if it does
        if db.has_table("test_table"):
            db.drop_table("test_table")

        # Create sample dataset
        data = {
            'id': [1, 2, 3],
            'column_one': ['a', 'b', 'c'],
            'column_two': [2, 4, 6]
        }
        create_table('test_table', data, db=db)

        # Check for dataset permissions
        before_has_permissions = has_dataset_permissions('test_table', db=db)

        # Add sample dataset to permissions
        create_dataset_permissions('test_table')

        # Check again for permissions
        after_has_permissions = has_dataset_permissions('test_table', db=db)

        # Print results
        print('before_has_permissions: ' + before_has_permissions)
        print('after_has_permissions: ' + after_has_permissions)
    """

    # (has_dataset_permissions_check) Check permissions table for dataset
    where = f'{dataset_column} = {dataset}'
    results = query_table(table=table, where=where, db=db)[dataset_column]
    
    # (has_dataset_permissions_return) Return if dataset permissions exist
    out = len(results) > 0
    return out

def has_user_permissions(
    id,
    permissions,
    operation='read',
    enable_all_users=True,
    all_users_keyword=DEFAULT_ALL_USERS_KEYWORD,
    user_prefix=DEFAULT_USER_KEYWORD_PREFIX):
    """
    Check if a user is permitted.
    
    Parameters
    ----------
    id : str
        User id to check for permissions.
    permissions : str
        Text containing permissions separated by spaces.
    operation : str
        Operation permission type as a keyword.
    dataset : name
        Name of the dataset to check for user permissions.
    table : str
        Table name holding the permissions information.
    dataset_column : str
        Column name for the dataset names.
    permissions_column : str
        Column name for the permissions per dataset.
    enable_all_users : bool
        Whether to allow all users to access datasets specified for all users or not.
    all_users_keyword : str
        Permissions keyword for all users permissions.
    user_prefix : str
        Leading characters that appear before user ids in the permissions column.
    db : :class:`msdss_base_database:msdss_base_database.core.Database`
        Database object to use for checking permissions.
    
    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>
    
    Example
    -------
    .. jupyter-execute::

        from msdss_data_api.users import *
        
        permissions = 'user:read:00123-msdss user:write:00345-msdss'
        has_read_permissions = has_user_permissions('00123-msdss', permissions, 'read')
        has_write_permissions = has_user_permissions('00123-msdss', permissions, 'write')
        
        print('has_read_permissions: ' + str(has_read_permissions))
        print('has_write_permissions: ' + str(has_write_permissions))
    """
    user_keyword = get_user_permissions_keyword(id, operation, user_prefix)
    out = (
        (enable_all_users and not all_users_keyword in permissions) or 
        (user_keyword not in permissions)
    )
    return out