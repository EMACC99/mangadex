"""Module providing Chapter and Manga info"""

from __future__ import absolute_import

import datetime

from dateutil.parser import parse
from typing_extensions import Dict, List, Self, Union

from mangadex.url_models import URLRequest

from .auth import Api, Auth


class Chapter:
    """Class that retrieves series chapters"""

    def __init__(self, auth: Union[Auth, None] = None) -> None:
        self.auth = auth
        self.api = Api()

        self.chapter_id: str = ""
        self.title: str = ""
        self.volume: str = ""
        self.chapter: Union[float, None] = None
        self.translated_language: str = ""
        self.hash = ""
        self.data = ""
        self.manga_id: str = ""
        self.group_id: str = ""
        self.uploader: str = ""
        self.created_at: datetime.datetime
        self.updated_at: datetime.datetime
        self.publish_at: datetime.datetime

    # Data Processors

    @classmethod
    def chapter_from_dict(cls, resp: dict) -> "Chapter":
        """Create a Chapter from JSON

        Args:
            resp: Raw JSON data

        Returns:
            Chapter: Chapter information
        """
        chapter = cls()
        try:
            resp = resp["data"]
        except KeyError:
            pass

        if resp["type"] != "chapter" or not resp:
            raise ValueError("The data provided is not a Chapter")

        attributes = resp["attributes"]

        chapter.chapter_id = resp["id"]
        chapter.title = attributes["title"]
        chapter.volume = attributes["volume"] if not "null" else None
        chapter.chapter = (
            float(attributes["chapter"]) if attributes["chapter"] is not None else None
        )
        chapter.translated_language = attributes["translatedLanguage"]
        for relations in resp["relationships"]:
            if relations["type"] == "scanlation_group":
                chapter.group_id = relations["id"]
            elif relations["type"] == "manga":
                chapter.manga_id = relations["id"]
            elif relations["type"] == "user":
                chapter.uploader = relations["id"]

        return chapter

    @staticmethod
    def __parse_chapter_list_args(params: Dict[str, str]) -> Dict[str, str]:
        if "groups" in params:
            params["groups[]"] = params.pop("groups")
        if "volume" in params:
            params["volume[]"] = params.pop("volume")
        if "translatedLanguage" in params:
            params["translatedLanguage[]"] = params.pop("translatedLanguage")

        return params

    @staticmethod
    def create_chapter_list(resp: dict) -> List["Chapter"]:
        """Creates a list of Chapters from JSON

        Args:
            resp: Raw response from chapter list

        Returns:
            List[Chapter]: List of Chapter information
        """
        resp = resp["data"]
        chap_list = []
        for elem in resp:
            chap_list.append(Chapter.chapter_from_dict(elem))
        return chap_list

    @property
    def url(self):
        """Returns the mangadex url"""
        return f"{self.api.url}/chapter/{self.chapter_id}"

    def __eq__(self, other: Self) -> bool:
        my_vals = [self.chapter_id, self.manga_id, self.chapter]
        other_vals = [other.chapter_id, other.manga_id, other.chapter]
        return my_vals == other_vals

    def __ne__(self, other: Self) -> bool:
        return not self.__eq__(other)

    def __repr__(self) -> str:
        part1 = f"Chapter(chapter_id = {self.chapter_id}, title = {self.title}, \
                        volume = {self.volume}, chapter = {self.chapter}, \
                        translatedLanguage = {self.translated_language} \n"
        part2 = f"data = List[filenames], publishAt = {self.publish_at}, \
                        createdAt = {self.created_at}, uploadedAt = {self.updated_at}, \
                        group_id = {self.group_id}, manga_id = {self.manga_id}, \
                        uploader = {self.uploader})"
        return f"{part1}{part2}"

    def get_chapter_list(self, **kwargs) -> List["Chapter"]:
        """Get information about multiple chapters

        Args:
            limit: int: How many chapters to return
            offset: int:
            ids[]: list[str]: Chapter IDs
            groups[]: list[str]: Group UUIDs
            uploader: str: Uploader UUID
            manga: str: Manga UUID
            volume[]: str: Volume UUID
            chapter: str: Chapter UUID
            translatedLanguage[]: str: List of accepted translated language, default is any.

        Returns:
            List[Chapter]: List of Chapters
        """
        params = self.__parse_chapter_list_args(kwargs)
        url = f"{self.api.url}/chapter"
        resp = URLRequest.request_url(
            url, "GET", timeout=self.api.timeout, params=params
        )
        return Chapter.create_chapter_list(resp)

    def get_chapter_by_id(self, chapter_id: str) -> "Chapter":
        """Get information about a single chapter

        Args:
            chapter_id: The chapter ID
            includes[] (list[str]): List of included entries. Values: manga, scanlation_group, user
            
        Returns:
            Chapter: Chapter info
        """
        url = f"{self.api.url}/chapter/{chapter_id}"
        resp = URLRequest.request_url(url, "GET", timeout=self.api.timeout)
        return Chapter.chapter_from_dict(resp)

    def get_manga_volumes_and_chapters(self, manga_id: str, **kwargs) -> Dict[str, str]:
        """Get a series volumes and chapters

        Args:
            manga_id: The series
            translatedLanguage[]: List of accepted translated language, default is any.
            groups[]: List of groups to get the releases for, default is any.

        Returns:
            Dict[str, str] List of Chapters per volume
        """
        params = None
        if "translatedLanguage" in kwargs:
            params = {"translatedLanguage[]": kwargs["translatedLanguage"]}
        url = f"{self.api.url}/manga/{manga_id}/ aggregate"
        resp = URLRequest.request_url(
            url, "GET", timeout=self.api.timeout, params=params
        )
        return resp["volumes"]

    def fetch_chapter_images(self) -> List[str]:  # maybe make this an async function?
        """
        Get the image links for the chapter

        Returns
        -----------
        (List[str]): A list with the links with the chapter images

        NOTE: There links are valid for 15 minutes until you need to renew the token

        Raises
        -----------
        `ApiError`
        """
        url = f"https://api.mangadex.org/at-home/server/{self.chapter_id}"
        image_server_url = URLRequest.request_url(url, "GET", timeout=5)
        self.hash = image_server_url["chapter"]["hash"]
        self.data = image_server_url["chapter"]["data"]
        image_server_url = image_server_url["baseUrl"].replace("\\", "")
        image_server_url = f"{image_server_url}/data"
        image_urls = []
        for file_name in self.data:
            image_urls.append(f"{image_server_url}/{self.hash}/{file_name}")

        return image_urls

    def update_chapter(
        self, chapter_id: str, body: dict, obj_return: bool = True
    ) -> Union["Chapter", None]:
        """Update a chapter

        Args:
            chapter_id: ID of the chapter to be updated.
            body: Body of the update.
            ObjReturn: bool: Default `True` If set to `False`, it will not return the info

        Returns:
            Union[Chapter, None]: Updated Chapter
        """
        url = f"{self.api.url}/list/{chapter_id}"
        headers = self.auth.get_bearer_token()
        headers["Content-Type"] = "application/json"
        resp = URLRequest.request_url(
            url, "PUT", params=body, headers=headers, timeout=self.api.timeout
        )
        return self.chapter_from_dict(resp["data"]) if not obj_return else None

    def delete_chapter(self, chapter_id: str) -> None:
        """Delete a chapter

        Args:
            chapter_id: ID of the chapter to be deleted.

        Returns:
            dict: result
        """
        url = f"{self.api.url}/chapter/{chapter_id}"
        resp = URLRequest.request_url(
            url,
            "DELETE",
            headers=self.auth.get_bearer_token(),
            timeout=self.api.timeout,
        )
        if resp["result"] == "error":
            raise ValueError(resp["errors"]["detail"])
        else:
            return None


