from __future__ import absolute_import

import datetime
from typing_extensions import Dict, List, Union, Any

from dateutil.parser import parse
from typing_extensions import Self

from mangadex.url_models import URLRequest
from .auth import Api, Auth


class Author:
    def __init__(self, auth=Union[Auth, None]) -> None:
        self.auth = auth
        self.api = Api()

        self.author_id: str = ""
        self.name: str = ""
        self.imageUrl: str = ""
        self.bio: Dict[str, str] = {}
        self.createdAt: datetime.datetime
        self.updatedAt: datetime.datetime
        self.mangas: List[str] = []

    @classmethod
    def author_from_dict(cls, resp: dict) -> Self:
        """Creates author from JSON

        Args:
            resp (dict): Raw data from JSON

        Raises:
            ValueError: Returned when the JSON doesn't contain Author Information

        Returns:
            Author: Author Information
        """
        try:
            resp = resp["data"]
        except KeyError:
            pass

        if resp["type"] != "author" or not resp:
            raise ValueError(f"The data provided is not Author is : {resp['type']}")

        author = cls()

        attributes = resp["attributes"]

        author.author_id = resp["id"]
        author.name = attributes["name"]
        author.imageUrl = attributes["imageUrl"]
        author.bio = attributes["biography"]
        author.createdAt = parse(attributes["createdAt"])
        author.updatedAt = parse(attributes["updatedAt"])
        author.mangas = [
            series["id"]
            for series in resp["relationships"]
            if series["type"] == "series"
        ]  # better keep it like this to not consume computing time

        return author

    @staticmethod
    def create_authors_list(resp: dict) -> List["Author"]:
        """Create a list of Authors from JSON

        :param resp: dict: Response from author list
        :param resp: dict:
        :returns: List[Author]: List of author

        """
        resp = resp["data"]
        authors_list = []
        for elem in resp:
            authors_list.append(Author.author_from_dict(elem))
        return authors_list

    @property
    def url(self):
        """Returns the mangadex url"""
        return f"{self.api.url}/author/{self.author_id}"

    def __eq__(self, other: Self) -> bool:
        my_vals = [self.author_id, self.name]
        other_vals = [other.author_id, other.name]
        return all((me == other for me, other in zip(my_vals, other_vals)))

    def __ne__(self, other: Self) -> bool:
        return not self.__eq__(other)

    def __repr__(self) -> str:
        return (
            f"Author(id = {self.author_id}, name = {self.name}, imageUrl = {self.imageUrl},"
            f"createdAt = {self.createdAt}, updatedAt = {self.updatedAt})"
        )

    def list_author(self, **kwargs) -> List["Author"]:
        """ Get the list of authors

        Args:
            limit: Number of authors to load
            offset:
            ids[]: Array of ids
            name: Name of author(for search)

        Returns:
            List[Author]: List of Authors
        """
        if "ids" in kwargs:
            kwargs["ids[]"] = kwargs.pop("ids")

        url = f"{self.api.url}/author"
        resp = URLRequest.request_url(
            url, "GET", timeout=self.api.timeout, params=kwargs
        )
        return list(Author.author_from_dict(author) for author in resp["data"])

    def get_author_by_id(self, author_id: str) -> "Author":
        """Gets an author by its id

        :param author_id: str`: The id of the author
        :param author_id: str:
        :returns: Author`

        """
        url = f"{self.api.url}/author/{author_id}"
        resp = URLRequest.request_url(url, "GET", timeout=self.api.timeout)
        return Author.author_from_dict(resp)

    def create_author(
            self, name: str, version: int, ObjReturn: bool = False
    ) -> Union["Author", None]:
        """Creates an Author

        :param name: type name: `str`. The author name
        :param version: type version: `int`. The version of the author
        :param ObjReturn: bool` Default `False`. If set to `True`, it will return the info
        :param name: str:
        :param version: int:
        :param ObjReturn: bool:  (Default value = False)
        :returns: Union[Author, None]`

        """
        url = f"{self.api.url}/author"
        params = {"name": name, "version": version}
        resp = URLRequest.request_url(
            url,
            "POST",
            timeout=self.api.timeout,
            params=params,
            headers=self.auth.get_bearer_token(),
        )
        if ObjReturn:
            return Author.author_from_dict(resp)

    def update_author(
            self,
            *,
            author_id: str,
            version: int,
            name: Union[str, None] = None,
            ObjReturn: bool = False,
    ) -> Union["Author", None]:
        """ Updates and Author

        Args:
            author_id: The author id
            version: The version of author info
            name: The name of the author
            ObjReturn: Default `False`. If set to `True`, it will return the info

        Returns:
            Union[Author, None]:  Updated Chapter
        """
        url = f"{self.api.url}/author/{author_id}"
        params: Dict[str, Any] = {"version": version}
        if name is not None:
            params["name"] = name
        resp = URLRequest.request_url(
            url, "PUT", timeout=self.api.timeout, params=params, headers=self.auth.get_bearer_token()
        )

        if ObjReturn:
            return Author.author_from_dict(resp) if ObjReturn else None

    def delete_author(self, author_id: str) -> None:
        """Deletes an author

        :param author_id: str: Author ID
        :param author_id: str:

        """
        url = f"{self.api.url}/author/{author_id}"
        URLRequest.request_url(
            url, "DELETE", headers=self.auth.get_bearer_token(), timeout=self.api.timeout
        )


