"""Module providing Chapter and Manga info"""

from __future__ import absolute_import

from typing import Optional, List

from mangadex.url_models import URLRequest

from .auth import Api, Auth


class Forums:
    """Class for Manga"""

    def __init__(self, auth: Optional[Auth]):
        self.auth = auth
        self.api = Api()

        self.id: str = ""

    @classmethod
    def forum_from_dict(cls, resp: dict) -> "Forums":
        """Create a Forum from JSON

        Args:
            resp (dict): Raw JSON data

        Returns:
            Forums: Forum Information
        """
        forum = cls(None)
        if resp["result"] != "ok":
            raise ValueError("The arguments provided is wrong")

        forum.id = resp["data"]["id"]
        return forum

    def create_forums_thread(self, **kwargs):
        """Creates a thread in the forums, in lieu of comments

        Args:
            type (str): Type of object. Options: `'manga'`, `'chapter'`
            id: ID of object
        """
        url = f"{self.api.url}/forums/thread"
        headers = self.auth.get_bearer_token()
        headers["Content-Type"] = "application/json"
        resp = URLRequest.request_url(
            url, "POST", params=kwargs, headers=headers, timeout=self.api.timeout
        )
        return Forums.forum_from_dict(resp)


class Stats:
    """Class for Settings"""

    def __init__(self):
        self.api = Api()

        self.object_id:str = ""
        self.thread_id: str = ""
        self.replies: int = None
        self.ratings: dict = None
        self.follows: int = None

    def __repr__(self) -> str:
        temp1 = f"Stats(thread_id = {self.thread_id}, replies = {self.replies},\
            ratings = {self.ratings}, follows = {self.follows})"
        return temp1

    @classmethod
    def stats_from_dict(cls, data: dict, object_id: str) -> "Stats":
        """
        Creates a Stats object from JSON
        """
        stats = cls()
        try:
            data = data["statistics"][object_id]
        except KeyError:
            pass

        if "rating" in list(data.keys()):
            stats.ratings = data["rating"]

        if "follows" in list(data.keys()):
            stats.follows = data["follows"]

        stats.object_id = object_id
        print(data)
        if data['comments'] != 'null':
            stats.thread_id = data["comments"]["threadId"]
            stats.replies = data["comments"]["repliesCount"]

        return stats

    @staticmethod
    def create_stats_list(resp) -> List["Stats"]:
        """
        Creates a manga list from a JSON
        """
        resp = resp["statistics"]
        manga_list = []
        for elem in [*resp.keys()]:
            manga_list.append(Stats.stats_from_dict(resp[elem], elem))
        return manga_list

    def get_chapter_stats(self, chapter_id: str) -> "Stats":
        """Get the group stats

        Args:
            chapter_id (str): Chapter ID

        Returns:
            Stats
        """
        url = f"{self.api.url}/statistics/chapter/{chapter_id}"
        resp = URLRequest.request_url(url, "GET", timeout=self.api.timeout)
        return Stats.stats_from_dict(resp, chapter_id)

    def get_chapters_stats(self, **kwargs) -> "Stats":
        """Get stats for multiple chapters

        Args:
            chapter[] (str): Chapter ID

        Returns:
            Stats
        """
        try:
            params = {'chapter[]': kwargs['chapter']}
        except KeyError as exc:
            raise ValueError("Did not give any chapter id in 'chapter' kwarg") from exc

        url = f"{self.api.url}/statistics/chapter/"
        resp = URLRequest.request_url(
            url, "GET", params=params, timeout=self.api.timeout
        )
        return Stats.create_stats_list(resp)

    def get_group_stats(self, group_id: str) -> "Stats":
        """Get the group stats

        Args:
            group_id (str): Group ID

        Returns:
            Stats
        """
        url = f"{self.api.url}/statistics/group/{group_id}"
        resp = URLRequest.request_url(url, "GET", timeout=self.api.timeout)
        return Stats.stats_from_dict(resp, group_id)

    def get_groups_stats(self, **kwargs) -> "Stats":
        """Get stats for multiple groups

        Args:
            groups[] (str): Group IDs

        Returns:
            Stats
        """
        try:
            params = {'group[]': kwargs['groups']}
        except KeyError as exc:
            raise ValueError("Did not give any manga id in 'groups' kwarg") from exc

        url = f"{self.api.url}/statistics/group/"
        resp = URLRequest.request_url(
            url, "GET", params=params, timeout=self.api.timeout
        )
        return Stats.create_stats_list(resp)

    def get_manga_stats(self, group_id: str) -> "Stats":
        """Get the manga stats

        Args:
            manga_id (str): Manga ID

        Returns:
            Stats
        """
        url = f"{self.api.url}/statistics/manga/{group_id}"
        resp = URLRequest.request_url(url, "GET", timeout=self.api.timeout)
        return Stats.stats_from_dict(resp, group_id)

    def get_multimanga_stats(self, **kwargs) -> List["Stats"]:
        """Get stats for multiple manga

        Args:
            manga[] (str): Manga IDs

        Returns:
            Stats
        """
        try:
            params = {'manga[]': kwargs['manga']}
        except KeyError as exc:
            raise ValueError("Did not give any manga id in 'manga' kwarg") from exc

        url = f"{self.api.url}/statistics/manga/"
        resp = URLRequest.request_url(
            url, "GET", params=params, timeout=self.api.timeout
        )
        return Stats.create_stats_list(resp)