class Cover:
    """Class used to get series covers."""

    def __init__(self, auth: Union[Auth, None] = None) -> None:
        self.auth = auth
        self.api = Api()

        self.cover_id: str = ""
        self.volume: str = ""
        self.file_name: str = ""
        self.description: str = ""
        self.created_at: datetime.datetime
        self.updated_at: datetime.datetime
        self.manga_id: str = ""
        self.locale: str = ""

    @classmethod
    def cover_from_dict(cls, data: dict) -> "Cover":
        """Get cover from json

        Args:
            data (dict): Raw JSON data

        Raises:
            ValueError: Raised when the data provided is not a Cover JSON

        Returns:
            Cover: The Coverart ids
        """
        try:
            data = data["data"]
        except (KeyError, TypeError):
            pass

        if data["type"] != "cover_art" or not data:
            raise ValueError("The data provided is not a cover")

        cover = cls()

        attributes = data["attributes"]

        cover.cover_id = data["id"]
        cover.volume = attributes["volume"]
        cover.file_name = attributes["fileName"]
        cover.locale = attributes["locale"]
        cover.description = attributes["description"]
        cover.created_at = parse(attributes["createdAt"])
        cover.updated_at = parse(attributes["updatedAt"])
        cover.manga_id = data["relationships"][0]["id"]

        return cover

    @staticmethod
    def create_coverart_list(resp: dict) -> List["Cover"]:
        """Creates a list of CoverArt from JSON

        Returns:
            List[Cover]: List of cover urls
        """

        resp = resp["data"]
        coverimage_list = []
        for elem in resp:
            coverimage_list.append(Cover.cover_from_dict(elem))
        return coverimage_list

    def __repr__(self) -> str:
        return f"CoverArt(id = {self.cover_id}, mangaId = {self.manga_id}, volume = {self.volume}, \
                            file_name = {self.file_name}, description = {self.description}, \
                            createdAt = {self.created_at}, updatedAt = {self.updated_at})"

    @staticmethod
    def __parse_coverart_params(params: Dict[str, str]) -> Dict[str, str]:
        if "manga" in params:
            params["manga[]"] = params.pop("manga")
        if "ids" in params:
            params["ids[]"] = params.pop("ids")
        if "uploaders" in params:
            params["uploaders[]"] = params.pop("uploaders")

        return params

    def fetch_cover_image(self, quality: str = "source") -> str:
        """Returns URLS of cover art

        Args:
            quality (str, optional): The quality you want to get the URL for. Defaults to "source".

        Returns:
            str: The image URL
        """

        url = f"https://uploads.mangadex.org/covers/{self.manga_id}/{self.file_name}"

        if quality == "medium":
            url = f"{url}.512.jpg"
        elif quality == "small":
            url = f"{url}.256.jpg"

        return url

    def get_coverart_list(self, **kwargs) -> List["Cover"]:
        """Gets list of CoverArt

        Returns:
            List["Cover"]: List of CoverArts
        """
        params = self.__parse_coverart_params(kwargs)
        url = f"{self.api.url}/cover"
        resp = URLRequest.request_url(
            url, "GET", params=params, timeout=self.api.timeout
        )
        return self.create_coverart_list(resp)

    def get_cover(self, cover_id: str) -> "Cover":
        """Get a cover image

        Args:
            cover_id: The cover id

        Returns:
            Cover: Cover information
        """
        url = f"{self.api.url}/cover/{cover_id}"
        resp = URLRequest.request_url(url, "GET", timeout=self.api.timeout)
        return self.cover_from_dict(resp)

    def upload_cover(
        self, manga_id: str, file_name: str, obj_return: bool = False
    ) -> Union["Cover", None]:
        """Upload a Cover

        Args:
            manga_id: ID of the series you want to upload a cover
            file_name: file_name of the cover
            ObjReturn: Default `False` If set to `True`, it will return the info.

        Returns:
            Union[Cover, None]: Cover info or None if ObjReturn is False
        """
        url = f"{self.api.url}/cover/{manga_id}"
        with open(file_name, "rb") as f:
            file = f.read()

        resp = URLRequest.request_url(
            url,
            "POST",
            params={"file": file},
            headers=self.auth.get_bearer_token(),
            timeout=self.api.timeout,
        )
        return self.cover_from_dict(resp) if obj_return else None

    def edit_cover(
        self,
        cover_id: str,
        description: str,
        locale: str = "en-us",
        volume: Union[str, None] = None,
        version: Union[int, None] = None,
        obj_return: bool = False,
    ) -> Union[None, Self]:
        """Update a Cover Info

        Args:
            cover_id: The id of the cover
            description: The description of the cover
            locale: Language of the cover
            volume: The volume number of the cover
            version: The version number of the cover info
            ObjReturn: bool: Default `False` If set to `True`, it will return the info

        Returns:
            Union[None, Self]: Cover information or None if ObjReturn is False
        """
        if version is None:
            raise ValueError("Version cannot be null")

        params = {"volume": volume, "locale": locale, "version": version}
        if description is not None:
            params["description"] = description

        url = f"{self.api.url}/cover/{cover_id}"
        resp = URLRequest.request_url(
            url,
            "PUT",
            params=params,
            headers=self.auth.get_bearer_token(),
            timeout=self.api.timeout,
        )
        return self.cover_from_dict(resp) if obj_return else None

    def delete_cover(self, cover_id: Union[str, "Cover"]):
        """Deletes a Cover

        Args:
            cover_id: ID of Cover to delete

        Returns:
            dict: result

        """
        url = f"{self.api.url}/cover/{cover_id}"
        resp = URLRequest.request_url(
            url,
            "DELETE",
            headers=self.auth.get_bearer_token(),
            timeout=self.api.timeout,
        )
        if resp["result"] == "error":
            raise ValueError(resp["errors"]["detail"])
        else:
            return None


