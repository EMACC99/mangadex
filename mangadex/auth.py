"""Module providing authentication and checking for infrastructure"""
from __future__ import absolute_import
from typing import Optional

from typing_extensions import Self, Union, Dict, List

from mangadex.errors import ApiError
from mangadex.url_models import URLRequest


class Api:
    """Class that checks for Infrastructure"""
    def __init__(self):
        self.url = "https://api.mangadex.org"
        self.timeout = 5

    def ping(self) -> Optional[str]:
        """ Ping healthcheck

        Raises:
            ApiError: Raised when api is not functioning

        Returns:
            Optional[str]: Returns string when the Infrastructure is ok
        """
        url = f"{self.url}/ping"
        pong = URLRequest.request_url(url, "GET", timeout=self.timeout)
        if pong != "pong":
            raise ApiError(
                {"status": "503", "reason": "Infrastructure Unavailable"},
                "MangaDex Infrastructure is down",
            )
        return pong


class Auth:
    """Class that provides Authentication"""
    def __init__(self):
        """Authentication class"""
        self.auth_url = "https://auth.mangadex.org"
        self.timeout = 5  # Default timeout
        self.bearer = None
        self.refresh_token = None
        self.client_id = None
        self.client_secret = None

    def set_bearer_token(self, bearer_token:dict) -> None:
        """Sets the bearer token. Used by other functions

        Args:
            bearer_token (dict): Bearer token
        """
        self.bearer = bearer_token

    def get_bearer_token(self) -> dict:
        """Gets the bearer token. Used by other functions

        Returns:
            str: The bearer token
        """
        return self.bearer

    def __auth_handler(self, http_form: dict, headers: dict) -> None:
        """Handles OAuth2 Requests to log in"""
        url = f"{self.auth_url}/realms/mangadex/protocol/openid-connect/token"
        auth_response = URLRequest.request_url(
            url, "POST", params=http_form, timeout=self.timeout, headers=headers
        )

        self.client_id = http_form["client_id"]
        self.client_secret = http_form["client_secret"]
        access_token = auth_response["access_token"]
        refresh_token = auth_response["refresh_token"]
        self.set_bearer_token({"Authorization": f"Bearer {access_token}"})
        self.refresh_token = refresh_token

    def login(
        self, username: str, password: str, client_id: str, client_secret: str
    ) -> None:
        """Logs into MangaDex

        Args:
            username (str): User's username
            password (str): User's password
            client_id (str): User's personal client ID
            client_secret (str): User's personal client secret
        """
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        self.__auth_handler(
            {
                "grant_type": "password",
                "username": username,
                "password": password,
                "client_id": client_id,
                "client_secret": client_secret,
            },
            headers,
        )

    def refresh_login(self) -> None:
        """Reauthenticate using refresh token"""
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        self.__auth_handler(
            {
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
            headers,
        )


class ApiClient(Auth):
    """ Class that checks for user's API Clients"""
    def __init__(self, auth: Union[Auth, None]):
        super().__init__()
        self.api = Api()
        self.auth = auth

        self.name = ""
        self.description = ""
        self.profile = ""
        self.client_id = ""
        self.state = ""
        self.is_active = ""
        self.created_at = ""
        self.updated_at = ""
        self.relations = []

    @classmethod
    def client_from_dict(cls, data: dict) -> "ApiClient":
        """Get client from json

        Args:
            data (dict): Raw JSON data

        Raises:
            ValueError: Raised when the data provided is not a Client JSON

        Returns:
            ApiClient: ApiClient info
        """
        try:
            data = data["data"]
        except (KeyError, TypeError):
            pass

        if data["type"] != "api_client" or not data:
            raise ValueError("The data provided is not a api_client")

        client = cls(auth=None)

        attributes = data["attributes"]

        client.name = attributes["name"]
        client.description = attributes["description"]
        client.profile = attributes["profile"]
        client.client_id = attributes["externalClientId"]
        client.state = attributes["state"]
        client.is_active = attributes["isActive"]
        client.created_at = attributes["createdAt"]
        client.updated_at = attributes["updatedAt"]
        for relation in attributes["relationships"]:
            client.relations.append({"type": relation["type"], "id": relation["id"]})

        return client

    def __eq__(self, other: Self) -> bool:
        my_vals = [self.client_id, self.name, self.created_at]
        other_vals = [other.client_id, other.name, other.created_at]
        return my_vals == other_vals

    def __ne__(self, other: Self) -> bool:
        return not self.__eq__(other)

    def __repr__(self) -> str:
        part1 = f"ApiClient(clientId = {self.client_id}, name = {self.name}, \
                        description = {self.description}, profile = {self.profile}, \
                        state = {self.state}, isActive = {self.is_active} \n"
        part2 = f"createdAt = {self.created_at}, uploadedAt = {self.updated_at} \
                        relations = {self.relations})"
        return f"{part1}{part2}"

    @staticmethod
    def __parse_client_params(params: Dict[str, str]) -> Dict[str, str]:
        if "includes" in params:
            params["includes[]"] = params.pop("includes")
        return params

    @staticmethod
    def create_client_list(resp: dict) -> List["ApiClient"]:
        """Creates info list from list of API Clients

        Args:
            resp (dict): Raw response

        Returns:
            List["ApiClient"]: List of API Client infos
        """
        resp = resp["data"]
        client = []
        for elem in resp:
            client.append(ApiClient.client_from_dict(elem))
        return client

    def get_api_clients(self, **kwargs) -> List["ApiClient"]:
        """List user's ApiClient

        Args:
            limit: Number of clients to show
            offset: 

        Returns:
            ApiClient:
        """
        params = self.__parse_client_params(kwargs)
        url = f"{self.api.url}/client"
        resp = URLRequest.request_url(
            url,
            "GET",
            headers=self.auth.get_bearer_token(),
            timeout=self.api.timeout,
            params=params,
        )
        return ApiClient.create_client_list(resp)

    def get_api_client_by_id(self, client_id: str) -> "ApiClient":
        """Gets the info of API Client from ID

        Args:
            client_id (str): Client ID in UUID format

        Returns:
            ApiClient: API Client info
        """
        url = f"{self.api.url}/client/{client_id}"
        resp = URLRequest.request_url(
            url, "GET", headers=self.auth.get_bearer_token(), timeout=self.timeout
        )
        return ApiClient.client_from_dict(resp)

    def create_api_client(
        self, name: str, description: str, obj_return: bool = True
    ) -> Optional["ApiClient"]:
        """_summary_

        Returns:
            _type_: _description_
        """
        url = f"{self.api.url}/client"
        params = {
            "name": name,
            "description": description,
            "profile": "personal",
            "version": 1,
        }
        resp = URLRequest.request_url(
            url,
            "POST",
            timeout=self.api.timeout,
            headers=self.auth.get_bearer_token(),
            params=params,
        )
        return ApiClient.client_from_dict(resp) if obj_return else None

    def edit_api_client(
        self, client_id: str,
        description: str,
        obj_return: bool = True)-> Optional["ApiClient"]:
        """Change an API Client description

        Returns:
            Optional["ApiClient"]: Returns the info if obj_return is specified
        """
        url = f"{self.api.url}/client/{client_id}"
        params = {"description": description}
        resp = URLRequest.request_url(
            url,
            "GET",
            params=params,
            headers=self.auth.get_bearer_token(),
            timeout=self.api.timeout,
        )
        return ApiClient.client_from_dict(resp) if obj_return else None

    def delete_api_client(self, client_id: str):
        """Deletes the API Client

        Args:
            client_id (str): Client ID you want to delete

        Raises:
            ApiError: Raised if the request is wrong
        """
        url = f"{self.api.url}/client/{client_id}"
        resp = URLRequest.request_url(
            url,
            "DELETE",
            headers=self.auth.get_bearer_token(),
            timeout=self.api.timeout,
        )
        if resp["result"] != "ok":
            raise ApiError(resp["errors"][0]["detail"])

    def get_api_secret(self, client_id: str) -> "ApiClient":
        """Get API Client Secret

        Args:
            client_id (str): The Client ID in UUID form

        Raises:
            ApiError: Raised when the authentication fails

        Returns:
            ApiClient: API Client info
        """
        url = f"{self.api.url}/client/{client_id}/secret"
        resp = URLRequest.request_url(
            url, "GET", headers=self.auth.get_bearer_token(), timeout=self.timeout
        )
        if resp["result"] != "ok":
            raise ApiError(resp["errors"][0]["detail"])
        return ApiClient.client_from_dict(resp)

    def regen_api_secret(self, client_id: str) -> "ApiClient":
        """Regenerates API Client Secret

        Args:
            client_id (str): The Client ID

        Raises:
            ApiError: Raised when the authentication fails

        Returns:
            ApiClient: API Client info
        """
        url = f"{self.api.url}/client/{client_id}/secret"
        resp = URLRequest.request_url(
            url, "POST", headers=self.auth.get_bearer_token(), timeout=self.timeout
        )
        if resp["result"] != "ok":
            raise ApiError(resp["errors"][0]["detail"])
        return ApiClient.client_from_dict(resp)


if __name__ == "__main__":
    from .people import User
    from dotenv import load_dotenv

    load_dotenv("mangadex/api/.env")
    api = Api()

    # auth = Auth()
    # auth.login(os.environ['md_username'], os.environ['md_password'],
    #            os.environ['client_id'], os.environ['client_secret'])
    user = User(auth=None)
    print(user.get_user("fca42d9d-b00c-4b52-8966-c3e1061fca4e"))
