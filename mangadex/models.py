import datetime

from dateutil.parser import parse
from future.utils import raise_with_traceback

from typing import Dict, List, Union

from mangadex import (MangaError, TagError, ChapterError, AuthorError, ScanlationGroupError, UserError, CustomListError, CoverArtError, URLRequest)

class Manga():
    def __init__(self) -> None:

        self.id : str = ""
        self.title : Dict[str, str] = {}
        self.altTitles : Dict[str, str] = {}
        self.description : Dict[str, str] = {}
        self.isLocked : bool = False
        self.links : Dict[str, str] = {}
        self.originalLanguage : str = ""
        self.lastVolume : str = ""
        self.lastChapter : str = ""
        self.publicationDemographic : str = ""
        self.status : str = ""
        self.year : int = 0
        self.contentRating : str = ""
        self.tags : List[str]  = []
        self.version = 1
        self.createdAt : datetime = ""
        self.updatedAt : datetime = ""
        self.authorId : List[str] = []
        self.artistId : List[str] = []
        self.coverId : str = ""

    def _MangaFromDict(self, data : dict):
        if data["data"]["type"] != 'manga' or not data:
            raise MangaError(data=data, message="The data probvided is not a Manga")
        
        attributes = data["data"]["attributes"]

        self.id = data["data"]["id"]
        self.title = attributes["title"]
        self.altTitles = attributes["altTitles"]
        self.description = attributes["description"]
        try:
            self.isLocked = attributes["isLocked"]
        except KeyError:
            pass
        
        self.links = attributes["links"]
        self.originalLanguage = attributes["originalLanguage"]
        self.lastVolume = attributes["lastVolume"]
        self.lastChapter = attributes["lastChapter"]
        self.publicationDemographic = attributes["publicationDemographic"]
        self.status = attributes["status"]
        self.year = attributes["year"]
        self.contentRating = attributes["contentRating"]
        self.tags = Tag._create_tag_list(attributes["tags"])
        self.createdAt = parse(attributes["createdAt"])
        self.updatedAt = parse(attributes["updatedAt"])

        for elem in data["relationships"]:
            if elem['type'] == 'author':
                self.authorId.append(elem['id'])
            elif elem['type'] == 'artist':
                self.artistId.append(elem['id'])
            elif elem['type'] == 'cover_art':
                self.coverId = elem['id']


    @staticmethod
    def _create_manga(elem) -> 'Manga':
        manga = Manga()
        manga._MangaFromDict(elem)
        return manga
    
    @staticmethod
    def _create_manga_list(resp) -> List['Manga']:
        resp = resp["results"]
        manga_list = []
        for elem in resp:
            manga_list.append(Manga._create_manga(elem))
        return manga_list

    def __eq__(self, other : 'Manga') -> bool:
        my_vals = [self.id, self.title, self.createdAt, self.authorId]
        other_vals = [other.id, other.title, other.createdAt, other.authorId]
        return all((me == other for me, other in zip(my_vals, other_vals)))
    
    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __repr__(self) -> str:
        temp1 = f"Manga(id = {self.id}, title = {self.title}, altTitles = {self.altTitles}, description = {self.description}, isLocked = {self.isLocked}, links = {self.links}, originalLanguage = {self.originalLanguage} \n"
        temp2 = f"lastVolume = {self.lastVolume}, lastChapter = {self.lastChapter}, publicationDemographic = {self.publicationDemographic}, status = {self.status}, year = {self.year}, contentRating = {self.contentRating} \n"
        temp3 = f"createdAt = {self.createdAt}, uploadedAt = {self.updatedAt}), authorId = {self.authorId}, artistId = {self.artistId}, coverId = {self.coverId}"
        return temp1 + temp2 + temp3