class ScanlationGroup:
    def __init__(self, auth=Union[Auth, None]) -> None:
        self.auth = auth
        self.api = Api()

        self.group_id: str = ""
        self.name: List[str] = []
        self.leader = None
        self.website: str = ""
        self.discord: str = ""
        self.twitter: str = ""
        self.mangaUpdates: str = ""
        self.email: str = ""
        self.bio: str = ""
        self.focusedLanguage: str = ""
        self.official: bool = False
        self.ex_licensed: bool = False
        self.verified: bool = False
        self.inactive: bool = False
        self.publish_delay: bool = False
        self.relationships: List[Dict[str, Any]] = []

    @classmethod
    def group_from_dict(cls, resp: dict) -> Self:
        """Creates Author from JSON

        :param resp: dict: Raw data from JSON
        :param resp: dict:
        :returns: Author` Author information

        """
        try:
            resp = resp["data"]
        except KeyError:
            pass

        if resp["type"] != "scanlation_group" or not resp:
            raise ValueError(f"The data provided is not Author is : {resp['type']}",
                            )

        group = cls()

        attributes = resp["attributes"]
        group.group_id = resp["id"]
        group.name = [attributes["name"]]
        if 'altNames' in attributes:
            group.name.append([altName["name"]
                                for altName in attributes['altNames']
                                ])
        group.website = attributes["website"]
        group.discord = attributes["discord"]
        group.twitter = attributes["twitter"]
        group.mangaUpdates = attributes["mangaUpdates"]
        group.email = attributes["contactEmail"]
        group.bio = attributes["description"]
        group.focusedLanguage = attributes["focusedLanguages"]
        group.official = attributes["official"]
        if group.official == 'true':
            group.ex_licensed = attributes["exLicensed"]
        group.verified = attributes["verified"]
        group.inactive = attributes["inactive"]
        group.publish_delay = attributes["publishDelay"]
        group.relationships = [
            {relations['type']: relations['id']}
            for relations in resp["relationships"]
            if len(relations) > 1
        ]
        return group

    @staticmethod
    def create_group_list(resp) -> List["ScanlationGroup"]:
        """
        Creates a ScanlationGroup List from JSON
        """
        resp = resp["data"]
        group_list = []
        for elem in resp:
            group_list.append(ScanlationGroup().group_from_dict(elem))
        return group_list

    @property
    def url(self):
        """
        Returns the mangadex url
        """
        return f"{self.api.url}/group/{self.group_id}"

    def __eq__(self, other: Self) -> bool:
        my_vals = [self.group_id, self.name]
        other_vals = [other.group_id, other.name]
        return my_vals == other_vals

    def __ne__(self, other: Self) -> bool:
        return not self.__eq__(other)

    def __repr__(self) -> str:
        return (f"ScanlationGroup(id = {self.group_id}, name = {self.name}, leader = {self.leader}, \
                createdAt = {self.createdAt}, updatedAt = {self.updatedAt})")

    def multi_group_list(self, **kwargs) -> List["ScanlationGroup"]:
        """ Get information about multiple groups

        Args:
            limit: Number of authors to load
            offset:
            ids[]: Array of ids
            name: Name of scan group(for search)

        Returns:
            List[ScanlationGroup]: List of Scanlation Groups
        """
        if "ids" in kwargs:
            kwargs["ids[]"] = kwargs.pop("ids")

        url = f"{self.api.url}/group"
        resp = URLRequest.request_url(
            url, "GET", timeout=self.api.timeout, params=kwargs
        )
        return list(ScanlationGroup.group_from_dict(author) for author in resp["data"])

    def get_group_by_id(self, group_id: str) -> "ScanlationGroup":
        """Gets a group by its id

        :param group_id: str`: The id of the author
        
        :returns: Author`

        """
        url = f"{self.api.url}/author/{group_id}"
        resp = URLRequest.request_url(url, "GET", timeout=self.api.timeout)
        return ScanlationGroup.group_from_dict(resp)

    def create_group(
            self, name: str, version: int, ObjReturn: bool = False
    ) -> Union["Author", None]:
        """Creates an Author

        :param name: type name: `str`. The author name
        :param version: type version: `int`. The version of the author
        :param ObjReturn: bool` Default `False`. If set to `True`, it will return the info
        :param name: str:
        :param version: int:
        :param ObjReturn: bool:  (Default value = False)
        :returns: Union[Author, None]`

        """
        url = f"{self.api.url}/author"
        params = {"name": name, "version": version}
        resp = URLRequest.request_url(
            url,
            "POST",
            timeout=self.api.timeout,
            params=params,
            headers=self.auth.get_bearer_token(),
        )
        if ObjReturn:
            return Author.author_from_dict(resp)

    def update_group(
            self,
            *,
            author_id: str,
            version: int,
            name: Union[str, None] = None,
            ObjReturn: bool = False,
    ) -> Union["Author", None]:
        """ Updates and Author

        Args:
            author_id: The author id
            version: The version of author info
            name: The name of the author
            ObjReturn: Default `False`. If set to `True`, it will return the info

        Returns:
            Union[Author, None]:  Updated Chapter
        """
        url = f"{self.api.url}/author/{author_id}"
        params: Dict[str, Any] = {"version": version}
        if name is not None:
            params["name"] = name
        resp = URLRequest.request_url(
            url, "PUT", timeout=self.api.timeout, params=params, headers=self.auth.get_bearer_token()
        )

        if ObjReturn:
            return Author.author_from_dict(resp) if ObjReturn else None

    def delete_group(self, author_id: str) -> None:
        """Deletes an author

        :param author_id: str: Author ID
        :param author_id: str:

        """
        url = f"{self.api.url}/author/{author_id}"
        URLRequest.request_url(
            url, "DELETE", headers=self.auth.get_bearer_token(), timeout=self.api.timeout
        )


