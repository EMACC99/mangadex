import datetime

from dateutil.parser import parse
from future.utils import raise_with_traceback

from typing import Dict, List

from mangadex import (MangaError, TagError, ChapterError, AuthorError, ScanlationGroupError, UserError, CustomListError)

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

    def _MangaFromDict(self, data : dict):
        if data["data"]["type"] != 'manga' or not data:
            raise MangaError("The data provides is not a Manga")
        
        attributes = data["data"]["attributes"]

        self.id = data["data"]["id"]
        self.title = attributes["title"]
        self.altTitles = attributes["altTitles"]
        self.description = attributes["description"]
        self.isLocked = attributes["isLocked"]
        self.links = attributes["links"]
        self.originalLanguage = attributes["originalLanguage"]
        self.lastVolume = attributes["lastVolume"]
        self.lastChapter = attributes["lastChapter"]
        self.publicationDemographic = attributes["publicationDemographic"]
        self.status = attributes["status"]
        self.year = attributes["year"]
        self.contentRating = attributes["contentRating"]
        self.tags = attributes["tags"]
        self.createdAt = parse(attributes["createdAt"])
        self.updatedAt = parse(attributes["updatedAt"])

    def __repr__(self) -> str:
        temp1 = f"Manga(id = {self.id}, title = {self.title}, altTitles = {self.altTitles}, description = {self.description}, isLocked = {self.isLocked}, links = {self.links}, originalLanguage = {self.originalLanguage} \n"
        temp2 = f"lastVolume = {self.lastVolume}, lastChapter = {self.lastChapter}, publicationDemographic = {self.publicationDemographic}, status = {self.status}, year = {self.year}, contentRating = {self.contentRating} \n"
        temp3 = f"createdAt = {self.createdAt}, uploadedAt = {self.updatedAt})"
        return temp1 + temp2 + temp3

class Tag():
    def __init__(self) -> None:
        self.id : str= ""
        self.name : Dict[str, str] = {}

    def _TagFromDict(self, data : dict):
        if data["data"]["type"] != 'tag' or not data:
            raise TagError("The data provided is not a Tag")
        
        attributes = data["data"]["attributes"]

        self.id = data["data"]["id"]
        self.name = attributes["name"]

    def __repr__(self) -> str:
        return f"Tag(id = {self.id}, name = {self.name})"
class Chapter():
    def __init__(self) -> None:
        self.id : str = ""
        self.title : str = ""
        self.volume : str = ""
        self.chapter : str = ""
        self.Mangaid : str = ""
        self.sacanlation_group_id : str = ""
        self.translatedLanguage : str= ""
        self.hash : str = ""
        self.data : List[str] = []
        self.uploader : str = ""
        self.createdAt : datetime = ""
        self.updatedAt : datetime = ""
        self.publishAt : datetime = ""
    
    def _ChapterFromDict(self, data):
        if data["data"]["type"] != 'chapter' or not data:
            raise ChapterError("The data probvided is not a Tag")

        attributes = data["data"]["attributes"]

        self.id = data["data"]["id"]
        self.title = attributes["title"]
        self.volume = attributes["volume"]
        self.chapter = attributes["chapter"]
        self.translatedLanguage = attributes["translatedLanguage"]
        self.hash = attributes["hash"]
        self.data = attributes["data"]
        self.publishAt = parse(attributes["publishAt"])
        self.createdAt = parse(attributes["createdAt"])
        self.updatedAt = parse(attributes["updatedAt"])
        self.sacanlation_group_id = data["relationships"][0]["id"]
        self.Mangaid = data["relationships"][1]["id"]
        self.uploader = data["relationships"][2]["id"]
    
    def __repr__(self) -> str:
        temp1 =  f"Chapter(id = {self.id}, title = {self.title}, volume = {self.volume}, chapter = {self.chapter}, translatedLanguage = {self.translatedLanguage}, hash = {self.hash} \n"
        temp2 = f"data = {self.data}, publishAt = {self.publishAt}, createdAt = {self.createdAt}, uploadedAt = {self.updatedAt}, sacanlation_group_id = {self.sacanlation_group_id}, Mangaid = {self.Mangaid}, uploader = {self.uploader})"
        return temp1 + temp2

class User():
    def __init__(self) -> None:
        self.id : str = ""
        self.username :str = ""

    def _UserFromDict(self, data):
        if data["data"]["type"] != "user" or not data:
            raise UserError("The data provided is not an author")
        
        attributes = data["data"]["attributes"]

        self.id = data["data"]["id"]
        self.username = attributes["username"]

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
    
    def _AuthorFromDict(self, data):
        if data["data"]["type"] != "author" or not data:
            raise AuthorError("The data provided is not an author")
    
        attributes = data["data"]["attributes"]

        self.id = data["data"]["id"]
        self.name = attributes["name"]
        self.imageUrl = attributes["imageUrl"]
        self.bio = attributes["biography"]
        self.createdAt = parse(attributes["createdAt"])
        self.updatedAt = parse(attributes["updatedAt"])
    
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

        self.id = data["data"]["id"]
        self.name = attributes["name"]

        leader = User()
        leader.id = attributes["leader"]["id"]
        leader.username = attributes["leader"]["attributes"]["username"] #didn't use the _UserFromDict method becasue the api response is different
        self.leader =  leader

        self.createdAt = parse(attributes["createdAt"])
        self.updatedAt = parse(attributes["updatedAt"])
    
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
    
    def __repr__(self) -> str:
        return f"CustomList(id = {self.id}, name = {self.name}, visibility = {self.visibility}, owner = {self.owner}, Manga = List[Manga])"
