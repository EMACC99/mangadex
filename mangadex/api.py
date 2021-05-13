from __future__ import absolute_import

import json
from mangadex.models import Author
import requests

from typing import Tuple, List

try:
    basestring
except NameError:
    from past.builtins import basestring

try:
    from urllib.parse import urlparse, urlencode
except ImportError:
    from urlparse import urlparse
    from urllib import urlencode


from mangadex import (ApiError, ApiClientError, Manga, Tag, Chapter)

class Api():
    def __init__(self, key = None, secret = None, timeout = 5):
        self.URL = 'https://api.mangadex.org'
        self.key = key
        self.secret = secret
        self.timeout = timeout


    def _request_url(self, url, type, params = None):
        headers = None #this is for private calls to the API. not implemented yet
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
                resp = requests.post(url, json = params, headers=headers, timeout=self.timeout)
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

    def _create_manga(self, elem):
        manga = Manga()
        manga._MangaFromDict(elem)
        return manga

    def _create_manga_list(self, resp):
        resp = resp["results"]
        manga_list = []
        for elem in resp:
            manga_list.append(self._create_manga(elem))
            
        return manga_list

    def _create_tag(self, elem):
        tag = Tag()
        tag._TagFromDict(elem)
        return tag

    def _create_tag_list(self, resp) -> List[Tag]:
        tag_list = []
        for tag in resp:
            tag_list.append(self._create_tag(tag))

        return tag_list

    def _create_chapter(self, elem):
        chap = Chapter()
        chap._ChapterFromDict(elem)
        return chap

    def _create_chapter_list(self, resp) -> List[Chapter]:
        resp = resp["results"]
        chap_list = []
        for elem in resp:
            chap_list.append(self._create_chapter(elem))

        return chap_list
    
    def _create_author(self, elem):
        author = Author()
        author._AuthorFromDict(elem)
        return author

    def _create_authors_list(self, resp) -> List[Author]:
        resp = resp["results"]
        authors_list = []
        for elem in resp:
            authors_list.append(self._create_author(elem))

        return authors_list

    def get_manga_list(self, **kwargs):
        url = f"{self.URL}/manga"
        resp = self._request_url(url, 'GET', params=kwargs)
        return self._create_manga_list(resp)

    def view_manga_by_id(self, id: str)-> Manga:
        url = f"{self.URL}/manga/{id}"
        resp = self._request_url(url, "GET")
        return self._create_manga(resp)
    
    def random_manga(self):
        url = f"{self.URL}/manga/random"
        resp = self._request_url(url, "GET")
        return self._create_manga(resp)
    
    def tag_list(self):
        url = f"{self.URL}/manga/tag"
        resp = self._request_url(url, "GET")
        return self._create_tag_list(resp)
    
    def manga_feed(self, id : str, **kwargs):
        url = f"{self.URL}/manga/{id}/feed"
        resp = self._request_url(url, "GET", params = kwargs)
        return self._create_chapter_list(resp)

    def fetch_chapter_images(self, chapter : Chapter):
        url = f"{self.URL}/at-home/server/{chapter.id}"
        image_server_url = self._request_url(url, "GET")
        image_server_url = image_server_url["baseUrl"].replace("\\", "")
        image_server_url = f"{image_server_url}/data"
        image_urls = []
        for filename in chapter.data:
            image_urls.append(f"{image_server_url}/{chapter.hash}/{filename}")

        return image_urls

    def get_author(self, **kwargs):
        url = f"{self.URL}/author"
        resp = self._request_url(url, "GET", kwargs)
        return self._create_authors_list(resp)

    def get_author_by_id(self, id : str) -> Author:
        url = f"{self.URL}/author/{id}"
        resp = self._request_url(url, "GET")
        return self._create_author(resp)
