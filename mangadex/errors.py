from requests import Response
from typing import Union, Dict, List

class ApiError(Exception):
    def __init__(self, resp : Union[Response, dict], message = "The api responded with the error") -> None:
        self.resp = resp
        if type(self.resp) == Response:
            self.code = self.resp.status_code                
        else:
            self.code = self.resp["status"]

        self.message = message
        super().__init__(self.message)
    
    def __str__(self) -> str:
        return f"{self.message}: {self.code}"

class ApiClientError(Exception):
    pass

class MangaError(Exception):
    pass

class TagError(Exception):
    pass

class ChapterError(Exception):
    pass

class AuthorError(Exception):
    pass

class ScanlationGroupError(Exception):
    pass

class UserError(Exception):
    pass

class CustomListError(Exception):
    pass

class CoverArtError(Exception):
    pass