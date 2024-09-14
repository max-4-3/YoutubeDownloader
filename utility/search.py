from random import choice
from re import compile as rcomp

from youtube_search import YoutubeSearch


def is_url(string):
    regex = rcomp(r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(watch\?v=|embed/|shorts/)|youtu\.be\/)([a-zA-Z0-9_-]+)')
    return bool(regex.match(string))


def is_playlist(url):
    regex = rcomp(r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com|youtu\.be)\/.*(?:\?|&)list=([^&]+)')
    return bool(regex.match(url))


class Query:

    __slots__ = (
        'title',
        'url',
        'id',
        'thumbnails',
        'thumbnail',
        'uploader',
        'duration',
        'views'
    )

    def __init__(self, cont: dict) -> None:
        self.__set(cont)

    def __set(self, item):
        self.title = item.get("title", "No Title")
        suffix = item.get('url_suffix')
        self.url = ("https://youtube.com" + suffix) if suffix else item.get("webpage_url")
        self.id = item.get("id")
        self.thumbnails = item.get("thumbnails", [])
        self.thumbnail = choice(self.thumbnails)
        self.views = item.get("views", item.get("view_count"))
        self.uploader = item.get("channel", item.get("channel"))
        try:
            duration = item.get('duration')
            self.duration = duration if isinstance(duration, str) else f"{duration // 60}:{duration % 60}"
        except (AttributeError, Exception):
            self.duration = item.get("duration", 120)


class Search:
    """
    Search on YouTube for a video based on provided keyword
    :raise ValueError: if keyword is an url!
    """
    def __init__(self, keyword: str, amount: int = 10) -> None:
        self.keyword = keyword
        self.amount = amount
        self.queries = None

        if not self.keyword:
            raise ValueError("Invalid Keyword Given!")

        if is_url(self.keyword):
            raise ValueError('Excepted keyword not url!')
        else:
            self.__search()

    def __search(self):
        results = YoutubeSearch(self.keyword, self.amount).to_dict()
        self.queries = [Query(k) for k in results]


class SearchWithUrl:
    """
    Gives the info of the video from provided url
    :raise ValueError: if url is not an url!
    """
    __slots__ = (
        'video'
    )

    def __init__(self, url: str) -> None:
        if not is_url(url):
            raise ValueError(f'Excepted url not {url}')
        self.__get(url)

    def __get(self, url):
        import yt_dlp
        ydl_opts = {
            'quiet': True,
            'skip_download': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            self.video = Query(info_dict)
