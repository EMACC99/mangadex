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
        failed = False
        resp = self.api.get_manga_list(title = "iris zero", limit = 1)[0]

        try:
            saved_resp = read_json_files("test/saved_search_manga_response.json")
        except FileNotFoundError:
            failed = True
        saved_resp = mangadex.Manga._create_manga(saved_resp["results"][0])

        if failed:
            pytest.fail("File not found")

        assert resp == saved_resp, "The Manga objects are not equal"
    
    def test_GetMangaChapter(self):
        failed = False
        resp = self.api.get_chapter(id = "015979c8-ffa4-4afa-b48e-3da6d10279b0")
        try:
            saved_resp = read_json_files("test/saved_get_chapter_response.json")
        except FileNotFoundError:
            failed = True
            
        saved_resp = mangadex.Chapter._create_chapter(saved_resp)

        if failed:
            pytest.fail("File not found, test could not be completed")
        
        assert resp == saved_resp,  "The Chapter Objects are not equal"

    def test_GetAuthor(self):
        failed = False
        resp = self.api.get_author_by_id(id = "df765fdc-ea9f-45d0-9191-d95615662d49")
        try:
            saved_resp = read_json_files("test/saved_get_author_id_response.json")
        except:
            failed = True
        
        saved_resp = mangadex.Author._create_author(saved_resp)

        if failed:
            pytest.fail("File not found, test could not be completed")
        
        assert resp == saved_resp, "The Author Objects are not equal"
    
    def test_GetTags(self):
        failed = False
        resp = self.api.tag_list()
        try:
            saved_reps = read_json_files("test/saved_get_tag_response.json")
        except FileNotFoundError:
            failed = True
        
        if failed: 
            pytest.fail("File not found, test could not be completed")
        
        saved_reps = mangadex.Tag._create_tag_list(saved_reps)

        assert resp == saved_reps, "The test objects are not equal"

    def test_GetMangaChaptersAndVolumes(self):
        #lets use iris zero as is in hiatus
        failed = False
        resp = self.api.get_manga_volumes_and_chapters(id = "786ff721-8fd3-413d-8e50-938d8b06f917")

        try:
            saved_resp = read_json_files("test/saved_get_manga_chaps_and_volumes_response.json")
        except FileNotFoundError:
            failed = True
        
        if failed:
            pytest.fail("File not found, test could not be completed")

        saved_resp = saved_resp["volumes"]
        assert resp == saved_resp, "The values are not equal"

    # def test_save_jsons(self):
    #     url = f"{self.api.URL}/group"
    #     params = {"ids[]" : "f5f83084-ec42-4354-96fd-1b637a89b8b3"}
    #     with open("test/saved_get_scan_group_response.json", "w+") as f:
    #         json.dump(mangadex.URLRequest._request_url(url, "GET", timeout=self.timeout, params=params),f)

    def test_GetScanlationGroup(self):
        failed = False
        resp = self.api.scanlation_group_list(group_ids = "f5f83084-ec42-4354-96fd-1b637a89b8b3") # black cat scanlations

        try:
            saved_response = read_json_files("test/saved_get_scan_group_response.json")
        except FileNotFoundError:
            failed = True
        
        if failed:
            pytest.fail("File not found, test could not be completed")

        saved_response = mangadex.ScanlationGroup._create_group_list(saved_response)
        assert resp == saved_response
        