class Tag:
    """Class for getting Tags"""

    def __init__(self) -> None:
        """Class used to get and parse tags"""

        self.api = Api()

        self.tag_id: str = ""
        self.name: Dict[str, str] = {}
        self.description: str = ""
        self.group: str = ""

    @classmethod
    def tag_from_dict(cls, resp: dict) -> "Tag":
        """Creates a Tag from a JSON

        Args:
            resp: Raw data from JSON

        Returns:
            Tag: Tag information
        """
        tag = cls()
        try:
            resp = resp["data"]
        except KeyError:
            pass

        if resp["type"] != "tag" or not resp:
            raise ValueError("The data provided is not a Tag")

        attributes = resp["attributes"]

        tag.tag_id = resp["id"]
        tag.name = attributes["name"]
        tag.description = attributes["description"]
        tag.group = attributes["group"]

        return tag

    @staticmethod
    def create_tag_list(resp) -> List["Tag"]:
        """Create a Tag list from JSON

        Args:
            resp: Response from Tag list

        Returns:
            List[Tag]: Tag list
        """
        tag_list = []
        try:
            resp = resp["data"]
        except (TypeError, KeyError):
            pass

        for tag in resp:
            tag_list.append(Tag.tag_from_dict(tag))
        return tag_list

    def __eq__(self, other: Self) -> bool:
        my_vals = [self.tag_id, self.name]
        other_vals = [other.tag_id, other.name]
        return all((me == other for me, other in zip(my_vals, other_vals)))

    def __ne__(self, other: Self) -> bool:
        return not self.__eq__(other)

    def __repr__(self) -> str:
        return f"Tag(tag_id = {self.tag_id}, name = {self.name})"

    def tag_list(self) -> List["Tag"]:
        """Get the list of available tags

        Returns:
            List[Tag]: Tag list
        """
        url = f"{self.api.url}/manga/tag"
        resp = URLRequest.request_url(url, "GET", timeout=self.api.timeout)
        return Tag.create_tag_list(resp)


