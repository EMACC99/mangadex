"""
Url handler module
"""

import json
from typing_extensions import Dict, Union, Any

import requests

from .errors import ApiError

try:
    basestring
except NameError:
    from past.builtins import basestring

try:
    from urllib.parse import urlparse, urlencode
except ImportError:
    from urlparse import urlparse
    from urllib import urlencode


class URLRequest:
    """
    Handles the request to the server
    """

    @staticmethod
    def request_url(
        url: str,
        method: str,
        timeout,
        params: Union[Dict[str, Any], None] = None,
        headers=None,
    ) -> dict:
        """
        The handler fot GET, POST, PUT and DEL
        """
        if params is None:
            params = {}
        params = {
            k: v.decode("utf-8") if isinstance(v, bytes) else v
            for k, v in params.items()
        }

        if method == "GET":
            url = URLRequest.__build_url(url, params)
            try:
                resp = requests.get(url, headers=headers, timeout=timeout)
            except requests.RequestException as e:
                print(f"An error has occurred: {e}")
                raise
        elif method == "POST":
            try:
                resp = requests.post(url, data=params, headers=headers, timeout=timeout)
            except requests.RequestException as e:
                print(f"An error has occurred: {e}")
                raise
        elif method == "DELETE":
            try:
                resp = requests.delete(url, headers=headers, timeout=timeout)
            except requests.RequestException as e:
                print(f"An error has occurred: {e}")
                raise
        elif method == "PUT":
            try:
                resp = requests.put(
                    url, headers=headers, params=params, timeout=timeout
                )
            except requests.RequestException as e:
                print(f"An error has occurred: {e}")
                raise
        else:
            raise ValueError(f"Method {method} is invalid")

        if not resp.ok:
            raise ApiError(resp)

        content = resp.content
        data = URLRequest.__parse_data(
            content if isinstance(content, basestring) else content.decode("utf-8")
        )
        return data

    @staticmethod
    def __build_url(url: str, params: dict) -> str:
        if params and len(params) > 0:
            url = url + "?" + URLRequest.__encode_parameters(params)
        return url

    @staticmethod
    def __encode_parameters(params: dict) -> str:
        if params is None:
            return ""
        else:
            params_tuple = []
            for k, v in params.items():
                if v is None:
                    continue
                if isinstance(v, (list, tuple)):
                    for _ in v:
                        params_tuple.append((k, _))
                else:
                    params_tuple.append((k, v))
            return urlencode(params_tuple)

    @staticmethod
    def __parse_data(content):
        try:
            data = json.loads(content)
            URLRequest._check_api_error(data)
        except json.JSONDecodeError as e:
            # the ping response doen't come in JSON and its just a string return it that way and throw error in class if needed
            data = content.decode("UTF-8")
        return data

    @staticmethod
    def _check_api_error(data: dict):
        if isinstance(data, list):
            data = data[0]
        if "result" in data.keys():
            if data["result"] == "error" or "error" in data:
                raise ApiError(data["errors"])
            if isinstance(data, (list, tuple)) and len(data) > 0:
                if "error" in data:
                    raise ApiError(data["errors"])