class Tag():
    def __init__(self) -> None:
        self.id : str= ""
        self.name : Dict[str, str] = {}
        self.description : str = ""
        self.group : str = ""
    def _TagFromDict(self, data : dict):
        if "data" in data:
            data = data["data"]
        
        if data["type"] != 'tag' or not data:
            raise TagError(data=data, message="The data provided is not a Tag")
        
        attributes = data["attributes"]

        self.id = data["id"]
        self.name = attributes["name"]
        self.description = attributes["description"]
        self.group = attributes["group"]

    @staticmethod
    def _create_tag(elem) -> 'Tag':
        tag = Tag()
        tag._TagFromDict(elem)
        return tag

    @staticmethod
    def _create_tag_list(resp) -> List['Tag']:
        tag_list = []
        for tag in resp:
            tag_list.append(Tag._create_tag(tag))
        return tag_list

    def __eq__(self, other : 'Tag') -> bool:
        my_vals = [self.id, self.name]
        other_vals = [other.id, other.name]
        return all((me == other for me,other in zip(my_vals, other_vals)))

    def __ne__(self, other: 'Tag') -> bool:
        return not self.__eq__(other)

    def __repr__(self) -> str:
        return f"Tag(id = {self.id}, name = {self.name})"

class Chapter():
    def __init__(self) -> None:
        self.id : str = ""
        self.title : str = ""
        self.volume : str = ""
        self.chapter : float = None
        self.Mangaid : str = ""
        self.scanlation_group_id : str = ""
        self.translatedLanguage : str= ""
        self.hash : str = ""
        self.data : List[str] = []
        self.uploader : str = ""
        self.createdAt : datetime = ""
        self.updatedAt : datetime = ""
        self.publishAt : datetime = ""
    
    def _ChapterFromDict(self, data):

        if data["data"]["type"] != 'chapter' or not data:
            raise ChapterError(data = data, mmessage="The data provided is not a Chapter")

        attributes = data["data"]["attributes"]

        self.id = data["data"]["id"]
        self.title = attributes["title"]
        self.volume = attributes["volume"]
        self.chapter = float(attributes["chapter"]) if attributes['chapter'] is not None else None
        self.translatedLanguage = attributes["translatedLanguage"]
        self.hash = attributes["hash"]
        self.data = attributes["data"]
        self.publishAt = parse(attributes["publishAt"])
        self.createdAt = parse(attributes["createdAt"])
        self.updatedAt = parse(attributes["updatedAt"])
        self.scanlation_group_id = data["relationships"][0]["id"]
        self.Mangaid = data["relationships"][1]["id"]
        self.uploader = data["relationships"][2]["id"]

    def fetch_chapter_images(self) -> List[str]: #maybe make this an async function?
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
        url = f"https://api.mangadex.org/at-home/server/{self.id}"
        image_server_url = URLRequest._request_url(url, "GET", timeout=5)
        image_server_url = image_server_url["baseUrl"].replace("\\", "")
        image_server_url = f"{image_server_url}/data"
        image_urls = []
        for filename in self.data:
            image_urls.append(f"{image_server_url}/{self.hash}/{filename}")

        return image_urls

    @staticmethod
    def _create_chapter(elem) -> 'Chapter':
        chap = Chapter()
        chap._ChapterFromDict(elem)
        return chap
    
    @staticmethod
    def _create_chapter_list(resp) -> List['Chapter']:
        resp = resp["results"]
        chap_list = []
        for elem in resp:
            chap_list.append(Chapter._create_chapter(elem))
        return chap_list

    def __eq__(self, other: 'Chapter') -> bool:
        my_vals = [self.id, self.hash, self.Mangaid, self.chapter]
        other_vals = [other.id, other.hash, other.Mangaid, other.chapter]
        return all((me == other for me,other in zip(my_vals, other_vals)))

    def __ne__(self, other: 'Chapter') -> bool:
        return not self.__eq__(other)
    
    def __repr__(self) -> str:
        temp1 =  f"Chapter(id = {self.id}, title = {self.title}, volume = {self.volume}, chapter = {self.chapter}, translatedLanguage = {self.translatedLanguage}, hash = {self.hash} \n"
        temp2 = f"data = List[filenames], publishAt = {self.publishAt}, createdAt = {self.createdAt}, uploadedAt = {self.updatedAt}, scanlation_group_id = {self.scanlation_group_id}, Mangaid = {self.Mangaid}, uploader = {self.uploader})"
        return temp1 + temp2

