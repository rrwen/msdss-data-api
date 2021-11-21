DEFAULT_METADATA_TABLE = 'data'
DEFAULT_USER_TABLE = 'user'
DEFAULT_RESTRICTED_TABLES = [DEFAULT_METADATA_TABLE, DEFAULT_USER_TABLE]
DEFAULT_METADATA_COLUMNS = [
    dict(name='id', type_='Integer', primary_key=True),
    dict(name='dataset', type_='String', unique=True),
    ('title', 'String'),
    ('description', 'String'),
    ('source', 'String'),
    ('created_by', 'String'),
    ('created_at', 'DateTime'),
    ('updated_at', 'DateTime')
]