class Manga:
    """Class for getting Manga Info"""

    def __init__(self, auth: Union[Auth, None] = None):
        self.auth = auth
        self.api = Api()

        self.manga_id: str = ""
        self.title: Dict[str, str] = {}
        self.alt_titles: Dict[str, str] = {}
        self.description: Dict[str, str] = {}
        self.is_locked: bool = False
        self.links: Dict[str, str] = {}
        self.original_language: str = ""
        self.last_volume: str = ""
        self.last_chapter: str = ""
        self.publication_demographic: str = ""
        self.status: str = ""
        self.year: int = 0
        self.content_rating: str = ""
        self.tags: List[Tag] = []
        self.version = 1
        self.created_at: datetime.datetime
        self.updated_at: datetime.datetime
        self.author_id: List[str] = []
        self.artist_id: List[str] = []
        self.cover_id: str = ""

    @classmethod
    def manga_from_dict(cls, data: dict):
        """
        Creates a Manga Object from a JSON
        """
        try:
            data = data["data"]
        except (TypeError, KeyError):
            pass

        if data["type"] != "manga" or not data:
            raise ValueError("The data provided is not a Manga")

        attributes = data["attributes"]

        manga = cls()

        manga.manga_id = data["id"]
        manga.title = attributes["title"]
        manga.alt_titles = attributes["altTitles"]
        manga.description = attributes["description"]
        try:
            manga.is_locked = attributes["isLocked"]
        except KeyError:
            pass

        manga.links = attributes["links"]
        manga.original_language = attributes["originalLanguage"]
        manga.last_volume = attributes["lastVolume"]
        manga.last_chapter = attributes["lastChapter"]
        manga.publication_demographic = attributes["publicationDemographic"]
        manga.status = attributes["status"]
        manga.year = attributes["year"]
        manga.content_rating = attributes["contentRating"]
        manga.tags = Tag.create_tag_list(attributes["tags"])
        manga.created_at = parse(attributes["createdAt"])
        manga.updated_at = parse(attributes["updatedAt"])

        for elem in data["relationships"]:
            if elem["type"] == "author":
                manga.author_id.append(elem["id"])
            elif elem["type"] == "artist":
                manga.artist_id.append(elem["id"])
            elif elem["type"] == "cover_art":
                manga.cover_id = elem["id"]

        return manga

    @staticmethod
    def __parse_manga_params(params: dict) -> dict:
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
            temp = params.pop("ids")
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
            params["availableTranslatedLanguage[]"] = temp
        if "status" in params:
            params["status[]"] = params.pop("status")
        if "contentRating" in params:
            params["contentRating[]"] = params.pop("contentRating")
        return params

    @staticmethod
    def create_manga_list(resp) -> List["Manga"]:
        """
        Creates a manga list from a JSON
        """
        resp = resp["data"]
        manga_list = []
        for elem in resp:
            manga_list.append(Manga.manga_from_dict(elem))
        return manga_list

    @property
    def url(self):
        """
        Return the mangadex url
        """
        return f"{self.api.url}/title/{self.manga_id}"

    def __eq__(self, other: Self) -> bool:
        my_vals = [self.manga_id, self.title, self.created_at, self.author_id]
        other_vals = [other.manga_id, other.title, other.created_at, other.author_id]
        return my_vals == other_vals

    def __ne__(self, other: Self) -> bool:
        return not self.__eq__(other)

    def __repr__(self) -> str:
        temp1 = f"Manga(manga_id = {self.manga_id}, title = {self.title}, \
                altTitles = {self.alt_titles}, description = {self.description}, \
                isLocked = {self.is_locked}, links = {self.links}, \
                originalLanguage = {self.original_language} \n"
        temp2 = f"lastVolume = {self.last_volume}, lastChapter = {self.last_chapter}, \
                publicationDemographic = {self.publication_demographic}, status = {self.status}, \
                year = {self.year}, contentRating = {self.content_rating} \n"
        temp3 = f"createdAt = {self.created_at}, uploadedAt = {self.updated_at}), \
                author_id = {self.author_id}, artist_id = {self.artist_id}, \
                cover_id = {self.cover_id}"
        return f"{temp1}{temp2}{temp3}"

    def get_manga_list(self, **kwargs) -> List["Manga"]:
        """
        Search a list of Manga.

        Args:
            limit (int): Limit the number of results.
            offset (int): Offset the results by this number.
            title (str): Search for manga with this title.
            authors (List[str]): List of authors.
            artist (List[str]): List of artists.
            year (int): Year of publication.
            includedTags (List[Tag.id]): Tags to include.
            includedTagsMode (str): Mode for included tags. Default is "AND".
                Possible Values: "AND", "OR".
            excludedTags (List[Tag.id]): Tags to exclude.
            excludedTagsMode (str): Mode for excluded tags. Default is "AND".
                Enum: "AND", "OR".
            status (List[str]): Status of manga.
                Enum: "ongoing", "completed", "hiatus", "cancelled".
            originalLanguage (List[str]): Original language of the manga.
            publicationDemographic (List[str]): Demographic of publication.
                Enum: "shounen", "shoujo", "josei", "seinen", "none".
            manga_ids (List[str]): List of manga IDs. Limited to 100 per call.
            contentRating (List[str]): Content rating.
                Enum: "safe", "suggestive", "erotica", "pornographic".
            createdAtSince (str): Datetime string in the format YYYY-MM-DDTHH:MM:SS.
            updatedAtSince (str): Datetime string in the format YYYY-MM-DDTHH:MM:SS.

        Returns:
            List[Manga]: A list of Manga objects.

        Raises:
            ApiError: An error occurred with the API.
            MangaError: An error occurred specific to Manga.
        """
        params = kwargs
        params = self.__parse_manga_params(params)
        url = f"{self.api.url}/manga"
        resp = URLRequest.request_url(
            url, "GET", params=params, timeout=self.api.timeout
        )
        return Manga.create_manga_list(resp)

    def get_manga_feed(self, manga_id: str, **kwargs) -> List[Chapter]:
        """
        Get the manga feed

        Args:
            manga_id (str): Required. The manga id
            limit (int): Limit the number of results.
            offset (int): Offset the results by this number.
            createdAtSince (str): Datetime String with the following format YYYY-MM-DDTHH:MM:SS
            updatedAtSince (str): Datetime String with the following format YYYY-MM-DDTHH:MM:SS

        Returns:
            List[Chapter]: A list of Chapter Objects

        Raises:
            ApiError: An error occurred with the API.
            ChapterError: An error occurred specific to Chapter.
        """
        kwargs = self.__parse_manga_params(kwargs)
        url = f"{self.api.url}/manga/{manga_id}/feed"
        resp = URLRequest.request_url(
            url, "GET", timeout=self.api.timeout, params=kwargs
        )
        return Chapter.create_chapter_list(resp)

    def get_manga_by_id(self, manga_id: str) -> "Manga":
        """
        Get a Manga by its id

        Args:
            manga_id (str): Required. The manga id

        Returns:
            Manga: A Manga Object

        Raises:
            ApiError: An error occurred with the API.
            MangaError: An error occurred specific to Manga.
        """
        url = f"{self.api.url}/manga/{manga_id}"
        resp = URLRequest.request_url(url, "GET", timeout=self.api.timeout)
        return Manga.manga_from_dict(resp)

    def get_random_manga(self) -> "Manga":
        """
        Get a random Manga

        Returns:
            Manga: A Manga Object

        Raises:
            ApiError: An error occurred with the API.
            MangaError: An error occurred specific to Manga.
        """
        url = f"{self.api.url}/manga/random"
        resp = URLRequest.request_url(url, "GET", timeout=self.api.timeout)
        return Manga.manga_from_dict(resp)

    def create_manga(self, title: str, **kwargs) -> "Manga":
        """
        Creates a manga

            Args:
            title (str): The manga title

            altTitles (List[Dict[str,str]]): The alt titles
            description Dict[str,str]). The alt titles in different languages
            authors (List[str]):. The list of author id's
            artists (List[str]): The list of artist id's
            links (Dict[str,str]): The links in different sites (al, ap, bw, mu, etc.).
                Please refer to the [documentation](https://api.mangadex.org/docs.html#section/Static-data/Manga-links-data)
            originalLanguage (str): The original Language
            lastVolume (str): The last volume
            lastChapter (str): The last chapter
            publicationDemographic (str):
            status (str):
            year (int):
            contentRating (str):
            modNotes (str):

        Returns:
            Manga: A Manga Object
        """
        params = self.__parse_manga_params(kwargs)
        url = f"{self.api.url}/manga"
        params["title"] = title
        resp = URLRequest.request_url(
            url,
            "POST",
            params=params,
            headers=self.auth.get_bearer_token(),
            timeout=self.api.timeout,
        )
        return Manga.manga_from_dict(resp)


    def update_manga(
        self, manga_id: str, ObjReturn: bool = False, **kwargs
    ) -> Union["Manga", None]:
        """
        Updates a manga parameters

        Args:
            manga_id (str): The manga id
            version (int)
            ObjReturn (bool): `True` if you want a Manga Object return
            altTitles (List[Dict[str,str]]): The alt titles
            description Dict[str,str]). The alt titles in different languages
            authors (List[str]):. The list of author id's
            artists (List[str]): The list of artist id's
            links (Dict[str,str]): The links in different sites (al, ap, bw, mu, etc.).
                Please refer to the [documentation](https://api.mangadex.org/docs.html#section/Static-data/Manga-links-data)
            originalLanguage (str): The original Language
            lastVolume (str): The last volume
            lastChapter (str): The last chapter
            publicationDemographic (str):
            status (str):
            year (int):
            contentRating (str):
            modNotes (str):

        Returns:
            Manga: A manga object if `ObjReturn` is set to `True`
        """
        kwargs = self.__parse_manga_params(kwargs)
        url = f"{self.api.url}/manga/{manga_id}"
        resp = URLRequest.request_url(
            url,
            "PUT",
            params=kwargs,
            headers=self.auth.get_bearer_token(),
            timeout=self.api.timeout,
        )
        if ObjReturn:
            return Manga.manga_from_dict(resp)

    def delete_manga(self, manga_id: str) -> None:
        """
        Deletes a manga

        Args:
            manga_id (str): Required. The manga id
        """
        url = f"{self.api.url}/manga{manga_id}"

        URLRequest.request_url(
            url,
            "DELETE",
            headers=self.auth.get_bearer_token(),
            timeout=self.api.timeout,
        )

    def get_manga_volumes_and_chapters(self, manga_id: str, **kwargs) -> Dict[str, str]:
        """
        Get a manga volumes and chapters

        Args:
            manga_id (str): Required. The manga id
            translatedLanguage (str): 

        Returns:
            (Dict[str, str]): A dictionary with the volumes and the chapter id's
        """
        params = None
        if "translatedLanguage" in kwargs:
            params = {"translatedLanguage[]": kwargs["translatedLanguage"]}
        url = f"{self.api.url}/manga/{manga_id}/aggregate"
        resp = URLRequest.request_url(
            url, "GET", timeout=self.api.timeout, params=params
        )
        return resp["volumes"]

    def get_manga_read_markers(self, manga_id: str) -> List[Chapter]:
        # this needs a performance update
        """
        A list of Chapter ids That are marked as read from the manga 

        Args:
            manga_id (str): Required. The manga id

        Returns
            (List[Chapters]): A list of chapters that are marked as read
        """
        url = f"{self.api.url}/manga/{manga_id}/read"
        resp = URLRequest.request_url(
            url, "GET", timeout=self.api.timeout, headers=self.auth.get_bearer_token()
        )
        chap_ids = resp["data"]
        chapter = Chapter()
        return [chapter.get_chapter_by_id(chap_id) for chap_id in chap_ids]

    def set_manga_read_markers(self, manga_id: str, **kwargs) -> List[Chapter]:
        """
        List of Chapter ids to be marked as read

        Args:
            manga_id (str): Required. The manga id
            chapterIdsUnread (List[str]): Chapter IDs to be set as unread
            chapterIdsRead (List[str]): Chapter IDs to be set as read

        Returns
            List[Chapters]: A list of chapters that are marked as read
        """
        url = f"{self.api.url}/manga/{manga_id}/read"
        resp = URLRequest.request_url(
            url, "GET", timeout=self.api.timeout, params=kwargs,
            headers=self.auth.get_bearer_token()
        )
        return resp

    def get_all_manga_reading_status(
        self, status: Union[str, None] = None
    ) -> Dict[str, str]:
        """
        Get all Manga followed by the user reading status

        Args:
            status (str): Optional.
                Values: `"reading"` `"on_hold"` `"plan_to_read"` `"dropped"` `"re_reading"` `"completed"`

        Returns:
            Dict[str,str]: A dictionary with the Manga id and its status
        """
        url = f"{self.api.url}/manga/status"
        resp = URLRequest.request_url(
            url,
            "GET",
            params={"status": status},
            headers=self.auth.get_bearer_token(),
            timeout=self.api.timeout,
        )
        return resp["statuses"]

    def get_manga_reading_status(self, manga_id: Union[str, int]) -> str:
        """
        Get a manga reading status given its id

        Args:
            manga_id (str): Required. The manga id

        Returns:
            str: The manga reading status
        """
        url = f"{self.api.url}/manga/{manga_id}/status"
        resp = URLRequest.request_url(
            url, "GET", headers=self.auth.get_bearer_token(), timeout=self.api.timeout
        )
        return resp["status"]

    def update_manga_reading_status(self, manga_id: str, status: str) -> None:
        """
        Update the reading status of a manga

        Args:
            manga_id (str): The manga id.
            status (str):
                Values : `reading"` `"on_hold"` `"plan_to_read"` `"dropped"` `"re_reading"` `"completed"`

        Raises:
            ApiError
        """
        url = f"{self.api.url}/manga/{manga_id}/status"
        URLRequest.request_url(
            url,
            "POST",
            params={"status": status},
            headers=self.auth.get_bearer_token(),
            timeout=self.api.timeout,
        )

