"""
Module for the Manga, Cover, Chapter, etc. Models
"""
import datetime
from typing import Dict, List, Union
from typing_extensions import Self
from dateutil.parser import parse
from mangadex import (
    MangaError,
    TagError,
    ChapterError,
    AuthorError,
    ScanlationGroupError,
    UserError,
    CustomListError,
    CoverArtError,
    URLRequest,
)


MANGADEX_BASEURL = "https://mangadex.org/"


class Manga:
    """
    Manga Object
    """

    def __init__(self) -> None:

        self.manga_id: str = ""
        self.title: Dict[str, str] = {}
        self.altTitles: Dict[str, str] = {}
        self.description: Dict[str, str] = {}
        self.isLocked: bool = False
        self.links: Dict[str, str] = {}
        self.originalLanguage: str = ""
        self.lastVolume: str = ""
        self.lastChapter: str = ""
        self.publicationDemographic: str = ""
        self.status: str = ""
        self.year: int = 0
        self.contentRating: str = ""
        self.tags: List[Tag] = []
        self.version = 1
        self.createdAt: datetime.datetime
        self.updatedAt: datetime.datetime
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
            raise MangaError(data=data, message="The data provided is not a Manga")

        attributes = data["attributes"]

        manga = cls()

        manga.manga_id = data["id"]
        manga.title = attributes["title"]
        manga.altTitles = attributes["altTitles"]
        manga.description = attributes["description"]
        try:
            manga.isLocked = attributes["isLocked"]
        except KeyError:
            pass

        manga.links = attributes["links"]
        manga.originalLanguage = attributes["originalLanguage"]
        manga.lastVolume = attributes["lastVolume"]
        manga.lastChapter = attributes["lastChapter"]
        manga.publicationDemographic = attributes["publicationDemographic"]
        manga.status = attributes["status"]
        manga.year = attributes["year"]
        manga.contentRating = attributes["contentRating"]
        manga.tags = Tag.create_tag_list(attributes["tags"])
        manga.createdAt = parse(attributes["createdAt"])
        manga.updatedAt = parse(attributes["updatedAt"])

        for elem in data["relationships"]:
            if elem["type"] == "author":
                manga.author_id.append(elem["id"])
            elif elem["type"] == "artist":
                manga.artist_id.append(elem["id"])
            elif elem["type"] == "cover_art":
                manga.cover_id = elem["id"]

        return manga

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
        return f"{MANGADEX_BASEURL}/title/{self.manga_id}"

    def __eq__(self, other: Self) -> bool:
        my_vals = [self.manga_id, self.title, self.createdAt, self.author_id]
        other_vals = [other.manga_id, other.title, other.createdAt, other.author_id]
        return my_vals == other_vals

    def __ne__(self, other: Self) -> bool:
        return not self.__eq__(other)

    def __repr__(self) -> str:
        temp1 = f"Manga(manga_id = {self.manga_id}, title = {self.title}, \
                altTitles = {self.altTitles}, description = {self.description}, \
                isLocked = {self.isLocked}, links = {self.links}, \
                originalLanguage = {self.originalLanguage} \n"
        temp2 = f"lastVolume = {self.lastVolume}, lastChapter = {self.lastChapter}, \
                publicationDemographic = {self.publicationDemographic}, status = {self.status}, \
                year = {self.year}, contentRating = {self.contentRating} \n"
        temp3 = f"createdAt = {self.createdAt}, uploadedAt = {self.updatedAt}), \
                author_id = {self.author_id}, artist_id = {self.artist_id}, \
                cover_id = {self.cover_id}"
        return f"{temp1}{temp2}{temp3}"


