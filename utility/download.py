import os
import platform
import time

import yt_dlp

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
        self.filename = filename

        if platform.system() in ["windows", "nt"]:
            self.filename = sanitize_filename(self.filename)

        self.options = self._set_options(video)

        playlist = is_playlist(self.url)

        if playlist:
            playlist_path = os.path.join(os.getcwd(), filename + 'playlist')
            os.makedirs(playlist_path, exist_ok=True)
            self.options.update({
                "noplaylist": False,
                "outtmpl": f"{playlist_path}/%(playlist_index)s - %(title)s.%(ext)s"
            })

        self.__download(self.options)
        if not playlist:
            self._modify_timestamp()

    def _set_options(self, video: bool):
        if video:
            return {
                'format': 'bestvideo+bestaudio/best',
                'outtmpl': f"{self.filename}.%(ext)s",
                'quiet': True,
                'no_warnings': True,
                'progress_hooks': [lambda d: None]
            }
        else:
            return {
                'format': 'bestaudio[ext=m4a]/bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '128',
                }],
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

        print(f"Unable to find file!")

    def __download(self, options):
        try:
            with yt_dlp.YoutubeDL(options) as ydl:
                ydl.download(self.url)
        except yt_dlp.DownloadError as d:
            print(f"Unable To Download: {repr(d)}")
        except Exception as e:
            print(f"Something Went Wrong: {repr(e)}")


class DownloadPlaylist:

    """
    Downloads video/audio from a YouTube playlist url!
    :param url: The url of the playlist
    :param video: Whether to download video or audio
    """

    def __init__(self, url: str, video: bool = False) -> None:
        self.url = url
        if not is_playlist(self.url):
            raise ValueError('Excepted a playlist url!')

        self.filename = self.title

        if platform.system() in ["windows", "nt"]:
            self.filename = sanitize_filename(self.filename)

        self.playlist_path = os.path.join(os.getcwd(), self.filename + '-playlist')
        os.makedirs(self.playlist_path, exist_ok=True)

        self._set_options(video)

    def _get_title(self):
        opts = {
            'quiet': True,  # Disable verbose output
            'no_warnings': True,  # Suppress warnings
            'extract_flat': True,  # Only extract metadata, no full processing
            'skip_download': True  # Do not download any content
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            title = ydl.extract_info(self.url, download=False).get('title', "Playlist1")
            return title

    def _set_options(self, video: bool):
        if video:
            self.options = {
                'format': 'bestvideo+bestaudio/best',
                'outtmpl': f"{self.playlist_path}/%(playlist_index)s - %(title)s.%(ext)s",
                'quiet': True,
                'no_warnings': True,
                'progress_hooks': [lambda d: None],
                'noplaylist': False
            }
        else:
            self.options = {
                'format': 'bestaudio[ext=m4a]/bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '128',
                }],
                'outtmpl': f"{self.playlist_path}/%(playlist_index)s - %(title)s.%(ext)s",
                'quiet': True,
                'no_warnings': True,
                'progress_hooks': [lambda d: None],
                'noplaylist': False
            }

    @property
    def title(self):
        return self._get_title()

    def download(self):
        try:
            with yt_dlp.YoutubeDL(self.options) as ydl:
                ydl.download(self.url)
        except yt_dlp.DownloadError as d:
            print(f"Unable To Download: {repr(d)}")
        except Exception as e:
            print(f"Something Went Wrong: {repr(e)}")