class Follows:
    """Handles follows for Manga"""
    def __init__(self, auth: Union[Auth, None]):
        self.auth = auth
        self.api = Api()

    
    def follow_manga(self, manga_id: str) -> None:
        """Follow a manga

        Args:
            manga_id: The manga you want to follow
        """
        url = f"{self.api.url}/manga/{manga_id}/follow"
        URLRequest.request_url(url, "POST", headers=self.auth.get_bearer_token(), timeout=self.api.timeout)

    def unfollow_manga(self, manga_id: str) -> None:
        """Follow a manga

        Args:
            manga_id: The manga you want to un follow
        """
        url = f"{self.api.url}/manga/{manga_id}/follow"
        URLRequest.request_url(url, "DELETE", headers=self.auth.get_bearer_token(), timeout=self.api.timeout)

    def get_followed_customlists(self, **kwargs) -> List["CustomList"]:
        """Get user's followed CustomList

        Args:
            limit (int): The limit of custom lists to return
            offset (int): The amount of offset

        Returns:
            List[CustomList]: List of CustomList
        """
        url = f"{self.api.url}/user/follows/list"
        resp = URLRequest.request_url(
            url, "GET", params=kwargs, headers=self.auth.get_bearer_token(), timeout=self.api.timeout
        )
        return CustomList.create_customlist_list(resp)

    def check_followed_customlist(self, list_id) -> dict:
        """ Check if logged user follows a CustomList

        Args:
            list_id (str): Required. The list id

        Returns:
            dict
        """
        url = f"{self.api.url}/user/follows/group/{list_id}"
        resp = URLRequest.request_url(
            url, "GET", timeout=self.api.timeout, headers=self.auth.get_bearer_token()
        )
        return resp # This outputs ok as response

