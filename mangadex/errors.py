"""
Module for error class declaration
"""
from typing import Union
from requests import Response
from typing_extensions import Self


class ApiError(Exception):
    def __init__(
        self, resp: Union[Response, dict], message="The api responded with the error"
    ) -> Self:
        self.resp = resp
        self.details = ""
        if isinstance(self.resp, Response):
            self.code = self.resp.status_code
        else:
            self.code = self.resp["status"]

        self.message = message
        super().__init__(self.message)
        self.details = self.resp.reason

    def __str__(self) -> str:
        return f"{self.message}: {self.code} \n {self.details}"


class ApiClientError(Exception):
    pass


class BaseError(Exception):
    def __init__(self, data: dict, message: str = None) -> Self:
        self.data = data
        self.message = message
        super(BaseError, self).__init__(self.message)


class MangaError(BaseError):
    def __init__(self, data: dict, message: str) -> Self:
        super(MangaError, self).__init__(data, message=message)
        self.data = data
        self.message = message


class TagError(BaseError):
    def __init__(self, data: dict, message: str) -> Self:
        super(TagError, self).__init__(data, message=message)
        self.data = data
        self.message = message


class ChapterError(BaseError):
    def __init__(self, data: dict, message: str) -> Self:
        super(ChapterError, self).__init__(data, message=message)
        self.data = data
        self.message = message


class AuthorError(BaseError):
    def __init__(self, data: dict, message: str) -> Self:
        super(AuthorError, self).__init__(data, message=message)
        self.data = data
        self.message = message


class ScanlationGroupError(BaseError):
    def __init__(self, data: dict, message: str) -> Self:
        super(ScanlationGroupError, self).__init__(data, message=message)
        self.data = data
        self.message = message


class UserError(BaseError):
    def __init__(self, data: dict, message: str) -> Self:
        super(UserError, self).__init__(data, message=message)
        self.data = data
        self.message = message


class CustomListError(BaseError):
    def __init__(self, data: dict, message: str) -> Self:
        super(CustomListError, self).__init__(data, message)
        self.data = data
        self.message = message


class CoverArtError(BaseError):
    def __init__(self, data: dict, message: str) -> Self:
        super(CoverArtError, self).__init__(data, message=message)
        self.data = data
        self.message = message
