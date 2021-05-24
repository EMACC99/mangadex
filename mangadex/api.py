from __future__ import absolute_import

import json
import requests

from typing import Dict, KeysView, Tuple, List, Union

try:
    basestring
except NameError:
    from past.builtins import basestring

try:
    from urllib.parse import urlparse, urlencode
except ImportError:
    from urlparse import urlparse
    from urllib import urlencode

from mangadex import (ApiError, ApiClientError, Manga, Tag, Chapter, User, UserError, ChapterError, Author, ScanlationGroup, CoverArt, CustomList)

class Api():
    def __init__(self, timeout = 5):
        self.URL = 'https://api.mangadex.org'
        self.bearer = None
        self.timeout = timeout

    def _auth_handler(self, json_payload) -> None:
        url = f"{self.URL}/auth/login"
        auth = self._request_url(url, "POST", params = json_payload)
        token = auth['token']['session']
        bearer = {"Authorization" : f"Bearer {token}"}
        self.bearer = bearer

    def _request_url(self, url, method, params = None, headers = None) -> dict:
        if params is None:
            params = {}
        params = {k: v.decode("utf-8") if isinstance(v, bytes) else v for k, v in params.items()}
        
        if method == "GET":
            url = self._build_url(url, params)
            try:
                resp = requests.get(url, headers=headers, timeout=self.timeout)
            except requests.RequestException as e:
                print(f"An error has occured: {e}")
                raise
        elif method == "POST":
            try:
                resp = requests.post(url, json = params, headers=headers, timeout=self.timeout)
            except requests.RequestException as e:
                print(f"An error has occured: {e}")
                raise
        elif method == "DELETE":
            try:
                resp = requests.delete(url, headers= headers, timeout=self.timeout)
            except requests.RequestException as e:
                print(f"An error has occured: {e}")
                raise
        elif method == "PUT":
            try:
                resp = requests.put(url, headers=headers, params=params, timeout=self.timeout)
            except requests.RequestException as e:
                print(f"An error has occured: {e}")
                raise

        content = resp.content
        data = self._parse_data(content if isinstance(content, basestring) else content.decode('utf-8'))
        return data

    def _build_url(self, url, params) -> str:
        if params and len(params) > 0:
            url = url + '?' + self._encode_parameters(params)
        return url

    def _encode_parameters(self, params) -> str:
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
    
    def _check_api_error(self, data : dict): 
        if type(data) == list:
            data = data[0]
        if "result" in data.keys():
            if data['result'] == 'error' or 'error' in data:
                raise ApiError(data['errors'])
            if isinstance(data, (list, tuple)) and len(data) > 0:
                if 'error' in data:
                    raise ApiError(data['errors'])

    def _parse_manga_params(self, params : dict):
        if "authors" in params:
            temp = params.pop("authors")
            params["authors[]"] = temp
        if "artist" in params:
            temp = params.pop("artist")
            params["artist[]"] = temp
        if "excludedTags" in params:
            temp = params.pop("excludedTags")
            params["excludedTags[]"] = temp
        if "originalLanguage" in params:
            temp = params.pop("originalLanguage")
            params["originalLanguage[]"] = temp
        if "includedTags" in params:
            temp = params.pop("includedTags")
            params["includedTags[]"] = temp
        if "publicationDemographic" in params:
            temp = params.pop("publicationDemographic")
            params["publicationDemographic[]"] = temp
        if "ids" in params:
            temp  = params.pop("ids")
            params["ids[]"] = temp
        if "altTitles" in params:
            temp = params.pop("altTitles")
            params["altTitles[]"] = temp
        if "description" in params:
            temp = params.pop("description")
            params["description[]"] = temp
        if "authors" in params:
            temp = params.pop("authors")
            params["authors[]"] = temp
        if "artists" in params:
            temp = params.pop("artists")
            params["artists[]"] = temp
        if "translatedLanguage" in params:
            temp = params.pop("translatedLanguage")
            params["translatedLanguage[]"] = temp
        
        return params

    def _create_manga(self, elem) -> Manga:
        manga = Manga()
        manga._MangaFromDict(elem)
        return manga

    def _create_manga_list(self, resp) -> List[Manga]:
        resp = resp["results"]
        manga_list = []
        for elem in resp:
            manga_list.append(self._create_manga(elem))
        return manga_list

    def _create_tag(self, elem) -> Tag:
        tag = Tag()
        tag._TagFromDict(elem)
        return tag

    def _create_tag_list(self, resp) -> List[Tag]:
        tag_list = []
        for tag in resp:
            tag_list.append(self._create_tag(tag))
        return tag_list

    def _create_chapter(self, elem) -> Chapter:
        chap = Chapter()
        chap._ChapterFromDict(elem)
        return chap

    def _create_chapter_list(self, resp) -> List[Chapter]:
        resp = resp["results"]
        chap_list = []
        for elem in resp:
            chap_list.append(self._create_chapter(elem))
        return chap_list
    
    def _create_author(self, elem) -> Author:
        author = Author()
        author._AuthorFromDict(elem)
        return author

    def _create_authors_list(self, resp) -> List[Author]:
        resp = resp["results"]
        authors_list = []
        for elem in resp:
            authors_list.append(self._create_author(elem))
        return authors_list

    def _create_user(self, elem) -> User:
        user = User()
        user._UserFromDict(elem)
        return user
    
    def _create_user_list(self, resp) -> List[User]:
        resp = resp["results"]
        user_list = []
        for elem in resp:
            user_list.append(self._create_user(elem))
        return user_list

    def _create_group(self, elem) ->  ScanlationGroup:
        group = ScanlationGroup()
        group._ScanlationFromDict(elem)
        return group

    def _create_group_list(self, resp)-> List[ScanlationGroup]:
        resp = resp["results"]
        group_list = []
        for elem in resp:
            group_list.append(self._create_group(elem))
        return group_list  

    def _create_customlist(self, elem) -> CustomList:
        custom_list = CustomList()
        custom_list._ListFromDict(elem)
        return custom_list

    def _create_customlist_list(self, resp) -> List[CustomList]:
        resp = resp["results"]
        custom_lists = []
        for elem in resp:
            custom_lists.append(self._create_customlist(elem))
        return custom_lists

    def _createCoverImage(self, elem) -> CoverArt:
        coverImage = CoverArt()
        coverImage._CoverFromDict(elem)
        return coverImage

    def _createCoverImageList(self, resp) -> List[CoverArt]:
        resp = resp["results"]
        coverimage_list = []
        for elem in resp:
            coverimage_list.append(self._createCoverImage(elem))
        return coverimage_list

    def get_manga_list(self, **kwargs) -> List[Manga]:
        """
        Search a List of Manga

        Parameters
        -------------
        This parameters may be used by ohter methods
        ### QueryParams:

        limit : `int`
        offset : `int`
        title : `str`
        authors : `List[str]`
        artist : `List[str]`
        year : `int`
        includedTags : `List[str]`
        includedTagsMode: `str`. Default `"AND"`. Enum: `"AND"` `"OR"`
        excludedTags : `List[str]`
        exludedTagsMode : `str`. Default `"AND"`, Enum : `"AND"`, `"OR"`
        status : `List[str]`. Items Enum : `"ongoing"`, `"completed"`, `"hiatus"`, `"cancelled"`
        originalLanguage : `List[str]`
        publicationDemographic : `List[str]`. Items Enum: `"shounen"` `"shoujo"` `"josei"` `"seinen"` `"none"`
        ids :  `List[str]`. Limited to 100 per call
        contentRating : `List[str]`. Items Enum : `"safe"` `"suggestive"` `"erotica"` `"pornographic"`
        createdAtSince : `str`. Datetime String with the following format YYYY-MM-DDTHH:MM:SS
        updatedAtSince : `str`. Datetime String with the following format YYYY-MM-DDTHH:MM:SS
        
        Returns
        -------------
        `List[Manga]`. A list of Manga objects

        Raises
        -------------
        `ApiError`

        `MangaError`
        """            
        params = kwargs
        params = self._parse_manga_params(params)
        url = f"{self.URL}/manga"
        resp = self._request_url(url, 'GET', params=params)
        return self._create_manga_list(resp)

    def view_manga_by_id(self, id: str)-> Manga:
        """
        Get a Manga by its id

        Parameters
        ------------
        id: `str`. The manga id

        Returns
        -------------
        `Manga`. A Manga object

        Raises
        ------------
        `ApiError`

        `MangaError`
        """
        url = f"{self.URL}/manga/{id}"
        resp = self._request_url(url, "GET")
        return self._create_manga(resp)
    
    def random_manga(self) -> Manga:
        """
        Get a random Manga

        Returns
        ----------
        `Manga`. A Manga object

        Raises
        ----------
        `ApiError`

        `MangaError`
        """
        url = f"{self.URL}/manga/random"
        resp = self._request_url(url, "GET")
        return self._create_manga(resp)

    def create_manga(self, title : str, **kwargs) -> Manga:
        """
        Creates a manga

        Params
        -----------
        title : `str`. The manga title

        ### Optional Parameters
        altTitles : `List[Dict[str,str]]`. The alt titles
        description : `Dict[str,str]`. The alt titles in different languages
        authors : `List[str]`. The list of author id's
        artists : `List[str]`. The list of artist id's
        links : `Dict[str,str]`. The links in differents sites (al, ap, bw, mu, etc). Please refer to the [documentation](https://api.mangadex.org/docs.html#section/Static-data/Manga-links-data)
        originalLanguage : `str`. The original Language
        lastVolume : `str`. The last volume
        lastChapter : `str`. The last chapter
        publicationDemographic : `str`.
        status : `str`.
        year : `int`.
        contentRating : `str`.
        modNotes : `str`

        Returns
        ------------
        `Manga`. A manga object if `ObjReturn` is set to `True`
        """
        kwargs = self._parse_manga_params(kwargs)
        url = f"{self.URL}/manga"
        kwargs["title"] = title
        resp = self._request_url(url, "POST", params=kwargs, headers=self.bearer)
        return  self._create_manga(resp)

    def get_manga_volumes_and_chapters(self, id : str) -> Dict[str, str]:
        """
        Get a manga volumes and chapters

        Parameters
        ------------
        id : `str`. The manga id

        Returns
        ------------
        `Dict[str, str]`. A dictionary with the volumes and the chapter id's
        """
        url = f"{self.URL}/manga/{id}/aggregate"
        resp = self._request_url(url, "GET")
        return resp["result"]

    def update_manga(self, id : str, ObjReturn : bool = False ,**kwargs) -> Manga:
        """
        Updates a manga parameters

        Parameters
        -------------
        ### Required parameters
        id : `str`. The manga id
        version : `int`
        ObjReturn : `bool`. `True` if you want a Manga Object return

        ### Optional Parameters
        title : `Dict[str,str]`. The manga title
        altTitles : `List[Dict[str,str]]`. The alt titles
        description : `Dict[str,str]`. The alt titles in different languages
        authors : `List[str]`. The list of author id's
        artists : `List[str]`. The list of artist id's
        links : `Dict[str,str]`. The links in differents sites (al, ap, bw, mu, etc). Please refer to the [documentation](https://api.mangadex.org/docs.html#section/Static-data/Manga-links-data)
        originalLanguage : `str`. The original Language
        lastVolume : `str`. The last volume
        lastChapter : `str`. The last chapter
        publicationDemographic : `str`.
        status : `str`.
        year : `int`.
        contentRating : `str`.
        modNotes : `str`

        Returns
        ------------
        `Manga`. A manga object if `ObjReturn` is set to `True`
        """
        kwargs = self._parse_manga_params(kwargs)
        url = f"{self.URL}/manga/{id}"
        resp = self._request_url(url, "PUT", params=kwargs, headers=self.bearer)
        if ObjReturn:
            return self._create_manga(resp)
    
    def delete_manga(self, id : str) -> None:
        """
        Deletes a manga
        
        Parameters
        ------------
        id : `str`. The manga id

        Returns
        -----------
        `None`
        """
        url = f"{self.URL}/manga{id}"
        self._request_url(url, "DELETE", headers=self.bearer)

    def get_manga_read_markes(self, id : str) -> List[Chapter]: # this needs a performance update
        """
        A list of Chapter Id's That are marked fro the given manga Id
        

        Parameters
        ------------
        id : `str`. The Manga id

        Returns
        -------------
        `List[Chapters]`. A list of chapters that are marked as read
        """
        url = f"{self.URL}/manga/{id}/read"
        resp = self._request_url(url, "GET", headers=self.bearer)
        chap_ids = resp["data"]
        return [self.get_chapter(chap) for chap in chap_ids] # I think this is 

    def tag_list(self) -> List[Tag]:
        """
        Get the list of available tags

        Returns
        ------------
        `List[Tag]`. A list of Tag objects

        Raises
        -----------
        `ApiError`

        `TagError`
        """
        url = f"{self.URL}/manga/tag"
        resp = self._request_url(url, "GET")
        return self._create_tag_list(resp)
    
    def manga_feed(self, id : str, **kwargs) -> List[Chapter]:
        """
        Get the manga feed

        Parameters
        ------------
        
        id `str`, Required. The manga id

        ### QueryParams:

        limit : `int`
        offset : `int`
        translatedLanguage : `List[str]`. The translated laguages to query
        createdAtSince : `str`. Datetime String with the following format YYYY-MM-DDTHH:MM:SS
        updatedAtSince : `str`. Datetime String with the following format YYYY-MM-DDTHH:MM:SS

        Returns
        -------------
        `List[Chapter]` A list of Chapter Objects

        Raises
        -------------
        `ApiError`

        `ChapterError`
        """
        kwargs = self._parse_manga_params(kwargs)
        url = f"{self.URL}/manga/{id}/feed"
        resp = self._request_url(url, "GET", params = kwargs)
        return self._create_chapter_list(resp)

    def chapter_list(self, **kwargs) -> List[Chapter]:
        """
        The list of chapters. To get the chpaters of a specific manga the manga parameter must be provided

        Parameters
        -----------
        ### QueryParams:

        limit : `int`
        offset : `int`
        title : `str`
        groups : `[str]`
        uploader : `str`    
        manga : `str`
        volume : `str`
        chapter : `str`
        translatedLanguage : `str`
        createdAtSince : `str`. Datetime String with the following format YYYY-MM-DDTHH:MM:SS
        updatedAtSince : `str`. Datetime String with the following format YYYY-MM-DDTHH:MM:SS
        publishAtSince : `str`. Datetime String with the following format YYYY-MM-DDTHH:MM:SS

        Returns
        ----------
        `List[Chpater]` A list of Chpater Objects

        Raises
        -------------
        `ApiError`

        `ChapterError`
        """
        if "groups" in kwargs:
            temp = kwargs.pop("groups")
            kwargs["groups[]"] = temp
        url = f"{self.URL}/chapter"
        resp = self._request_url(url, "GET", params= kwargs)
        return self._create_chapter_list(resp)

    def get_chapter(self, id: str) -> Chapter:
        """
        Get a Chapter by its id


        Parameters
        ------------
        id : `str` The chapter id

        Returns
        ------------
        `Chapter` A chapter Object

        Raises
        ------------
        `ApiError`

        `ChapterError`

        """
        url = f"{self.URL}/chapter/{id}"
        resp = self._request_url(url, "GET")
        return self._create_chapter(resp)
        

    def fetch_chapter_images(self, chapter : Chapter) -> List[str]: #maybe make this an async function?
        """
        Get the image links for a given chapter

        Params
        -----------
        chapter : `Chapter`. The chapter 

        Returns
        -----------
        `List[str]`. A list with the links with the chapter images

        NOTE: There links are valid for 15 minutes until you need to renew the token

        Raises
        -----------
        `ApiError`
        """
        url = f"{self.URL}/at-home/server/{chapter.id}"
        image_server_url = self._request_url(url, "GET")
        image_server_url = image_server_url["baseUrl"].replace("\\", "")
        image_server_url = f"{image_server_url}/data"
        image_urls = []
        for filename in chapter.data:
            image_urls.append(f"{image_server_url}/{chapter.hash}/{filename}")

        return image_urls

    def get_author(self, **kwargs) -> List[Author]:
        """
        Get the author List

        Parameters
        ------------

        limit : `int`
        offset : `int`
        ids : `string`. Array of ids 
        name : `str`

        Returns
        -----------
        `List[Author]`. A list of Author objects

        Raises
        ------------
        `ApiError`

        `AuthorError`

        """
        url = f"{self.URL}/author"
        resp = self._request_url(url, "GET", kwargs)
        return self._create_authors_list(resp)

    def get_author_by_id(self, id : str) -> Author:
        """
        Get's an author by its id

        Parameters
        -------------

        id `str` The id of the author

        Returns
        ------------
        `Author`

        Raises
        ------------
        `ApiError`

        `AuthorError`
        """
        url = f"{self.URL}/author/{id}"
        resp = self._request_url(url, "GET")
        return self._create_author(resp)

    def create_author(self, name : str, version : int, ObjReturn : bool = False) -> Author:
        """
        Creates an Author

        Parameters
        --------------
        name : `str`. The author name
        version : `int`. The version of the author
        ObjReturn : `bool`.  `True` if you want a Author Object return

        Returns
        --------------
        `Author` if `ObjReturn` is `True`
        """
        url = f"{self.URL}/author"
        params = {"name" : name, "version" : version}
        resp = self._request_url(url, "POST", params=params, headers=self.bearer)
        if ObjReturn:
            return self._create_author(resp)
    
    def update_author(self, id : str, version : int, name : str = None, ObjReturn : bool = False) -> Author:
        """
        Updates an Author

        Parameters
        -------------
        id : `str`. Required. The author id
        version : `int`. Required
        name : `str`. 
        ObjReturn : `bool`.  `True` if you want a Author Object return

        Returns
        -----------
        `Author` if `ObjReturn` is `True`
        """
        url = f"{self.URL}/author/{id}"
        params  = {"version" : version}
        if name is not None:
            params["name"] = name
        resp = self._request_url(url, "PUT", params=params, headers=self.bearer)

        if ObjReturn:
            return self._create_author(resp)
        
    def delete_author(self, id : str) -> None:
        """
        Deletes an author

        Paratemets
        ---------------
        id : `str`. Required. The author id

        Returns
        --------------
        `None`
        """
        url = f"{self.URL}/author/{id}"
        self._request_url(url, "DELETE", headers=self.bearer)
    

    def get_user(self, id : str) -> User:
        """
        Get User by its id

        Parameters
        ------------
        id `str` The user id

        Returns
        ------------
        `User`

        Raises
        ------------
        `ApiError`

        `UserError`
        """
        url = f"{self.URL}/user/{id}"
        resp = self._request_url(url, "GET")
        return self._create_user(resp)
    
    def scanlation_group_list(self, limit : int = None, offset : int = None, group_ids : List[str] = None, name : str = None) -> List[ScanlationGroup]:
        """
        Get the scanlation groups list

        Parameters
        --------------
        ### Optional

        limit : `int`
        offset : `int`
        group_ids : `List[str]`
        name : `str`

        Returns
        -------------
        `List[ScanlationGroup]`
        """
        
        url = f"{self.URL}/group"
        params = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if group_ids is not None:
            params["ids[]"] = group_ids
        if name is not None:
            params["name"] = name
        
        resp = self._request_url(url, "GET", params=params)
        return self._create_group_list(resp)

    def login(self, username : str, password : str):
        """
        Method to login into the website

        Parameters
        ---------------
        username `str` your username

        password `str` your password

        Raises
        ---------------
        `ApiError`

        """
        self._auth_handler(json_payload= {"username" : username, "password" : password})

    def me(self) -> User:
        """
        Get your user info

        Return
        ---------
        `User`

        """
        url = f"{self.URL}/user/me"
        resp = self._request_url(url, "GET", headers= self.bearer)
        return self._create_user(resp)

    def get_my_mangalist(self, **kwargs) -> List[Manga]:
        """
        Get the mangas you follow

        Parameters
        -------------
        limit `int`

        offset `int`

        Returns
        -------------
        `List[Manga]`

        """
        url = f"{self.URL}/user/follows/manga"
        resp = self._request_url(url, "GET", params = kwargs, headers=self.bearer)
        return self._create_manga_list(resp)
    
    def get_my_followed_groups(self, **kwargs) -> List[ScanlationGroup]:
        """
        Get the Scanlination Groups you follow

        Parameters
        -------------
        limit `int`

        offset `int`

        Returns
        -------------
        `List[ScanlationGroup]`
        """
        url = f"{self.URL}/user/follows/group"
        resp = self._request_url(url, "GET", params=kwargs, headers= self.bearer)
        return self._create_group_list(resp)

    def get_my_followed_users(self, **kwargs) -> List[User]:
        """
        Get the users you follow

        Parameters
        -------------
        limit : `int`

        offset : `int`

        Returns
        -------------
        `List[User]`
        
        """
        url = f"{self.URL}/user/follows/user"
        resp = self._request_url(url, "GET", params=kwargs, headers=self.bearer)
        return self._create_user_list(resp)

    def get_manga_reading_status(self, id : str) -> str:
        """
        Get a manga reading status given its id

        Parameters
        ------------
        id : `str`. The manga id

        Returns
        ------------
        `str` The manga reading status

        """
        url = f"{self.URL}/manga/{id}/status"
        resp = self._request_url(url, "GET", headers=self.bearer)
        return resp["status"]

    def get_all_manga_reading_status(self, status : str = None) -> Dict[str, str]:
        """
        Get all Manga followed by the user reading status

        Parameters
        ------------

        status : `str`. Optional. Values : `"reading"` `"on_hold"` `"plan_to_read"` `"dropped"` `"re_reading"` `"completed"`

        Returns
        -----------

        `Dict[str,str]` A dictionary with the Manga id and its status
        """
        url = f"{self.URL}/manga/status"
        resp = self._request_url(url, "GET", params={"status": status}, headers=self.bearer)
        return resp["statuses"]
    

    def follow_manga(self, id  : str) -> None:
        """
        Follow a manga

        Paramerets
        --------------

        id : `str`. The manga id

        Returns
        -------------
        `None`

        Raises
        -------------
        `ApiError`
        """
        url = f"{self.URL}/manga/{id}/follow"
        self._request_url(url, "POST", headers=self.bearer)
    
    def unfollow_manga(self, id : str) -> None:
        """
        Unfollow a Manga

        Parameters
        -------------
        id : `str`. The manga id

        Returns
        ------------
        `None`

        Raises
        -----------
        `ApiError`
        """
        
        url = f"{self.URL}/manga/{id}/follow"
        self._request_url(url, "DELETE", headers=self.bearer)

    def update_manga_reading_status(self, id : str, status : str ) -> None:
        """
        Update the reading stauts of a manga

        Parameters
        -------------

        id : `str`. The manga id
        status : `str`. Values : `"reading"` `"on_hold"` `"plan_to_read"` `"dropped"` `"re_reading"` `"completed"`

        Returns
        -------------
        `None`

        Raises
        -------------
        `ApiError`
        """
        url = f"{self.URL}/manga/{id}/status"
        self._request_url(url, "POST", params={"status" : status}, headers=self.bearer)

    
    def add_manga_to_customlist(self, id : str, listId :str) -> None:
        """
        Adds a manga to a custom list

        Parameters
        --------------
        id : `str`. The manga id
        listId : `str`. The list id

        Returns
        -------------
        `None`
 
        """
        url = f"{self.URL}/{id}/list{listId}"
        self._request_url(url, "POST", headers=self.bearer)
    
    def remove_manga_from_customlist(self, id : str, listId : str) -> None:
        """
        Removes a manga from a custom list

        Parameters
        ------------
        id : `str`. The manga id
        listId : `str`. The list id

        Returns
        ------------
        `None`

        """
        url = f"{self.URL}/manga/{id}/list/{listId}"
        self._request_url(url, "DELETE", headers=self.bearer)

    def create_customlist(self, name : str, visibility : str = "public", manga : List[str] = None, version : int = 1) -> None:
        """
        Creates a custom list

        Parameters
        -------------
        ### QueryParams:

        name : `str`. The custom list name
        visibility : `str. The visibility of the custom list
        manga : `List[str]`. List of manga ids

        Returns
        -----------
        `None`
        """
        url = f"{self.URL}/list"
        params = {"name" : name, "version" : version}
        params["visibility"] =  visibility
        params["manga[]"] = manga

        self._request_url(url, "POST", params=params)

    def get_customlist(self, id : str) -> CustomList:
        """
        Get a custom list by its id

        Parameters
        ------------
        id : `str`. The id of the custom list

        Returns
        ------------
        `CustomList`
        
        """
        url = f"{self.URL}/list/{id}"
        resp = self._request_url(url, "GET", headers=self.bearer)
        return self._create_customlist(resp["result"])
    
    def update_customlist(self, id : str, **kwargs) -> CustomList:
        """
        Update a custom list

        Parameters
        ------------
        id : `str`. The custom list id

        ### QueryParams:

        name : `str`. The custom list name
        visibility : `str`. Values : `"public"` `"private"`

        Returns
        -----------
        `CustomList`
        """
        url = f"{self.URL}/list/{id}"
        resp = self._request_url(url, "PUT", params= kwargs, headers=self.bearer)
        return self._create_customlist(resp["result"])
        
    def delete_customlist(self, id : str) -> None:
        """
        Deletes a Custom List

        Parameters
        ------------
        id : `str`. The custom list id

        Returns
        ----------
        `None`
        """
        url = f"{self.URL}/list{id}"
        self._request_url(url, "DELETE", headers=self.bearer)
    
    def get_my_customlists(self, **kwargs) -> List[CustomList]:
        """
        Get my custom lists

        Parameters
        ------------
        ### QueryParams:

        limit : `int`. The limit of custom lists to return
        offset : `int`. The amout of offset

        Returns
        ----------
        `List[CustomList]`

        """
        url = f"{self.URL}/user/list"
        resp = self._request_url(url, "GET", params=kwargs, headers=self.bearer)
        return self._create_customlist_list(resp)

    def get_user_customlists(self, id : str, **kwargs) -> List[CustomList]:
        """
        Get a user's custom list. This will list only public custom lists

        Parameters
        ------------
        id : `str`. the User id

        ### QueryParams:

        limit : `int`. The limit of custom lists to return
        offset : `int`. The amout of offset

        Returns
        ----------
        `List[CustomList]`
        """
        url = f"{self.URL}/user/{id}/list"
        resp = self._request_url(url, "GET", params=kwargs, headers=self.bearer)
        return self._create_customlist_list(resp)
    
    def get_customlist_manga_feed(self, id : str, **kwargs) -> List[Chapter]:
        """
        Get the chapter feed of a given custom list. 

        Paramters
        ------------
        id : `str`. The custom list id

        ### QueryParams:

        limit : `int`. 
        offset : `int`
        translatedLanguage : `List[str]`. The translated laguages to query
        createdAtSince : `str`. Datetime String with the following format YYYY-MM-DDTHH:MM:SS
        updatedAtSince : `str`. Datetime String with the following format YYYY-MM-DDTHH:MM:SS
        publishAtSince : `str`. Datetime String with the following format YYYY-MM-DDTHH:MM:SS

        Returns
        -----------
        `List[Chapter]`

        """
        url = f"{self.URL}/user/{id}/feed"
        resp = self._request_url(url, "GET", params=kwargs, headers=self.bearer)
        return  self._create_chapter_list(resp)

    def get_coverart_list(self, **kwargs):
        """
        Get the list of cover arts (like the manga feed)
        """
        if "manga" in kwargs:
            temp = kwargs.pop("manga")
            kwargs["manga[]"] = temp 
        url = f"{self.URL}/cover"
        resp = self._request_url(url, "GET", params=kwargs)
        return self._createCoverImageList(resp)
    
    def get_single_cover(self, cover : CoverArt):
        url = f"{self.URL}/cover/{cover.id}"
        resp = self._request_url(url, "GET")
        return resp
        
    def upload_cover(self, manga_id : str, file : str, ObjReturn : bool = False):
        url = f"{self.URL}/cover/{manga_id}"
        resp = self._request_url(url, "POST", params = {"file" : file}, headers= self.bearer)
        
        return self._createCoverImage(resp) if ObjReturn else None

    def edit_cover(self, coverId : str, description : str, volume : str = None, version : int = None, ObjReturn : bool = False) -> Union[None, CoverArt]:
        """
        Edit a cover parameters

        Parameters
        ------------
        coverId : `str`. The coverId
        description : `str`. The cover description
        volume : `str`. The volume representing the volume
        version : `int`. The version of the cover
        ObjReturn : `bool`. Default `False`. If set to `True`, it will return a CoverArt

        Returns
        -----------
        `CoverArt` if `ObjReturn` set to `True`
        
        """
        if version is None:
            raise ValueError("Version cannot be null")
        
        params = {"volume" : volume, "version" : version}
        if description is not None:
            params["description"] = description

        url = f"{self.URL}/cover/{coverId}"
        resp = self._request_url(url, "PUt", params=params, headers=self.bearer)

        return self._createCoverImage(resp) if ObjReturn else None
    
    def delete_cover(self, coverId : Union[str , CoverArt]):
        """
        Deletes a cover

        Params
        -----------
        coverId : `str` | `CoverArt`. The cover id or the cover object
        """
        if not coverId:
            raise ValueError("coverId cannot be empty")
        if type(coverId) == CoverArt:
            coverId = coverId.id
        url = f"{self.URL}/cover/{coverId}"
        self._request_url(url, "DELETE", headers= self.bearer)
    
    def fetch_cover_image(self, manga : Union[Manga, str], cover : Union[CoverArt, str], quality : str = "source") -> str:
        """
        Returns the url of a cover art

        Parameters
        -------------
        manga : `str` | `Manga`. the manga id or the manga object
        cover : `str` | `CoverArt`. Ther cover id or a cover object

        Returns
        -----------
        url : `str`. The cover url
        """
        if type(manga) == Manga:
            manga = manga.id
        if type(cover) == CoverArt:
            cover = cover.fileName
        url = f"https://uploads.mangadex.org/covers/{manga}/{cover}"
        
        if quality == "medium":
            url = f"{url}.512.jpg"
        elif quality == "small":
            url = f"{url}.256.jpg"
        
        return url