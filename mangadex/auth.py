from __future__ import absolute_import

from typing_extensions import Self, Union, Dict, List

from mangadex.errors import ApiError
from mangadex.url_models import URLRequest


# TODO: Fix the in-code documentation
class Api:
    def __init__(self):
        self.url = "https://api.mangadex.org"
        self.timeout = 5

    def ping(self):
        url = f"{self.url}/ping"
        pong = URLRequest.request_url(url, "GET", timeout=self.timeout)
        if pong != "pong":
            raise ApiError(
                {"status": "503", "reason": "Infrastructure Unavailable"},
                "MangaDex Infrastructure is down",
            )
        # if we raise we dont return
        return pong


class Auth:
    def __init__(self):
        """Authentication class"""
        self.auth_url = "https://auth.mangadex.org"
        self.timeout = 5  # Default timeout
        self.bearer = None
        self.refresh_token = None
        self.client_id = None
        self.client_secret = None

    def set_bearer_token(self, bearer_token):
        self.bearer = bearer_token

    def get_bearer_token(self):
        return self.bearer

    def __auth_handler(self, http_form: dict, headers: dict) -> None:
        """Handle OAuth2 Requests"""
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
            username (str): The user's username
            password (str): The user's password
            client_id (str): The user's personal client ID
            client_secret (str): The user's personal client secret
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
    def __init__(self, auth: Union[Auth, None]):
        super().__init__()
        self.api = api
        self.auth = auth

        self.name = ""
        self.description = ""
        self.profile = ""
        self.client_id = ""
        self.state = ""
        self.isActive = ""
        self.createdAt = ""
        self.updatedAt = ""
        self.relations = []

    @classmethod
    def client_from_dict(cls, data: dict):
        """Get client from json

        Args:
            data (dict): Raw JSON data

        Raises:
            ValueError: Raised when the data provided is not a Client JSON

        Returns:
            Cover: The Coverart ids
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
        client.isActive = attributes["isActive"]
        client.createdAt = attributes["createdAt"]
        client.updatedAt = attributes["updatedAt"]
        for relation in attributes["relationships"]:
            client.relations.append({"type": relation["type"], "id": relation["id"]})

        return client

    def __eq__(self, other: Self) -> bool:
        my_vals = [self.client_id, self.name, self.createdAt]
        other_vals = [other.client_id, other.name, other.createdAt]
        return my_vals == other_vals

    def __ne__(self, other: Self) -> bool:
        return not self.__eq__(other)

    def __repr__(self) -> str:
        part1 = f"ApiClient(clientId = {self.client_id}, name = {self.name}, \
                        description = {self.description}, profile = {self.profile}, \
                        state = {self.state}, isActive = {self.isActive} \n"
        part2 = f"createdAt = {self.createdAt}, uploadedAt = {self.updatedAt} \
                        relations = {self.relations})"
        return f"{part1}{part2}"

    @staticmethod
    def __parse_client_params(params: Dict[str, str]) -> Dict[str, str]:
        if "includes" in params:
            params["includes[]"] = params.pop("includes")
        return params

    @staticmethod
    def create_client_list(resp: dict):
        resp = resp["data"]
        client = []
        for elem in resp:
            client.append(ApiClient.client_from_dict(elem))
        return client

    def get_api_clients(self, **kwargs) -> List["ApiClient"]:
        """Get users ApiClient

        Args:
            **kwargs: The API client arguments

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

    def get_api_client_by_id(self, client_id: str):
        url = f"{self.api.url}/client/{client_id}"
        resp = URLRequest.request_url(
            url, "GET", headers=self.auth.get_bearer_token(), timeout=self.timeout
        )
        return ApiClient.client_from_dict(resp)

    def create_api_client(
        self, name: str, description: str, ObjReturn: bool = True
    ) -> Union["ApiClient", None]:
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
        return ApiClient.client_from_dict(resp) if ObjReturn else None

    def edit_api_client(self, client_id: str, description: str, ObjReturn: bool = True):
        url = f"{self.api.url}/client/{client_id}"
        params = {"description": description}
        resp = URLRequest.request_url(
            url,
            "GET",
            params=params,
            headers=self.auth.get_bearer_token(),
            timeout=self.api.timeout,
        )
        return ApiClient.client_from_dict(resp) if ObjReturn else None

    def delete_api_client(self, client_id: str):
        url = f"{self.api.url}/client/{client_id}"
        resp = URLRequest.request_url(
            url,
            "DELETE",
            headers=self.auth.get_bearer_token(),
            timeout=self.api.timeout,
        )
        if resp["result"] != "ok":
            raise Exception(resp["errors"][0]["detail"])

    def get_api_secret(self, client_id: str):
        url = f"{self.api.url}/client/{client_id}/secret"
        resp = URLRequest.request_url(
            url, "GET", headers=self.auth.get_bearer_token(), timeout=self.timeout
        )
        if resp["result"] != "ok":
            raise Exception(resp["errors"][0]["detail"])
        return ApiClient.client_from_dict(resp)

    def regen_api_secret(self, client_id: str):
        url = f"{self.api.url}/client/{client_id}/secret"
        resp = URLRequest.request_url(
            url, "POST", headers=self.auth.get_bearer_token(), timeout=self.timeout
        )
        if resp["result"] != "ok":
            raise Exception(resp["errors"][0]["detail"])
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
