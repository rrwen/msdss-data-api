DEFAULT_METADATA_TABLE = 'metadata'
DEFAULT_METADATA_COLUMNS = [
    dict(name='id', type_='Integer', primary_key=True),
    dict(name='dataset', type_='String', unique=True),
    ('created_by', 'String'),
    ('created_at', 'DateTime'),
    ('title', 'String'),
    ('description', 'String'),
]
DEFAULT_USER_TABLE = 'user'
DEFAULT_RESTRICTED_TABLES = [DEFAULT_METADATA_TABLE, DEFAULT_USER_TABLE]