import os
import sys
import mangadex
import json
import pytest

def read_json_files(filename : str, mode :str = "r") -> dict:
    with open(filename, mode) as f:
        resp = json.load(f)
    return resp

class TestApi():
    api = mangadex.Api()
    timeout = 5
    
    def test_mangaList(self):
        self.api.get_manga_list(limit = 1)[0]
        
    def test_SearchManga(self):
        # we're going to search for the iris zero
        resp = self.api.get_manga_list(title = "iris zero", limit = 1)[0]

        url = f"{self.api.URL}/manga"
        raw_response = mangadex.URLRequest._request_url(url, "GET", timeout = self.timeout, params={"limit" : 1, "title" : "iris zero"})

        saved_resp = mangadex.Manga._create_manga(raw_response["data"][0])

        assert resp == saved_resp, "The Manga objects are not equal"
    
    def test_GetMangaChapter(self):
        ch_id = "015979c8-ffa4-4afa-b48e-3da6d10279b0"
        resp = self.api.get_chapter(id = ch_id)

        url = f"{self.api.URL}/chapter/{ch_id}"
        raw_response = mangadex.URLRequest._request_url(url, "GET", timeout = self.timeout, params= {"id" : ch_id})

        saved_resp = mangadex.Chapter._create_chapter(raw_response)        

        assert resp == saved_resp,  "The Chapter Objects are not equal"

    def test_GetAuthor(self):

        author_id = "df765fdc-ea9f-45d0-9191-d95615662d49"

        resp = self.api.get_author_by_id(id = author_id)

        url = f"{self.api.URL}/author/{author_id}"

        raw_respone  = mangadex.URLRequest._request_url(url, "GET", timeout = self.timeout, params = {"id" : author_id})

        saved_resp = mangadex.Author._create_author(raw_respone)

        assert resp == saved_resp, "The Author Objects are not equal"
    
    def test_GetTags(self):
        resp = self.api.tag_list()

        url = f"{self.api.URL}/manga/tag"
        raw_response = mangadex.URLRequest._request_url(url, "GET", timeout = self.timeout)
        saved_reps = mangadex.Tag._create_tag_list(raw_response)

        assert resp == saved_reps, "The test objects are not equal"

    def test_GetMangaChaptersAndVolumes(self):
        #lets use iris zero as is in hiatus
        manga_id = "786ff721-8fd3-413d-8e50-938d8b06f917"
        resp = self.api.get_manga_volumes_and_chapters(id = manga_id)

        url = f"{self.api.URL}/manga/{manga_id}/aggregate"
        
        raw_response = mangadex.URLRequest._request_url(url, "GET", timeout = self.timeout)
    
        saved_resp = raw_response["volumes"]

        assert resp == saved_resp, "The values are not equal"


    def test_GetScanlationGroup(self):
        ids = ["f5f83084-ec42-4354-96fd-1b637a89b8b3"]
        resp = self.api.scanlation_group_list(group_ids = ids) # black cat scanlations

        url = f"{self.api.URL}/group"
        raw_response = mangadex.URLRequest._request_url(url, "GET", timeout = self.timeout, params = {"ids[]" : ids})

        saved_response = mangadex.ScanlationGroup._create_group_list(raw_response)

        assert resp == saved_response
        
    # def test_GetChapter(self):
    #     raise NotImplementedError

    # def test_FetchCoverImages(self):
    #     raise NotImplementedError

    # def test_(self):
    #     raise NotImplementedError