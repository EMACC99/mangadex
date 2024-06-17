# mangadex.py

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A python wrapper for the MangaDex API V5. It uses the requests library and all the aditional arguments can be viewed in the [Official Mangadex Documentation](https://api.mangadex.org/docs/)

## Instaling the API wrapper module

### PyPI

```sh
pip install --Upgrade mangadex
```

### Installing via setuptools

```sh
python setup.py install --user
```

## Wrapper Usage

```py
>>> import mangadex as md
>>> auth = md.auth.Auth()
>>> manga = md.series.Manga(auth=auth)
>>> chapter = md.series.Chapter(auth=auth)
>>> customlist = md.series.CustomList(auth=auth)
>>> tag = md.series.Tag(auth=auth)
>>> cover = md.series.Cover(auth=auth)
>>> scangroup = md.people.ScanlationGroup(auth=auth)
>>> user = md.people.User(auth=auth)
>>> follows = md.people.Follows(auth=auth)
```

## Manga

### Getting the latest manga chapters

This is called mangalist in the [documentation](https://api.mangadex.org/docs.html#operation/get-search-manga)

```py
>>> manga_list = manga.get_manga_list(limit = 1) #limits the query to return just one manga
>>> manga_list[Manga(manga_id = 0001183c-2089-48e9-96b7-d48db5f1a611, title = {'en': 'Eight'}, altTitles = [{'ja': '8（エイト）'}], description = {'en': 'Tokyo in the 90s, the city center has been suffering from a continuing depopulation. Also affected is the Udagawa Junior High School where only six people are left, as their class leader, protector and very good friend Masato just died in an illegal skateboarding race. Five months later Eito Hachiya, nickname: Eight or "8" enrolls in school and wants to find out what happened. He even just looks like Masato! But mysteries surround him: Why does he know all the other six? Why can’t they remember him?  \n  \nNote: Was cancelled after ~25% of volume 4, the epilogue consists of an alternative ending for Eight.'}, isLocked = False, links = {'al': '38734', 'ap': 'eight', 'kt': '17709', 'mu': '6521', 'amz': 'https://www.amazon.co.jp/dp/B07WS2K894', 'mal': '8734', 'raw': 'https://csbs.shogakukan.co.jp/book?book_group_id=14478'}, originalLanguage = ja
 lastVolume = 4, lastChapter = 37.6, publicationDemographic = seinen, status = completed, year = 2000, contentRating = safe
 createdAt = 2018-02-04 21:32:02+00:00, uploadedAt = 2022-01-12 21:42:40+00:00), author_id = ['905aaced-1556-4925-bff0-14ea277fb0b1', '905aaced-1556-4925-bff0-14ea277fb0b1'], artist_id = [], cover_id = 51bf2e88-98ac-4fd7-afb5-80edff694d53
```

### Searching manga

```py
>>> manga_list = manga.get_manga_list(title = "You manga title here")
```

### Getting manga information by its id

```py
>>> manga = manga.view_manga_by_id(manga_id = "0001183c-2089-48e9-96b7-d48db5f1a611")
```

### Getting random manga

```py
>>> random_manga = Manga.random_manga()
```

### Manga Feed

Get the chapter, or chapters from MDList.

```py
>>> manga_feed = Manga.manga_feed(manga_id = "0001183c-2089-48e9-96b7-d48db5f1a611", limit = 1)
[Chapter(chapter_id = 015979c8-ffa4-4afa-b48e-3da6d10279b0, title = Navel-Gazing, volume = 3, chapter = 23.0, translatedLanguage = en, hash =
 data = List[filenames], publishAt = 2018-03-19 01:32:00+00:00, createdAt = 2018-03-19 01:32:00+00:00, uploadedAt = 2018-03-19 01:32:00+00:00, group_id = 59957a04-fa91-4099-921d-7e7988a19acb, manga_id = 0001183c-2089-48e9-96b7-d48db5f1a611, uploader = e19519ce-8c5f-4d7c-8280-704a87d34429)]
```

## Chapter

### Get manga volumes and chapters

```py
>>> chapter.get_manga_volumes_and_chapters(manga_id = "the manga id")
```

### Get Chapter Info

```py
>>> chp = chapter.get_chapter(chapter_id = "015979c8-ffa4-4afa-b48e-3da6d10279b0")
>> chp
Chapter(chapter_id = 015979c8-ffa4-4afa-b48e-3da6d10279b0, title = Navel-Gazing, volume = 3, chapter = 23.0, translatedLanguage = en, hash =
data = List[filenames], publishAt = 2018-03-19 01:32:00+00:00, createdAt = 2018-03-19 01:32:00+00:00, uploadedAt = 2018-03-19 01:32:00+00:00, group_id = 59957a04-fa91-4099-921d-7e7988a19acb, manga_id = 0001183c-2089-48e9-96b7-d48db5f1a611, uploader = e19519ce-8c5f-4d7c-8280-704a87d34429)
```

### Chapter List

Returns a list of latest chapters

```py
>>> chapter_list = chapter.chapter_list()
```

### Chapter Images

Return the links for the chapter images.

```py
>>> chapter.fetch_chapter_images()
```

## Tag

### Get Tag List

```py
>>> tag_list = tag.tag_list()
```

## Scanlation Group

### Get Scanlation Group List

```py
>>> scangroup.scanlation_group_list()
```

## Cover

### Get Cover Images List

```py
>>> cover.get_coverart_list()
```

### Get Cover by Id

```py
>>> cover.get_cover(cover_id = "the cover id")
```

### Edit Cover

```py
>>> cover.edit_cover(cover_id = "the cover id", description = "the cover description, can be null", volume = "the volume number", version = "int, the cover version")
```

### Get cover image link

```py
>>> cover.fetch_cover_image()
```

This is a CoverArt method that returns the cover image url of that object

## Private Calls

### Login

**Username and password combo-only logins are deprecated as MangaDex shift to OAuth. [Personal clients](https://api.mangadex.org/docs/02-authentication/personal-clients/) are needed alongside it. [#26](https://github.com/EMACC99/mangadex/issues/26)**

Method to login to the website

```py
>>> auth.login(username = USERNAME, password = PASSWORD, client_id = clientId, client_secret = clientSecret)
```

It is recomended that you add this values to your environment variables and use text input for client-facing solutions for security reasons.

```py
>>> auth.login(os.environ['md_username'], os.environ['md_password'],os.environ['client_id'], os.environ['client_secret'])
```

### Your User Info

Get your user info

```py
>>> my_user = user.me()
```

### Get User Info

```py
>>> user = user.get_user(user_id = "id of user")
```

### Get Logged User Followed Manga List

Get your manga follow list!

```py
>>> follow_list = follows.get_my_mangalist()
```

### Get Logged User Followed Groups

Get the list of the Scanlation group you follow!

```py
>>> scangroups_followlist = follows.get_my_followed_groups()
```

### Get Logged User Followed Users

Get the list of the users you follow!

```py
>>> followed_users = follows.get_my_followed_users()
```

### Get chapters marked as read from a manga

Get a list of the chapters marked as read for a given manga

```py
>>> read_chapters = manga.get_manga_read_markes(id = "the manga id")
```

### Get all followed manga reading status

Get a list of the all the manga reading stauts

```py
>>> my_manga_reading_stauts = manga.get_all_manga_reading_status()
```

### Get a specific manga reading status

Get the reading status of a specific manga

```py
>>> manga_reading_status = manga.get_manga_reading_status(manga_id = "the manga id")
```

### Update Manga reading status

```py
>>> manga.update_manga_reading_status(manga_id = "the manga id", status = "the new reading status")
```

The `status` parameter can take the following values:
`"reading"` `"on_hold"` `"plan_to_read"` `"dropped"` `"re_reading"` `"completed"`

### Follow a manga

Follow a manga

```py
>>> follows.follow_manga(manga_id = "the manga id")
```

### Unfollow a manga

Unfollows a manga

```py
>>> manga.unfollow_manga(manga_id = "the manga id")
```

### Create manga

Creates a manga

```py
>>> manga.create_manga(title = "manga title", )
```

### Update Manga

Update manga information

```py
>>> manga.update_manga(manga_id = "the manga id")
```

### Delete Manga

Deletes manga

```py
>>> manga.delete_manga(manga_id = "the manga id")
```

### Add manga to custom list

Add a manga to a custom list

```py
>>> customlist.add_manga_to_customlist(manga_id = "the manga id", list_id = "the list id")
```

### Remove a manga from custom list

Removes a manga from a custom list

```py
>>> customlist.remove_manga_from_customlist(id = "the manga id", listId = "the list id")
```

### Create a custom list

```py
>>> customlist.create_customlist() #this will create a custom list with no special parameters
```

### Get custom list

```py
>>> customlist.get_customlist(id = "custom list id")
```

### Update custom list

```py
>>> customlist.update_customlist(id = "custom list id")
```

### Delete custom list

```py
>>> customlist.delete_customlist(id = "the custom list id")
```

### Get User Custom list

```py
>>> customlist.get_user_customlists(id = "the user id")
```

### Create Author

```py
>>> author.create_author(name = "author name", version = 1, ObjReturn = False)
```

### Update Author

```py
>>> author.update_author(id = "the author id", version = "int with the version", name = "author's name", ObjReturn = False)
```

### Delete Author

```py
>>> author.delete_author(id = "the author id")
```

### Disclaimer

All the credit for the API goes to the MangaDex Team.
