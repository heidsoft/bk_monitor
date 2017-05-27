# -*- coding: utf-8 -*-
"""Collections for component client"""
from .apis.cc import CollectionsCC
from .apis.job import CollectionsJOB
from .apis.bk_login import CollectionsBkLogin


# Available components
AVAILABLE_COLLECTIONS = {
    'cc': CollectionsCC,
    'job': CollectionsJOB,
    'bk_login': CollectionsBkLogin,
}
