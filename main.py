import json
import os

from config import CONFIG, DOWNLOAD, DOWNLOAD_PATH_KEY, SPINNER, cls, loading
from utility import search, download


def loadConfig() -> dict:
    """Gives the configuration from CONFIG file!"""
    try:
        if not os.path.exists(CONFIG):
            return writeConfig(DOWNLOAD)
        else:
            with open(CONFIG, 'r') as file:
                j = json.load(file)
                if j.get(DOWNLOAD_PATH_KEY):
                    return j
                else:
                    return writeConfig(DOWNLOAD)
    except Exception as load_exception:
        print(f"Unable to open \"{CONFIG}\": {repr(load_exception)}")
        return {DOWNLOAD_PATH_KEY: DOWNLOAD}


def writeConfig(path: str) -> dict:
    """Write configuration to CONFIG file!"""
    try:
        with open(CONFIG, 'w') as file:
            json.dump({DOWNLOAD_PATH_KEY: path}, file, indent=2, ensure_ascii=False)
        return loadConfig()
    except Exception as write_exception:
        print(f"Unable to open \"{CONFIG}\": {repr(write_exception)}")
        return {DOWNLOAD_PATH_KEY: DOWNLOAD}


def setPath() -> None:
    """Sets 'CWD' to the DOWNLOAD directory"""
    try:
        d_path = loadConfig().get(DOWNLOAD_PATH_KEY)
        os.makedirs(d_path, exist_ok=True)
        os.chdir(d_path)
    except Exception as cwd_error:
        print(f"Unable to change current path: {cwd_error}")


@loading(SPINNER, "Searching...")
def get_results(string: str) -> list[search.Query]:
    """Takes the keyword and returns the list of items related to the keyword!"""
    return search.Search(string).queries


@loading(SPINNER, "Extracting...")
def get_result(url: str) -> search.Query:
    """Takes an url and returns a video as a Query object"""
    return search.SearchWithUrl(url).video


@loading(SPINNER, "Downloading...")
def download_helper(q: search.Query, video: bool) -> None:
    download.Download(q.url, q.title, video)


@loading(SPINNER, "Extracting Playlist...")
def extract_playlist(url, video: bool) -> download.DownloadPlaylist:
    return download.DownloadPlaylist(url, video)


@loading(SPINNER, "Downloading Playlist...")
def download_playlist(o: download.DownloadPlaylist) -> None:
    o.download()


def path_validate() -> None:
    """Validates path, set new path, change cwd, etc"""
    p = input(f"Download Path: "
              f"{loadConfig().get(DOWNLOAD_PATH_KEY, DOWNLOAD)}\nDo You Want to change the download path?(y/n):\n")
    if p in ['yes', 'y']:
        p = input('Enter the path: ')
        writeConfig(p)
    setPath()


def downloader(q: search.Query | None, url: str, video: bool, playlist: bool) -> None:
    """Download the video/playlist"""
    path_validate()

    if playlist:
        playlist_obj = extract_playlist(url, video)
        print(f"Downloading: {playlist_obj.title}")
        download_playlist(playlist_obj)
        return
    else:
        print(f"Downloading: {q.title} [{q.duration}]")
        download_helper(q, video)


def show_items(queries: list[search.Query]) -> None:
    """prints the info of videos!"""
    cls()
    for idx, q in enumerate(queries, start=1):
        print(f"{idx}. {q.title} [{q.duration}]")


def get_item(queries: list[search.Query], idx: int) -> search.Query:
    """returns a video element from the list of elements via idx"""
    return queries[idx - 1]


def main() -> None:
    """Main execution starts here!"""
    query = input('Enter the query (url, name):\n')
    video = input('Video or Audio?(v/a):\n').lower()
    video = True if video.lower() in ['v', 'video'] else False
    is_playlist = search.is_playlist(query)
    is_url = search.is_url(query)

    if is_url:
        if is_playlist:
            # downloads the playlist based on given url
            downloader(q=None, video=video, url=query, playlist=True)
            return
        else:
            # download the video from the url
            downloader(q=get_result(query), video=video, url="", playlist=False)
            return
    else:
        results = get_results(query)
        show_items(results)
        idx = int(input("Choose the video (enter the index or s.no.):\n").strip())  # lazy work
        # downloads a single video from the list shown above
        downloader(q=get_item(results, idx), url="", playlist=False, video=video)


if __name__ == '__main__':
    while True:
        try:
            cls()
            main()
            choice = input("Continue?(y/n):\n").lower()
            if choice in ['yes', 'y']:
                continue
            else:
                break
        except Exception as e:
            print(f"Something went wrong: {repr(e)}")
