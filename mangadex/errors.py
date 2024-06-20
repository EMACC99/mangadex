"""
Module for error class declaration
"""
from typing_extensions import Union

from requests import Response


class ApiError(Exception):
    def __init__(
            self, resp: Union[Response, dict], message="The api responded with the error"
    ) -> None:
        self.resp = resp
        self.details = ""
        if isinstance(self.resp, Response):
            self.code = self.resp.status_code
            self.details = self.resp.reason

        else:
            self.code = self.resp["status"]
            self.details = self.resp["reason"]

        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"{self.message}: {self.code} \n {self.details}"


class BaseError(Exception):
    def __init__(self, data: dict, message: str) -> None:
        self.data = data
        self.message = message
        super(BaseError, self).__init__(self.message)


class ApiClientError(BaseError):
    def __init__(self, data: dict, message: str) -> None:
        super(ApiClientError, self).__init__(data, message=message)
        self.data = data
        self.message = message