class MangaList(Manga):
    """Class for getting user's Manga List"""

    def __init__(self, auth=Auth):
        super().__init__(auth=auth)

    def get_my_mangalist(self, **kwargs) -> List["Manga"]:
        """Get the user's MangaList

        Args:
            limit (int): The limit of custom lists to return
            offset (int): The amount of offset
            includes[] (list[str]): List of included entries. Values: manga, cover_art, author

        Returns:
            List[Manga]: List of Manga in user's list
        """
        url = f"{self.api.url}/user/follows/manga"
        resp = URLRequest.request_url(
            url,
            "GET",
            timeout=self.api.timeout,
            params=kwargs,
            headers=self.auth.get_bearer_token(),
        )
        return self.create_manga_list(resp)

    def check_followed_mangalist(self, manga_id: str) -> dict:
        """Checks if logged user follows mangalist

        Args:
            manga_id (str): Required. The manga id

        Returns:
            dict: 
        """
        url = f"{self.api.url}/user/follows/manga/{manga_id}"
        resp = URLRequest.request_url(
            url,
            "GET",
            timeout=self.api.timeout,
            headers=self.auth.get_bearer_token(),
        )
        return resp


class CustomList:
    """Class for getting users' custom lists"""

    def __init__(self, auth: Union[Auth, None] = None):
        self.auth = auth
        self.api = Api()
        self.list_id: str = ""
        self.name: str = ""
        self.visibility: str = ""
        self.owner: str = ""
        self.mangas: List[str] = []

    @classmethod
    def list_from_dict(cls, data: dict) -> Self:
        """
        Creates a CustomList from a JSON
        """
        if data["type"] != "custom_list" or not data:
            raise ValueError(data, "The data provided is not a CustomList")

        custom_list = cls()

        attributes = data["attributes"]
        relationships = data["relationships"]

        custom_list.list_id = data["id"]
        custom_list.name = attributes["name"]
        custom_list.visibility = attributes["visibility"]
        for elem in relationships:
            if elem["type"] == "user":
                custom_list.owner = elem["id"]
            elif elem["type"] == "manga":
                custom_list.mangas.append(elem["id"])

        return custom_list

    @staticmethod
    def create_customlist_list(resp) -> List["CustomList"]:
        """
        Creates a list of CustomList from a JSON
        """
        resp = resp["data"]
        custom_lists = []
        for elem in resp:
            custom_lists.append(CustomList.list_from_dict(elem))
        return custom_lists

    def __repr__(self) -> str:
        return f"CustomList(id = {self.list_id}, name = {self.name},\
                visibility = {self.visibility}, owner = {self.owner}, Manga = List[Manga])"

    def get_my_customlists(self, **kwargs) -> List["CustomList"]:
        """
        Get my custom lists

        Args:
            limit (int): The limit of custom lists to return
            offset (int): The amount of offset

        Returns:
            List[CustomList]
        """
        url = f"{self.api.url}/user/list"
        resp = URLRequest.request_url(
            url,
            "GET",
            params=kwargs,
            headers=self.auth.get_bearer_token(),
            timeout=self.api.timeout,
        )
        return self.create_customlist_list(resp)

    def get_user_customlists(self, user_id: str, **kwargs) -> List["CustomList"]:
        """
        Get a user's custom list. This will list only public custom lists

        Args:
            user_id (str): the User id
            limit (int): The limit of custom lists to return
            offset (int): The amount of offset

        Returns:
            List[CustomList]
        """
        url = f"{self.api.url}/user/{user_id}/list"
        resp = URLRequest.request_url(
            url,
            "GET",
            params=kwargs,
            headers=self.auth.get_bearer_token(),
            timeout=self.api.timeout,
        )
        return self.create_customlist_list(resp)

    def add_manga_to_customlist(self, manga_id: str, list_id: str) -> None:
        """
        Adds a manga to a custom list

        Args:
            manga_id (str): The manga id.
            list_id (str): The list id.
        """
        url = f"{self.api.url}/{manga_id}/list{list_id}"
        URLRequest.request_url(
            url, "POST", headers=self.auth.get_bearer_token(), timeout=self.api.timeout
        )

    def remove_manga_from_customlist(self, manga_id: str, list_id: str) -> None:
        """
        Removes a manga from a custom list

        Args:
            manga_id (str): The manga id
            list_id (str): The list id
        """
        url = f"{self.api.url}/manga/{manga_id}/list/{list_id}"
        URLRequest.request_url(
            url,
            "DELETE",
            headers=self.auth.get_bearer_token(),
            timeout=self.api.timeout,
        )

    def create_customlist(
        self,
        name: str,
        visibility: str = "public",
        manga: Union[List[str], None] = None,
        version: int = 1,
    ) -> None:
        """
        Creates a custom list

        Args:
            name (str): The custom list name
            visibility (str): The visibility of the custom list
            manga (List[str]): List of manga ids
        """
        url = f"{self.api.url}/list"
        params = {
            "name": name,
            "version": version,
            "visibility": visibility,
            "manga[]": manga,
        }
        URLRequest.request_url(url, "POST", params=params, timeout=self.api.timeout)

    def get_customlist(self, customlist_id: str, **kwargs) -> "CustomList":
        """
        Get a custom list by its id

        Parameters
        ------------
            customlist_id (str): The id of the custom list
            limit (int):
            offset (int):
            translatedLanguage (List[str]): 
            createdAtSince (str): Datetime String with the following format YYYY-MM-DDTHH:MM:SS
            updatedAtSince (str): Datetime String with the following format YYYY-MM-DDTHH:MM:SS
            publishAtSince (str): Datetime String with the following format YYYY-MM-DDTHH:MM:SS
        
        Returns:
            CustomList
        """
        url = f"{self.api.url}/list/{customlist_id}"
        resp = URLRequest.request_url(
            url, "GET", timeout=self.api.timeout, params=kwargs
        )
        return CustomList.list_from_dict(resp["data"])

    def update_customlist(self, customlist_id: str, **kwargs) -> "CustomList":
        """
        Update a custom list

        Args:
            customlist_id (str): The custom list id
            name (str): The custom list name
            visibility (str): Values : `"public"` `"private"`

        Returns:
            CustomList
        """
        url = f"{self.api.url}/list/{customlist_id}"
        resp = URLRequest.request_url(
            url,
            "PUT",
            params=kwargs,
            headers=self.auth.get_bearer_token(),
            timeout=self.api.timeout,
        )
        return CustomList.list_from_dict(resp["data"])

    def delete_customlist(self, customlist_id: str) -> None:
        """
        Deletes a Custom List

        Args:
            customlist_id (str): The custom list id
        """
        url = f"{self.api.url}/list{customlist_id}"
        URLRequest.request_url(
            url,
            "DELETE",
            headers=self.auth.get_bearer_token(),
            timeout=self.api.timeout,
        )
