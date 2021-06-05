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
    def test_SearchManga(self):
        # we're going to search for thge iris zero
        resp = self.api.get_manga_list(title = "iris zero", limit = 1)[0]

        try:
            saved_resp = read_json_files("test/saved_search_manga_response.json")

        except FileNotFoundError:
            print ("File not found")
            sys.exit()
        saved_resp = mangadex.Manga._create_manga(saved_resp["results"][0])
        assert resp == saved_resp, "The Manga objects are not equal"
    
    def test_GetMangaChapter(self):
        resp = self.api.get_chapter(id = "015979c8-ffa4-4afa-b48e-3da6d10279b0")
        try:
            saved_resp = read_json_files("test/saved_get_chapter_response.json")
        except FileNotFoundError:
            saved_resp = read_json_files("saved_get_chapter_response.json")
        finally:
            print("File not found, test failed")
        saved_resp = mangadex.Chapter._create_chapter(saved_resp),  "The Chapter Objects are not equal"
        assert resp == saved_resp
    
    def test_GetAuthor(self):
        raise NotImplementedError
    
    def test_GetScanlationGroup(self):
        raise NotImplementedError
    
    def test_GetTags(self):
        raise NotImplementedError
    
    def test_GetMangaChaptersAndVolumes(self):
        raise NotImplementedError

    def test_GetAuthor(self):
        raise NotImplementedError

    def test_GetAuthorById(self):
        raise NotImplementedError

    def test_save_jsons(self):
        url = f"{self.api.URL}/chapter/015979c8-ffa4-4afa-b48e-3da6d10279b0"
        with open("test/saved_get_chapter_response.json", "w+") as f:
            json.dump(mangadex.URLRequest._request_url(url, "GET", timeout=self.timeout),f)
        