class User():
    def __init__(self) -> None:
        self.id : str = ""
        self.username :str = ""

    def _UserFromDict(self, data):
        if "data" in data:
            data = data["data"]

        if data["type"] != "user" or not data:
            raise UserError(data = data, message="The data provided is not a User")
        
        attributes = data["attributes"]

        self.id = data["id"]
        self.username = attributes["username"]

    @staticmethod
    def _create_user(elem) -> 'User':
        user = User()
        user._UserFromDict(elem)
        return user

    @staticmethod    
    def _create_user_list(resp) -> List['User']:
        resp = resp["results"]
        user_list = []
        for elem in resp:
            user_list.append(User._create_user(elem))
        return user_list

    def __eq__(self, other: 'User') -> bool:
        my_vals = [self.id, self.username]
        other_vals = [other.id, other.username]
        return all((me == other for me,other in zip(my_vals, other_vals)))

    def __ne__(self, other: 'User') -> bool:
        return not self.__eq__(other)

    def __repr__(self) -> str:
        return f"User(id = {self.id}, username = {self.username})"

class Author():
    def __init__(self) -> None:
        self.id : str = ""
        self.name : str = ""
        self.imageUrl : str = ""
        self.bio : Dict[str,  str] = {}
        self.createdAt : datetime = ""
        self.updatedAt : datetime = ""
        self.mangas : List[str] = []
    
    def _AuthorFromDict(self, data):
        if data["data"]["type"] != "author" or not data:
            raise AuthorError(data = data, message= f"The data provided is not Author is : {data['data']['type']}")
    
        attributes = data["data"]["attributes"]

        self.id = data["data"]["id"]
        self.name = attributes["name"]
        self.imageUrl = attributes["imageUrl"]
        self.bio = attributes["biography"]
        self.createdAt = parse(attributes["createdAt"])
        self.updatedAt = parse(attributes["updatedAt"])
        self.mangas =  [manga["id"] for manga in data["relationships"] if manga["type"] == "manga"] # better keep it like this to not consume computing time

    @staticmethod
    def _create_author(elem) -> 'Author':
        author = Author()
        author._AuthorFromDict(elem)
        return author

    @staticmethod
    def _create_authors_list(self, resp) -> List['Author']:
        resp = resp["results"]
        authors_list = []
        for elem in resp:
            authors_list.append(Author._create_author(elem))
        return authors_list

    def __eq__(self, other: 'Author') -> bool:
        my_vals = [self.id ,self.name]
        other_vals = [other.id, other.name]
        return all((me == other for me,other in zip(my_vals, other_vals)))

    def __ne__(self, other: 'Author') -> bool:
        return not self.__eq__(other)

    def __repr__(self) -> str:
        return f"Author(id = {self.id}, name = {self.name}, imageUrl = {self.imageUrl}, createdAt = {self.createdAt}, updatedAt = {self.updatedAt})"

class ScanlationGroup():
    def __init__(self) -> None:
        self.id : str = ""
        self.name : str = ""
        self.leader : User = None
        self.createdAt : datetime = None
        self.updatedAt : datetime = None

    def _ScanlationFromDict(self, data):
        
        if data["data"]["type"] != "scanlation_group" or not data:
            raise ScanlationGroupError("The data provided is not an scanlation group")

        attributes = data["data"]["attributes"]
        relationships = data["relationships"]
        self.id = data["data"]["id"]
        self.name = attributes["name"]

        leader = User()
        for elem in relationships:
            try:
                if elem["type"] == "leader":
                    leader.id = elem["id"]
                    break
            except KeyError:
                continue

        # leader.username = attributes["leader"]["attributes"]["username"] #didn't use the _UserFromDict method becasue the api response is different
        self.leader =  leader

        self.createdAt = parse(attributes["createdAt"])
        self.updatedAt = parse(attributes["updatedAt"])
    
    @staticmethod
    def _create_group(elem) ->  'ScanlationGroup':
        group = ScanlationGroup()
        group._ScanlationFromDict(elem)
        return group

    @staticmethod
    def _create_group_list(resp)-> List['ScanlationGroup']:
        resp = resp["results"]
        group_list = []
        for elem in resp:
            group_list.append(ScanlationGroup._create_group(elem))
        return group_list  

    def __eq__(self, other: 'ScanlationGroup') -> bool:
        my_vals = []
        other_vals = []
        return all((me == other for me,other in zip(my_vals, other_vals)))
    
    def __ne__(self, other: 'ScanlationGroup') -> bool:
        return not self.__eq__(other)
        
    def __repr__(self) -> str:
        return f"ScanlationGroup(id = {self.id}, name = {self.name}, leader = {self.leader}, createdAt = {self.createdAt}, updatedAt = {self.updatedAt})"

