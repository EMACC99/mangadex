"""
Python module for interacting with the mangadex API
"""
from .auth import Api, ApiClient, Auth
from .errors import ApiError
from .people import Author, Follows, ScanlationGroup, User
from .series import Chapter, Cover, CustomList, Manga, MangaList, Tag
from .url_models import URLRequest

__author__ = "Eduardo Ceja"
__version__ = "2.7.1"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2021 Eduardo Ceja"
