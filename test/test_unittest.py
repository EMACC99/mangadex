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
        # we're going to search for the iris zero
        failed = False
        resp = self.api.get_manga_list(title = "iris zero", limit = 1)[0]

        try:
            saved_resp = read_json_files("test/saved_search_manga_response.json")
        except FileNotFoundError:
            print ("File not found")
            failed = True
        saved_resp = mangadex.Manga._create_manga(saved_resp["results"][0])

        if failed:
            return False

        assert resp == saved_resp, "The Manga objects are not equal"
    
    def test_GetMangaChapter(self):
        failed = False
        resp = self.api.get_chapter(id = "015979c8-ffa4-4afa-b48e-3da6d10279b0")
        try:
            saved_resp = read_json_files("test/saved_get_chapter_response.json")
        except FileNotFoundError:
            saved_resp = read_json_files("saved_get_chapter_response.json")
        finally:
            print("File not found, test failed")
            failed = True
            
        saved_resp = mangadex.Chapter._create_chapter(saved_resp)

        if failed:
            return False

        assert resp == saved_resp,  "The Chapter Objects are not equal"

    # def test_save_jsons(self):
    #     url = f"{self.api.URL}/author/df765fdc-ea9f-45d0-9191-d95615662d49"
    #     with open("test/saved_get_author_id_response.json", "w+") as f:
    #         json.dump(mangadex.URLRequest._request_url(url, "GET", timeout=self.timeout),f)
    
    def test_GetAuthor(self):
        failed = False
        resp = self.api.get_author_by_id(id = "df765fdc-ea9f-45d0-9191-d95615662d49")
        try:
            saved_resp = read_json_files("test/saved_get_author_id_response.json")
        except:
            saved_resp = read_json_files("saved_get_author_id_response.json")
        finally:
            print("File not found, test could not be completed")
            failed = False
        
        saved_resp = mangadex.Author._create_author(saved_resp)

        if failed:
            return False
        
        assert resp == saved_resp, "The Author Objects are not equal"

    def test_GetScanlationGroup(self):
        raise NotImplementedError
    
    def test_GetTags(self):
        raise NotImplementedError
    
    def test_GetMangaChaptersAndVolumes(self):
        raise NotImplementedError

