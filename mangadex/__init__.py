"""
Python module for interacting with the mangadex API
"""
from .errors import (
    ApiError
)
from .url_models import URLRequest

from .auth import (
    Api,
    ApiClient,
    Auth
)
from .people import (
    Author,
    ScanlationGroup,
    User,
    Follows
)
from .series import (
    Chapter,
    Cover,
    Tag,
    Manga,
    MangaList,
    CustomList,
)
__author__ = "Eduardo Ceja"
__version__ = "2.7"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2021 Eduardo Ceja"