class Tag:
    """
    Class for Manga Tags
    """

    def __init__(self) -> None:
        self.tag_id: str = ""
        self.name: Dict[str, str] = {}
        self.description: str = ""
        self.group: str = ""

    @classmethod
    def tag_from_dict(cls, data: dict) -> Self:
        """
        Creates a Tag Object from a JSON
        """
        tag = cls()
        try:
            data = data["data"]
        except KeyError:
            pass

        if data["type"] != "tag" or not data:
            raise TagError(data=data, message="The data provided is not a Tag")

        attributes = data["attributes"]

        tag.tag_id = data["id"]
        tag.name = attributes["name"]
        tag.description = attributes["description"]
        tag.group = attributes["group"]

        return tag

    @staticmethod
    def create_tag_list(resp) -> List["Tag"]:
        """
        Creates a Tag list from a JSON
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


class Chapter:
    """
    Chapter Object
    """

    def __init__(self) -> None:
        self.chapter_id: str = ""
        self.title: str = ""
        self.volume: str = ""
        self.chapter: Union[float, None] = None
        self.manga_id: str = ""
        self.group_id: str = ""
        self.translatedLanguage: str = ""
        self.hash: str = ""
        self.data: List[str] = []
        self.uploader: str = ""
        self.createdAt: datetime.datetime
        self.updatedAt: datetime.datetime
        self.publishAt: datetime.datetime

    @classmethod
    def chapter_from_dict(cls, data) -> Self:
        """
        Creates a Chapter from JSON
        """
        chapter = cls()
        try:
            data = data["data"]
        except KeyError:
            pass

        if data["type"] != "chapter" or not data:
            raise ChapterError(data=data, message="The data provided is not a Chapter")

        attributes = data["attributes"]

        chapter.chapter_id = data["id"]
        chapter.title = attributes["title"]
        chapter.volume = attributes["volume"]
        chapter.chapter = (
            float(attributes["chapter"]) if attributes["chapter"] is not None else None
        )
        chapter.translatedLanguage = attributes["translatedLanguage"]
        # chapter.hash = attributes["hash"]
        # chapter.data = attributes["data"]
        chapter.publishAt = parse(attributes["publishAt"])
        chapter.createdAt = parse(attributes["createdAt"])
        chapter.updatedAt = parse(attributes["updatedAt"])
        chapter.group_id = data["relationships"][0]["id"]
        chapter.manga_id = data["relationships"][1]["id"]
        try:
            chapter.uploader = data["relationships"][2]["id"]
        except IndexError:
            pass

        return chapter

    def fetch_chapter_images(self) -> List[str]:  # maybe make this an async function?
        """
        Get the image links for the chapter

        Returns
        -----------
        `List[str]`. A list with the links with the chapter images

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
        for filename in self.data:
            image_urls.append(f"{image_server_url}/{self.hash}/{filename}")

        return image_urls

    @staticmethod
    def create_chapter_list(resp) -> List["Chapter"]:
        """
        Creates a Chapter list from JSON
        """
        resp = resp["data"]
        chap_list = []
        for elem in resp:
            chap_list.append(Chapter.chapter_from_dict(elem))
        return chap_list

    @property
    def url(self):
        """
        Returns the mangadex url
        """
        return f"{MANGADEX_BASEURL}/chapter/{self.chapter_id}"

    def __eq__(self, other: Self) -> bool:
        my_vals = [self.chapter_id, self.manga_id, self.chapter]
        other_vals = [other.chapter_id, other.manga_id, other.chapter]
        return my_vals == other_vals

    def __ne__(self, other: Self) -> bool:
        return not self.__eq__(other)

    def __repr__(self) -> str:
        temp1 = f"Chapter(chapter_id = {self.chapter_id}, title = {self.title}, \
                volume = {self.volume}, chapter = {self.chapter}, \
                translatedLanguage = {self.translatedLanguage}, hash = {self.hash} \n"
        temp2 = f"data = List[filenames], publishAt = {self.publishAt}, \
                createdAt = {self.createdAt}, uploadedAt = {self.updatedAt}, \
                group_id = {self.group_id}, manga_id = {self.manga_id}, uploader = {self.uploader})"
        return f"{temp1}{temp2}"


