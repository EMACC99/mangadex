"""
Module for unit and integration tests
"""

import os

import pytest
from dotenv import load_dotenv

from mangadex import URLRequest, ApiError
import mangadex as md

load_dotenv()


class TestApi:
    """Class for testing API infrastructure calls"""

    api = md.Api()
    timeout = 5

    def test_ping(self):
        ping = self.api.ping()
        saved_resp = URLRequest.request_url(f"{self.api.url}/ping", "GET", self.timeout)
        assert ping == saved_resp


class TestManga:
    """
    Class for testing the public API calls
    """

    manga = md.series.Manga()
    tag = md.series.Tag()
    timeout = 5

    def test_mangaList(self):
        self.manga.get_manga_list(limit=1)[0]

    def test_SearchManga(self):
        # we're going to search for the iris zero
        resp = self.manga.get_manga_list(title="iris zero", limit=1)[0]

        url = f"{self.manga.api.url}/manga"
        raw_response = URLRequest.request_url(
            url, "GET", timeout=self.timeout, params={"limit": 1, "title": "iris zero"}
        )

        saved_resp = md.Manga.manga_from_dict(raw_response["data"][0])

        assert resp == saved_resp, "The Manga objects are not equal"

    def test_SearchMangaWithLotOfArgs(self):
        tags = self.tag.tag_list()
        wanted_tags = ["Oneshot", "Romance"]
        not_wanted_tags = ["Loli", "Incest"]
        wanted_tags_ids = []
        not_wanted_tags_ids = []
        for _, tag in enumerate(tags):
            if tag.name["en"] in wanted_tags:
                wanted_tags_ids.append(tag.tag_id)
            elif tag.name["en"] in not_wanted_tags:
                not_wanted_tags_ids.append(tag.tag_id)

        self.manga.get_manga_list(
            contentRating=["erotica", "pornographic"],
            status=["completed"],
            excludedTags=not_wanted_tags_ids,
            excludedTagsMode="AND",
            includedTags=wanted_tags_ids,
            includedTagsMode="AND",
        )

    def test_GetTranslatedManga(self):
        self.manga.get_manga_list(translatedLanguage=["en"], limit=1)[0]

    def test_GetMangaFeed(self):
        resp = self.manga.get_manga_list(title="iris zero", limit=1)[0]
        self.manga.manga_feed(resp.manga_id)

    def test_ViewMangaById(self):
        self.manga.get_manga_by_id(manga_id="88796863-04bd-49d4-ad85-d9f993e95109")

    def test_RandomManga(self):
        self.manga.random_manga()

    def test_GetMangaChaptersAndVolumes(self):
        # lets use iris zero as is in hiatus
        manga_id = "786ff721-8fd3-413d-8e50-938d8b06f917"
        resp = self.manga.get_manga_volumes_and_chapters(manga_id=manga_id)

        url = f"{self.manga.api.url}/manga/{manga_id}/aggregate"

        raw_response = URLRequest.request_url(url, "GET", timeout=self.timeout)

        saved_resp = raw_response["volumes"]

        assert resp == saved_resp, "The values are not equal"


class TestChapter:
    chapter = md.series.Chapter()
    author = md.people.Author()
    timeout = 5

    def test_GetMangaChapter(self):
        ch_id = "015979c8-ffa4-4afa-b48e-3da6d10279b0"
        resp = self.chapter.get_chapter_by_id(chapter_id=ch_id)

        url = f"{self.chapter.api.url}/chapter/{ch_id}"
        raw_response = URLRequest.request_url(
            url, "GET", timeout=self.timeout, params={"id": ch_id}
        )

        saved_resp = md.Chapter.chapter_from_dict(raw_response)

        assert resp == saved_resp, "The Chapter Objects are not equal"

    def test_FetchChapterImages(self):
        ch_id = "015979c8-ffa4-4afa-b48e-3da6d10279b0"

        resp = self.chapter.get_chapter_by_id(chapter_id=ch_id)

        resp.fetch_chapter_images()


class TestAuthor:
    author = md.people.Author()
    chapter = md.series.Chapter()
    timeout = 5

    def test_GetAuthor(self):
        author_id = "df765fdc-ea9f-45d0-9191-d95615662d49"

        resp = self.author.get_author_by_id(author_id=author_id)

        url = f"{self.author.api.url}/author/{author_id}"

        raw_response = URLRequest.request_url(
            url, "GET", timeout=self.timeout, params={"id": author_id}
        )

        saved_resp = md.Author.author_from_dict(raw_response)

        assert resp == saved_resp, "The Author Objects are not equal"

    def test_GetManyAuthor(self):
        author_ids = [
            "df765fdc-ea9f-45d0-9191-d95615662d49",
            "742bea86-c1ae-4893-bd06-805287991849",
        ]

        resp = self.author.list_author(ids=author_ids)

        url = (
            f"{self.author.api.url}/author/?ids[]={author_ids[0]}&ids[]={author_ids[1]}"
        )
        raw_response = URLRequest.request_url(url, "GET", timeout=self.timeout)

        manual_authors = [
            md.Author.author_from_dict(author) for author in raw_response["data"]
        ]
        manual_authors = dict(((author.author_id, author) for author in manual_authors))

        for author in author_ids:
            api_author = next((a for a in resp if a.author_id == author), None)
            assert api_author is not None, "Required author not returned in response"
            assert (
                api_author == manual_authors[author]
            ), "The Author Objects are not equal"