class CustomList():
    def __init__(self) -> None:
        self.id : str = ""
        self.name : str = ""
        self.visibility : str = ""
        self.owner : User = None
        self.mangas : List[Manga] = None

    def _ListFromDict(self, data):
        if data["data"]["type"] != "custom_list" or not data:
            raise CustomListError("The data provided is not a Custom List")
        
        attributes = data["data"]["attributes"]

        self.id = data["data"]["id"]
        self.name = attributes["name"]
        self.visibility = attributes["visibility"]
        self.owner = User()
        self.owner._UserFromDict(attributes["owner"])
    
    @staticmethod
    def _create_customlist(elem) -> 'CustomList':
        custom_list = CustomList()
        custom_list._ListFromDict(elem)
        return custom_list

    @staticmethod
    def _create_customlist_list(resp) -> List['CustomList']:
        resp = resp["results"]
        custom_lists = []
        for elem in resp:
            custom_lists.append(CustomList._create_customlist(elem))
        return custom_lists

    def __repr__(self) -> str:
        return f"CustomList(id = {self.id}, name = {self.name}, visibility = {self.visibility}, owner = {self.owner}, Manga = List[Manga])"

class CoverArt():
    def __init__(self) -> None:
        self.id : str = ""
        self.volume : str = None
        self.fileName : str = ""
        self.description : str = None
        self.createdAt : datetime = None
        self.updatedAt : datetime = None
        self.mangaId : str = None

    def _CoverFromDict(self, data):
        if data["data"]["type"] != "cover_art" or not data:
            raise CoverArtError("The data provided is not a Custom List")
        
        attributes = data["data"]["attributes"]

        self.id = data["data"]["id"]
        self.volume = attributes["volume"]
        self.fileName = attributes["fileName"]
        self.description = attributes["description"]
        self.createdAt = parse(attributes["createdAt"])
        self.updatedAt = parse(attributes["updatedAt"])
        self.mangaId = data["relationships"][0]["id"]
    
    def fetch_cover_image(self, quality : str = "source") -> str:
        """
        Returns the url of a cover art

        Parametes
        -------------
        quality : `str`. Values : `medium`,  `small`

        Returns
        -----------
        url : `str`. The cover url
        """
        url = f"https://uploads.mangadex.org/covers/{self.mangaId}/{self.fileName}"
        
        if quality == "medium":
            url = f"{url}.512.jpg"
        elif quality == "small":
            url = f"{url}.256.jpg"
        
        return url

    @staticmethod
    def _createCoverImage(elem) -> 'CoverArt':
        coverImage = CoverArt()
        coverImage._CoverFromDict(elem)
        return coverImage

    @staticmethod
    def _createCoverImageList(resp) -> List['CoverArt']:
        resp = resp["results"]
        coverimage_list = []
        for elem in resp:
            coverimage_list.append(CoverArt._createCoverImage(elem))
        return coverimage_list

    def __repr__(self) -> str:
        return f"CoverArt(id = {self.id}, mangaId = {self.mangaId}, volume = {self.volume}, fileName = {self.fileName}, description = {self.description}, createdAt = {self.createdAt}, updatedAt = {self.updatedAt})"