class User:
    """
    User representation
    """

    def __init__(self) -> None:
        self.user_id: str = ""
        self.username: str = ""

    @classmethod
    def user_from_dict(cls, data: dict) -> Self:
        """
        Creates a User from a JSON
        """
        if "data" in data:
            data = data["data"]

        if data["type"] != "user" or not data:
            raise UserError(data=data, message="The data provided is not a User")

        attributes = data["attributes"]

        user = cls()
        user.user_id = data["id"]
        user.username = attributes["username"]

        return user

    @staticmethod
    def create_user_list(resp: dict) -> List["User"]:
        """
        Creates a List of users from a JSON
        """
        resp = resp["data"]
        user_list = []
        for elem in resp:
            user_list.append(User.user_from_dict(elem))
        return user_list

    @property
    def url(self):
        """
        Returns mangadex url
        """
        return f"{MANGADEX_BASEURL}/user/{self.user_id}"

    def __eq__(self, other: Self) -> bool:
        my_vals = [self.user_id, self.username]
        other_vals = [other.user_id, other.username]
        return my_vals == other_vals

    def __ne__(self, other: "User") -> bool:
        return not self.__eq__(other)

    def __repr__(self) -> str:
        return f"User(id = {self.user_id}, username = {self.username})"


class Author:
    """
    Author Object
    """

    def __init__(self) -> None:
        self.author_id: str = ""
        self.name: str = ""
        self.imageUrl: str = ""
        self.bio: Dict[str, str] = {}
        self.createdAt: datetime.datetime
        self.updatedAt: datetime.datetime
        self.mangas: List[str] = []

    @classmethod
    def author_from_dict(cls, data: dict):
        """
        Creates Author from JSON
        """
        try:
            data = data["data"]
        except KeyError:
            pass

        if data["type"] != "author" or not data:
            raise AuthorError(
                data=data,
                message=f"The data provided is not Author is : {data['type']}",
            )

        author = cls()

        attributes = data["attributes"]

        author.author_id = data["id"]
        author.name = attributes["name"]
        author.imageUrl = attributes["imageUrl"]
        author.bio = attributes["biography"]
        author.createdAt = parse(attributes["createdAt"])
        author.updatedAt = parse(attributes["updatedAt"])
        author.mangas = [
            manga["id"] for manga in data["relationships"] if manga["type"] == "manga"
        ]  # better keep it like this to not consume computing time

        return author

    @staticmethod
    def create_authors_list(resp: dict) -> List["Author"]:
        """
        Create a list of Authors from JSON
        """
        resp = resp["data"]
        authors_list = []
        for elem in resp:
            authors_list.append(Author.author_from_dict(elem))
        return authors_list

    @property
    def url(self):
        """
        Returns the mangadex url
        """
        return f"{MANGADEX_BASEURL}/author/{self.author_id}"

    def __eq__(self, other: Self) -> bool:
        my_vals = [self.author_id, self.name]
        other_vals = [other.author_id, other.name]
        return all((me == other for me, other in zip(my_vals, other_vals)))

    def __ne__(self, other: Self) -> bool:
        return not self.__eq__(other)

    def __repr__(self) -> str:
        return f"Author(id = {self.author_id}, name = {self.name}, imageUrl = {self.imageUrl}, createdAt = {self.createdAt}, updatedAt = {self.updatedAt})"


