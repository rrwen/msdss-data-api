DEFAULT_METADATA_TABLE = 'data'
DEFAULT_USER_TABLE = 'user'
DEFAULT_RESTRICTED_TABLES = [DEFAULT_METADATA_TABLE, DEFAULT_USER_TABLE]
DEFAULT_METADATA_DATASET_COLUMN = 'dataset'
DEFAULT_METADATA_UPLOADED_COLUMN = 'uploaded'
DEFAULT_METADATA_UPLOADED_BY_COLUMN = 'uploaded_by'
DEFAULT_METADATA_UPDATED_COLUMN = 'updated'
DEFAULT_METADATA_COLUMNS = [
    dict(name='id', type_='Integer', primary_key=True),
    dict(name=DEFAULT_METADATA_DATASET_COLUMN, type_='String', unique=True),
    ('title', 'String'),
    ('description', 'String'),
    ('source', 'String'),
    (DEFAULT_METADATA_UPLOADED_BY_COLUMN, 'String'),
    (DEFAULT_METADATA_UPLOADED_COLUMN, 'DateTime'),
    (DEFAULT_METADATA_UPDATED_COLUMN, 'DateTime')
]