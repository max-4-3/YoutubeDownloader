import os
import time

import yt_dlp

from utility import is_windows
from .search import is_playlist


def sanitize_filename(filename: str):

    reserved_chars = [r'<', r'>', r':', r'"', r'/', r'\\', r'|', r'?', r'*']
    for char in reserved_chars:
        filename = filename.replace(char, '_')

    filename = filename.strip()

    if not filename:
        filename = 'File Name is Empty lol'

    return filename


class Download:

    """
    Downloads a YouTube video either as an audio file or as a video file!
    :param url: The url of the video
    :param filename: The filename or simple pass the title of the video
    :param video: Whether to download video or audio
    """

    def __init__(self, url: str, filename: str, video: bool = False) -> None:
        self.url = url
        self.filename = sanitize_filename(filename) if is_windows else filename

        playlist = is_playlist(self.url)

        if playlist:
            raise ValueError(f'Excepted a video url not a playlist url!')

        self._set_options(video)
        self.__download()

    def _choose_format_id(self):
        ydl_opts = {
            'format': 'all',
            'listformats': False,
            'quiet': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(self.url, download=False)

        fmts = info.get('formats', None)

        if not fmts:
            return None

        audio = {}
        audio_end_index = 0
        for idx, a in enumerate(fmts, start=1):
            if ('audio only' in a.get('format').lower()) and (a.get('abr', 0) not in [0, None]):
                audio[len(audio) + 1] = a
                audio_end_index = idx

        video = {}
        for idx, v in enumerate(fmts, start=1):
            if idx <= audio_end_index:
                continue
            if (v.get('height', 0) == 0) or (v.get('vbr', 0) == 0):
                continue
            video[len(video) + 1] = v

        high_video = max(video.values(), key=lambda a: (a.get('vbr', 0), a.get('height', 0)))
        high_audio = max(audio.values(), key=lambda a: a.get('abr', 0))

        return f"{high_audio['format_id']}+{high_video['format_id']}"
    
    def _set_options(self, video: bool):

        fmt = self._choose_format_id()

        if video:
            self.options = {
                'format': fmt if fmt is not None else 'bv*+ba/b',
                'outtmpl': f"{self.filename}.%(ext)s",
                'quiet': True,
                'no_warnings': True,
                'progress_hooks': [lambda d: None]
            }
        else:
            self.options = {
                'format': 'bestaudio[ext=m4a]/bestaudio/best',
                'outtmpl': f"{self.filename}.%(ext)s",
                'quiet': True,
                'no_warnings': True,
                'progress_hooks': [lambda d: None]
            }

    def _modify_timestamp(self):
        current_time = time.time()

        for file in os.listdir(os.getcwd()):

            if not os.path.isfile(file):
                continue

            if os.path.splitext(file)[0] != self.filename:
                continue

            fp = os.path.join(os.getcwd(), file)
            os.utime(fp, (current_time, current_time))
            return

        print(f"Unable to find {self.filename}!")

    def __download(self):
        try:
            with yt_dlp.YoutubeDL(self.options) as ydl:
                ydl.download(self.url)
            self._modify_timestamp()
        except yt_dlp.DownloadError as d:
            if "Operation not permitted".lower() in str(d).lower():
                raise PermissionError
            print(f"Unable To Download: {repr(d)}")
        except Exception as e:
            print(f"Something Went Wrong: {repr(e)}")


class DownloadPlaylist:

    """
    Downloads video/audio from a YouTube playlist url!
    :param url: The url of the playlist
    :param video: Whether to download video or audio
    """

    __slots__ = (
        'url',
        'title',
        'options',
        'filename',
        'playlist_url',
        'playlist_path'
    )

    def __init__(self, url: str, video: bool = False) -> None:
        self.url = url
        if not is_playlist(self.url):
            raise ValueError('Excepted a playlist url!')

        # Sets the options for downloading either a video or audio
        self._set_options(video)
        # Sets the title and playlist url + handles the path generation and validation
        self._set_title_and_playlist_url(self._get_metadata())

    def _choose_format_id(self):
        ydl_opts = {
            'format': 'all',
            'listformats': False,
            'quiet': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(self.url, download=False)

        fmts = info.get('formats', None)

        if not fmts:
            return None

        audio = {}
        audio_end_index = 0
        for idx, a in enumerate(fmts, start=1):
            if ('audio only' in a.get('format').lower()) and (a.get('abr', 0) not in [0, None]):
                audio[len(audio) + 1] = a
                audio_end_index = idx

        video = {}
        for idx, v in enumerate(fmts, start=1):
            if idx <= audio_end_index:
                continue
            if (v.get('height', 0) == 0) or (v.get('vbr', 0) == 0):
                continue
            video[len(video) + 1] = v

        high_video = max(video.values(), key=lambda a: (a.get('vbr', 0), a.get('height', 0)))
        high_audio = max(audio.values(), key=lambda a: a.get('abr', 0))

        return f"{high_audio['format_id']}+{high_video['format_id']}"

    def _get_metadata(self):
        opts = {
            'quiet': True,  # Disable verbose output
            'no_warnings': True,  # Suppress warnings
            'extract_flat': True,  # Only extract metadata, no full processing
            'skip_download': True  # Do not download any content
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(self.url, download=False)
            return info

    def _set_title_and_playlist_url(self, metadata: dict):
        self.title = metadata.get('title')
        self.playlist_url = metadata.get('url')
        self._set_paths()

    def _set_options(self, video: bool):

        fmt = self._choose_format_id().get('format_id', None)

        if video:
            self.options = {
                'format': 'bestvideo+bestaudio/best' if not fmt else fmt,
                'quiet': True,
                'no_warnings': True,
                'progress_hooks': [lambda d: None],
                'noplaylist': False
            }
        else:
            self.options = {
                'format': 'bestaudio[ext=m4a]/bestaudio/best',
                'quiet': True,
                'no_warnings': True,
                'progress_hooks': [lambda d: None],
                'noplaylist': False
            }

    def _set_paths(self):
        self.filename = sanitize_filename(self.title) if is_windows else self.title
        self.playlist_path = os.path.join(os.getcwd(), self.filename + '-playlist')

        # makes the download path
        os.makedirs(self.playlist_path, exist_ok=True)

        # adds the paths to self.options
        self.options['outtmpl'] = f"{self.playlist_path}/%(playlist_index)s - %(title)s.%(ext)s"

    def download(self):
        try:
            with yt_dlp.YoutubeDL(self.options) as ydl:
                ydl.download(self.playlist_url)
        except yt_dlp.DownloadError as d:
            if "Operation not permitted".lower() in str(d).lower():
                raise PermissionError
            print(f"Unable To Download: {repr(d)}")
        except Exception as e:
            print(f"Something Went Wrong: {repr(e)}")

    def __repr__(self):
        return f"Downloading: {self.title} in {self.playlist_path}"