class ScanlationGroup:
    def __init__(self) -> None:
        self.group_id: str = ""
        self.name: str = ""
        self.leader: Union[User, None] = None
        self.createdAt: datetime.datetime
        self.updatedAt: datetime.datetime

    @classmethod
    def scanlation_from_dict(cls, data) -> Self:
        """
        Creates a ScanlationGroup from JSON
        """
        if data["type"] != "scanlation_group" or not data:
            raise ScanlationGroupError(
                data, "The data provided is not an scanlation group"
            )

        scan_group = cls()

        attributes = data["attributes"]
        relationships = data["relationships"]
        scan_group.group_id = data["id"]
        scan_group.name = attributes["name"]

        leader = User()
        for elem in relationships:
            try:
                if elem["type"] == "leader":
                    leader.user_id = elem["id"]
                    break
            except KeyError:
                continue

        scan_group.leader = leader

        scan_group.createdAt = parse(attributes["createdAt"])
        scan_group.updatedAt = parse(attributes["updatedAt"])

        return scan_group

    @staticmethod
    def create_group_list(resp) -> List["ScanlationGroup"]:
        """
        Creates a ScanlationGroup List from JSON
        """
        resp = resp["data"]
        group_list = []
        for elem in resp:
            group_list.append(ScanlationGroup.scanlation_from_dict(elem))
        return group_list

    @property
    def url(self):
        """
        Returns the mangadex url
        """
        return f"{MANGADEX_BASEURL}/group/{self.group_id}"

    def __eq__(self, other: Self) -> bool:
        my_vals = [self.group_id, self.name]
        other_vals = [other.group_id, other.name]
        return my_vals == other_vals

    def __ne__(self, other: Self) -> bool:
        return not self.__eq__(other)

    def __repr__(self) -> str:
        return f"ScanlationGroup(id = {self.group_id}, name = {self.name}, leader = {self.leader}, createdAt = {self.createdAt}, updatedAt = {self.updatedAt})"


class CustomList:
    """
    Manga Custom List Object
    """

    def __init__(self) -> None:
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
            raise CustomListError(data, "The data provided is not a Custom List")

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
        return f"CustomList(id = {self.list_id}, name = {self.name}, visibility = {self.visibility}, owner = {self.owner}, Manga = List[Manga])"


class CoverArt:
    """
    Object Containing Manga Cover Art Attributes
    """

    def __init__(self) -> None:
        self.cover_id: str = ""
        self.volume: str = ""
        self.fileName: str = ""
        self.description: str = ""
        self.createdAt: datetime.datetime
        self.updatedAt: datetime.datetime
        self.manga_id: str = ""
        self.locale: str = ""

    @classmethod
    def cover_from_dict(cls, data: dict) -> Self:
        """
        Creates a CoverArt form a JSON
        """
        try:
            data = data["data"]
        except (KeyError, TypeError):
            pass

        if data["type"] != "cover_art" or not data:
            raise CoverArtError(data, "The data provided is not a Custom List")

        cover = cls()

        attributes = data["attributes"]

        cover.cover_id = data["id"]
        cover.volume = attributes["volume"]
        cover.fileName = attributes["fileName"]
        cover.locale = attributes["locale"]
        cover.description = attributes["description"]
        cover.createdAt = parse(attributes["createdAt"])
        cover.updatedAt = parse(attributes["updatedAt"])
        cover.manga_id = data["relationships"][0]["id"]

        return cover

    def fetch_cover_image(self, quality: str = "source") -> str:
        """
        Returns the url of a cover art

        Parameters
        -------------
        quality : `str`. Values : `medium`,  `small`

        Returns
        -----------
        url : `str`. The cover url
        """
        url = f"https://uploads.mangadex.org/covers/{self.manga_id}/{self.fileName}"

        if quality == "medium":
            url = f"{url}.512.jpg"
        elif quality == "small":
            url = f"{url}.256.jpg"

        return url

    @staticmethod
    def create_coverart_list(resp) -> List["CoverArt"]:
        """
        Creates a list of CoverArts form a JSON
        """
        resp = resp["data"]
        coverimage_list = []
        for elem in resp:
            coverimage_list.append(CoverArt.cover_from_dict(elem))
        return coverimage_list

    def __repr__(self) -> str:
        return f"CoverArt(id = {self.cover_id}, mangaId = {self.manga_id}, volume = {self.volume}, \
                fileName = {self.fileName}, description = {self.description}, \
                createdAt = {self.createdAt}, updatedAt = {self.updatedAt})"
