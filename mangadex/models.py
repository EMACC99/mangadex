import datetime

from dateutil.parser import parse
from future.utils import raise_with_traceback

from mangadex import (MangaError, TagError)

class Manga():
    def __init__(self) -> None:

        self.id = ""
        self.title = ""
        self.altTitles = {}
        self.description = {}
        self.isLocked = False
        self.links = []
        self.originalLanguage = ""
        self.lastVolume = ""
        self.lastChapter = ""
        self.publicationDemographic = ""
        self.status = ""
        self.year = 0
        self.contentRating = ""
        self.tags = []
        self.version = 1
        self.createdAt = ""
        self.updatedAt = ""

    def _MangaFromDict(self, data):
        if data["data"]["type"] != 'manga' or not data:
            # print("The type is not a manga")
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


class Tag():
    def __init__(self) -> None:
        self.id = ""
        self.name = []

    def _TagFromDict(self, data):
        if data["data"]["type"] != 'tag' or not data:
            raise TagError("The data provided is not a Tag")
        
        attributes = data["data"]["attributes"]

        self.id = data["data"]["id"]
        self.name = attributes["name"]