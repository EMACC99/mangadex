import mangadex

api = mangadex.Api()

manga_list = api.get_manga_list(limit=2)
print(manga_list)