class TestTag:
    tag = md.series.Tag()
    timeout = 5

    def test_GetTags(self):
        resp = self.tag.tag_list()

        url = f"{self.tag.api.url}/manga/tag"
        raw_response = URLRequest.request_url(url, "GET", timeout=self.timeout)
        saved_reps = md.Tag.create_tag_list(raw_response)

        assert resp == saved_reps, "The test objects are not equal"


class TestScanlationGroup:
    scangroup = md.ScanlationGroup()
    api = md.Api()
    timeout = 5

    def test_GetScanlationGroup(self):
        ids = ["f5f83084-ec42-4354-96fd-1b637a89b8b3"]
        resp = self.scangroup.multi_group_list(ids=ids)  # black cat scanlations

        url = f"{self.scangroup.api.url}/group"
        raw_response = URLRequest.request_url(
            url, "GET", timeout=self.api.timeout, params={"ids[]": ids}
        )

        saved_response = md.ScanlationGroup.create_group_list(raw_response)

        assert resp == saved_response


class TestCoverArt:
    manga = md.series.Manga()
    coverart = md.series.Cover()
    customlist = md.series.CustomList()

    def test_GetCoverArtList(self):
        self.coverart.get_coverart_list()

    def test_GetMangaCoverArt(self):
        random_manga = self.manga.random_manga()
        self.coverart.get_cover(random_manga.cover_id)

    def test_GetCustomList(self):
        custom_list_id = "aa0356ad-12c8-4f1a-9723-8342ade4dc6e"
        self.customlist.get_customlist(customlist_id=custom_list_id)


@pytest.mark.skipif(
    "md_username" not in os.environ
    or "md_password" not in os.environ
    or "client_id" not in os.environ
    or "client_secret" not in os.environ,
    reason="The credentials are not in env",
)
class TestAuth:
    """
    Class for testing private API calls
    """

    auth = md.auth.Auth()
    user = md.people.User(auth=auth)
    manga = md.series.Manga(auth=auth)
    follows = md.people.Follows(auth=auth)
    mangalist = md.series.MangaList(auth=auth)
    customlist = md.series.CustomList(auth=auth)

    timeout = 5

    def login(self):
        self.auth.login(
            os.environ.get("md_username"),
            os.environ.get("md_password"),
            os.environ.get("client_id"),
            os.environ.get("client_secret"),
        )

    def test_GetUser(self):
        self.login()
        user = self.user.me()

        assert user.username == os.environ.get("md_username"), "This user is invalid"

    def test_GetUserCustomLists(self):
        self.login()
        user_id = self.user.me()
        self.customlist.get_user_customlists(user_id.id)

    def test_GetMangaReadingStatus(self):
        self.login()
        manga_id = "35c33279-395d-4d9f-abec-93893c28ab29"
        self.manga.get_manga_read_markers(manga_id=manga_id)

    def test_GetAllMangaReadingStatus(self):
        self.login()
        self.manga.get_all_manga_reading_status()

    def test_GetMyMangaList(self):
        self.login()
        self.mangalist.get_my_mangalist()

    def test_FollowManga(self):
        self.login()
        manga_id = "32d76d19-8a05-4db0-9fc2-e0b0648fe9d0"  # solo leveling
        self.follows.follow_manga(manga_id=manga_id)

    def test_UnfollowManga(self):
        self.login()
        manga_id = "32d76d19-8a05-4db0-9fc2-e0b0648fe9d0"  # solo leveling
        self.follows.unfollow_manga(manga_id=manga_id)

    def test_GetMyCustomLists(self):
        self.login()
        self.customlist.get_my_customlists()


class Test_Errors:
    """
    Class for testing the errors
    """

    chapter = md.series.Chapter()
    follows = md.people.Follows(auth=None)
    timeout = 5

    def test_BadRequest(self): ...

    def test_NotFound(self):
        try:
            ch_id = (
                "015979c8-ffa4-4afa-b48e-3da6d102fdfsdfsdfsdfs"  # some random string
            )
            resp = self.chapter.get_chapter_by_id(chapter_id=ch_id)
            resp.fetch_chapter_images()
        except ApiError as e:
            assert 404 == e.code

    def test_Unauthorized(self):  # Errors out
        manga_id = "32d76d19-8a05-4db0-9fc2-e0b0648fe9d0"  # solo leveling
        try:
            self.follows.follow_manga(manga_id=manga_id)
        except AttributeError:
            pass
