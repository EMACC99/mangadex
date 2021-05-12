from __future__ import absolute_import
from mangadex.errors import ApiError

import json
import requests

from typing import Tuple
from future.utils import iteritems

try:
    basestring
except NameError:
    from past.builtins import basestring

try:
    from urllib.parse import urlparse, urlencode
except ImportError:
    from urlparse import urlparse
    from urllib import urlencode


from mangadex import (ApiError, ApiClientError, Manga, manga)

class Api():
    def __init__(self, key = None, secret = None, timeout = 5):
        self.URL = 'https://api.mangadex.org'
        self.key = key
        self.secret = secret
        self.timeout = timeout


    def _request_url(self, url, type, params = None):
        headers = None
        if params is None:
            params = {}
        params = {k: v.decode("utf-8") if isinstance(v, bytes) else v for k, v in params.items()}
        
        if type == 'GET':
            url = self._build_url(url, params)
            try:
                resp = requests.get(url, headers=headers, timeout=self.timeout)
            except requests.RequestException as e:
                print(f"An error has occured: {e}")
                raise
        elif type == 'POST':
            try:
                resp = requests.post(url, headers=headers, timeout=self.timeout)
            except requests.RequestException as e:
                print(f"An error has occured: {e}")
                raise
        elif type == "DELETE":
            try:
                resp = requests.post(url, headers= headers, timeout=self.timeout)
            except requests.RequestException as e:
                print(f"An error has occured: {e}")
                raise
        content = resp.content
        data = self._parse_data(content if isinstance(content, basestring) else content.decode('utf-8'))
        return data

    def _build_url(self, url, params):
        if params and len(params) > 0:
            url = url + '?' + self._encode_parameters(params)
        return url

    def _encode_parameters(self, params):
        if params is None:
            return None
        else:
            params_tuple = []
            for k,v in params.items():
                if v is None:
                    continue
                if isinstance(v, (list,tuple)):
                    for _ in v:
                        params_tuple.append((k,_))
                else:
                    params_tuple.append((k,v))
            return urlencode(params_tuple)

    def _parse_data(self, content):
        try:
            data = json.loads(content)
            self._check_api_error(data)
        except:
            raise
            
        return data
    
    def _check_api_error(self, data):
        try:
            if data['result'] == 'error' or 'error' in data:
                raise ApiError(data['errors'])
            if isinstance(data, (list, tuple)) and len(data) > 0:
                if 'error' in data[0]:
                    raise ApiError(data['errors'])
        except:
            return

    def _create_manga_list(self, resp):
        resp = resp["results"]
        manga_list = []
        for elem in resp:
            current_manga = Manga()
            current_manga._MangaFromDict(elem)
            manga_list.append(current_manga)
        return manga_list

    def get_manga_list(self, **kwargs):
        url = f"{self.URL}/manga"
        resp = self._request_url(url, 'GET', params=kwargs)
        return self._create_manga_list(resp)
