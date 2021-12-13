DEFAULT_METADATA_TABLE = 'data'
DEFAULT_USER_TABLE = 'user'
DEFAULT_NAME_COLUMN = 'dataset'
DEFAULT_UPDATE_COLUMN = 'updated_at'
DEFAULT_RESTRICTED_TABLES = [DEFAULT_METADATA_TABLE, DEFAULT_USER_TABLE]
DEFAULT_METADATA_COLUMNS = [
    dict(name='id', type_='Integer', primary_key=True),
    dict(name='dataset', type_='String', unique=True),
    ('title', 'String'),
    ('description', 'String'),
    ('tags', 'String'),
    ('source', 'String'),
    ('created_by', 'String'),
    ('created_at', 'DateTime'),
    ('updated_at', 'DateTime')
]
DEFAULT_DATA_ROUTE_SETTINGS = dict(
    columns=dict(
        path='/{dataset}/columns',
        _restricted_tables=DEFAULT_RESTRICTED_TABLES,
        _enable=True,
        _get_user={}
    ),
    create=dict(
        path='/',
        _restricted_tables=DEFAULT_RESTRICTED_TABLES,
        _enable=True,
        _get_user={'superuser': True}
    ),
    delete=dict(
        path='/{dataset}',
        _restricted_tables=DEFAULT_RESTRICTED_TABLES,
        _enable=True,
        _get_user={'superuser': True}
    ),
    id=dict(
        path='/{dataset}/id/{id}',
        _restricted_tables=DEFAULT_RESTRICTED_TABLES,
        _enable=True,
        _get_user={}
    ),
    insert=dict(
        path='/{dataset}/insert',
        _restricted_tables=DEFAULT_RESTRICTED_TABLES,
        _enable=True,
        _get_user={'superuser': True}
    ),
    metadata=dict(
        path='/{dataset}/metadata',
        tags=['metadata'],
        _restricted_tables=DEFAULT_RESTRICTED_TABLES,
        _enable=True,
        _get_user={}
    ),
    metadata_update=dict(
        path='/{dataset}/metadata',
        tags=['metadata'],
        _restricted_tables=DEFAULT_RESTRICTED_TABLES,
        _enable=True,
        _get_user={'superuser': True}
    ),
    query=dict(
        path='/{dataset}',
        _restricted_tables=DEFAULT_RESTRICTED_TABLES,
        _enable=True,
        _get_user={}
    ),
    rows=dict(
        path='/{dataset}/rows',
        _restricted_tables=DEFAULT_RESTRICTED_TABLES,
        _enable=True,
        _get_user={}
    ),
    search=dict(
        path='/',
        _restricted_tables=DEFAULT_RESTRICTED_TABLES,
        _enable=True,
        _get_user={}
    ),
    update=dict(
        path='/{dataset}',
        _restricted_tables=DEFAULT_RESTRICTED_TABLES,
        _enable=True,
        _get_user={'superuser': True}
    )
)