class User:
    def __init__(self, auth: Union[Auth, None]):
        self.auth = auth
        self.api = Api()

        self.id = None
        self.username = None
        self.roles = []
        self.relations = {}

    @property
    def url(self):
        """
        Returns mangadex url
        """
        return f"{self.api.url}/user/{self.id}"

    def __eq__(self, other: Self) -> bool:
        my_vals = [self.id, self.username]
        other_vals = [other.id, other.username]
        return my_vals == other_vals

    def __ne__(self, other: "User") -> bool:
        return not self.__eq__(other)

    def __repr__(self) -> str:
        return (f"User(id = {self.id}, username = {self.username}, \
                roles = {self.roles}, relations = {self.relations})")

    @classmethod
    def user_from_dict(cls, data: dict) -> "User":
        """Create a user object from raw data"""
        if "data" in data:
            data = data["data"]

        if data["type"] != "user" or not data:
            raise ValueError("The data provided is not a User JSON")

        attributes = data["attributes"]
        relationships = data["relationships"]

        user = cls(auth=None)  # No need to pass auth here
        user.id = data["id"]
        user.username = attributes["username"]
        user.roles = [' '.join([word.title() for word in role.split('_')])
                      for role in attributes["roles"]]
        user.relations = []
        if relationships:
            for relationship in relationships:
                user.relations.append({relationship["type"]: relationship["id"]})

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

    def get_user_list(self):
        pass

    def me(self) -> "User":
        url = f"{self.api.url}/user/me"
        resp = URLRequest.request_url(
            url, "GET",
            timeout=self.auth.timeout,
            headers=self.auth.get_bearer_token()
        )
        return User.user_from_dict(resp)

    def get_user(self, user_id: str) -> "User":
        url = f"{self.api.url}/user/{user_id}"
        resp = URLRequest.request_url(url, "GET", timeout=self.api.timeout)
        return User.user_from_dict(resp)


class Follows:
    def __init__(self, auth: Union[Auth, None]):
        self.auth = auth
        self.api = Api()

    def followed_groups(self, **kwargs) -> List["ScanlationGroup"]:
        """
        Get the Scanlation Groups you follow

        Parameters
        -------------
        limit `int`
        offset `int`
        translatedLanguage : `List[str]`

        Returns
        -------------
        `List[ScanlationGroup]`
        """
        if "translatedLanguage" in kwargs:
            kwargs["translatedLanguage[]"] = kwargs.pop("translatedLanguage")
        url = f"{self.api.url}/user/follows/group"
        resp = URLRequest.request_url(
            url, "GET", timeout=self.api.timeout, params=kwargs, headers=self.auth.get_bearer_token()
        )
        return ScanlationGroup.create_group_list(resp)

    def followed_users(self, **kwargs) -> List["User"]:
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
        url = f"{self.api.url}/user/follows/user"
        resp = URLRequest.request_url(
            url, "GET", timeout=self.api.timeout, params=kwargs, headers=self.auth.get_bearer_token()
        )
        return User.create_user_list(resp)

    def follow_manga(self, manga_id: Union[str, int]) -> None:
        """
        Follow a manga

        Parameters
        --------------
        manga_id : `str`. The manga id

        Raises
        -------------
        `ApiError`
        """
        url = f"{self.api.url}/manga/{manga_id}/follow"
        URLRequest.request_url(url, "POST", headers=self.auth.get_bearer_token(), timeout=self.api.timeout)

    def unfollow_manga(self, manga_id: str) -> None:
        """
        Unfollows a Manga

        Parameters
        -------------
        manga_id : `str`. The manga id

        Raises
        -----------
        `ApiError`
        """
        url = f"{self.api.url}/manga/{manga_id}/follow"
        URLRequest.request_url(url, "DELETE", headers=self.auth.get_bearer_token(), timeout=self.api.timeout)


if __name__ == '__main__':
    md = Author()
    print(md.list_author())
