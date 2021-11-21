from pydantic import BaseModel
from typing import Any, Dict, List, Optional

class DataCreate(BaseModel):
    """
    Model for creating data.
    
    Attributes
    ----------
    title : str
        Title of the dataset stored in metadata.
    description : str
        Description of dataset stored in metadata.
    source : str
        Data source stored in metadata.
    data : list(dict)
        The data itself for the dataset. Should be a list of dictionaries with the same keys, where each key in each dict is a column name.
    
    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>
    
    Example
    -------
    .. jupyter-execute::

        from msdss_data_api.models import *
        from pprint import pprint

        fields = DataCreate.__fields__
        pprint(fields)
    """
    title: Optional[str]
    description: Optional[str]
    source: Optional[str]
    data: List[Dict[str, Any]]

class MetadataUpdate(BaseModel):
    """
    Model for updating metadata.
    
    Attributes
    ----------
    title : str
        Title of the dataset stored in metadata.
    description : str
        Description of dataset stored in metadata.
    source : str
        Data source stored in metadata.
    
    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>
    
    Example
    -------
    .. jupyter-execute::

        from msdss_data_api.models import *
        from pprint import pprint

        fields = MetadataUpdate.__fields__
        pprint(fields)
    """
    title: Optional[str]
    description: Optional[str]
    source: Optional[str]
    