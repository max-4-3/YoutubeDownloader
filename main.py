import json
import os

from config import DOWNLOAD, CONFIG, SPINNER, Spinner, cls
from utility import search, download


def loadConfig() -> dict:
    try:
        if not os.path.exists(CONFIG):
            return writeConfig(DOWNLOAD)
        else:
            with open(CONFIG, 'r') as file:
                return json.load(file)
    except Exception as e:
        print(repr(e))


def writeConfig(path: str):
    try:
        with open(CONFIG, 'w') as file:
            json.dump({"download_path": path}, file, indent=2, ensure_ascii=False)
        return loadConfig()
    except Exception as e:
        print(repr(e))


def setPath():
    try:
        os.chdir(loadConfig().get('download_path', DOWNLOAD))
    except Exception as e:
        print(f"Unable to change current path: {e}")


def loading(spinner: Spinner, message: str = "", speed: float = 0.1):
    def spin(func):

        def wrapper(*args, **kwargs):
            try:
                spinner.msg = message or spinner.msg
                spinner.speed = speed

                spinner.start()
                results = func(*args, **kwargs)
            finally:
                spinner.stop()

            return results

        return wrapper

    return spin


@loading(SPINNER, "Searching...")
def get_results(string: str) -> list[search.Query]:
    """
    Takes the keyword and returns the list of items related to the keyword!
    """
    return search.Search(string).queries


@loading(SPINNER, "Extracting...")
def get_result(url: str) -> search.Query:
    """
    Takes an url and returns a video as a Query object
    """
    return search.SearchWithUrl(url).video


@loading(SPINNER, "Downloading...")
def download_helper(q: search.Query, video: bool):
    download.Download(q.url, q.title, video)


def path_validate():
    p = input(f"Download Path: "
              f"{loadConfig().get('download_path', DOWNLOAD)}\nDo You Want to change the download path?(y/n):\n")
    if p in ['yes', 'y']:
        p = input('Enter the path: ')
        writeConfig(p)
    setPath()


def downloader(q: search.Query | None, url: str, video: bool, playlist: bool) -> None:
    path_validate()

    if playlist:
        playlist_obj = download.DownloadPlaylist(url, video)
        print(f"Downloading: {playlist_obj.title}")
        loading(SPINNER)(playlist_obj.download)()
        return
    else:
        print(f"Downloading: {q.title} [{q.duration}]")
        download_helper(q, video)


def show_items(queries: list[search.Query]) -> None:
    for idx, q in enumerate(queries, start=1):
        print(f"{idx}. {q.title} [{q.duration}]")


def get_item(queries: list[search.Query], idx: int) -> search.Query:
    return queries[idx - 1]


def main():
    query = input('Enter the query (url, name):\n')
    video = input('Video or Audio?(v/a):\n').lower()
    video = True if video.lower() in ['v', 'video'] else False
    is_playlist = search.is_playlist(query)
    is_url = search.is_url(query)

    if is_url:
        downloader(q=get_result(query), video=video, url="", playlist=False)
    elif is_playlist:
        downloader(q=None, video=video, url=query, playlist=True)
    else:
        results = get_results(query)
        show_items(results)
        downloader(q=get_item(results, int(input("Choose the video:\n").strip())), url="", playlist=False, video=video)


if __name__ == '__main__':
    while True:
        cls()
        main()
        choice = input("Continue?(y/n):\n").lower()
        if choice in ['yes', 'y']:
            continue
        else:
            break
