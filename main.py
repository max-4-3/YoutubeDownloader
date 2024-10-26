import json
import shutil
import subprocess as sp
import os
import random

from config import CONFIG, DOWNLOAD, DOWNLOAD_PATH_KEY, SPINNER, cls, loading, cli, is_windows, shell_script_path
from utility import search, download

WORK_AROUND = False
WORK_AROUND_FOLDER_NAME = None


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
        cli.error(f"Unable to open \"{CONFIG}\": {repr(load_exception)}")
        return {DOWNLOAD_PATH_KEY: DOWNLOAD}


def writeConfig(path: str) -> dict:
    """Write configuration to CONFIG file!"""

    # Path
    if path.startswith("~"):
        path = os.path.expanduser(path)

    if path.startswith("."):
        path = os.path.join(os.getcwd(), path[1:])

    try:
        with open(CONFIG, 'w') as file:

            json.dump({DOWNLOAD_PATH_KEY: path}, file, indent=2, ensure_ascii=False)
        return loadConfig()
    except Exception as write_exception:
        cli.error(f"Unable to open \"{CONFIG}\": {repr(write_exception)}")
        return {DOWNLOAD_PATH_KEY: DOWNLOAD}


def setPath() -> None:
    """Sets 'CWD' to the DOWNLOAD directory if WORK_AROUND is False"""

    if WORK_AROUND:
        new_path = os.path.join(os.path.split(__file__)[0], WORK_AROUND_FOLDER_NAME)
        os.makedirs(new_path, exist_ok=True)
        os.chdir(new_path)
        return

    try:
        d_path = loadConfig().get(DOWNLOAD_PATH_KEY)
        os.makedirs(d_path, exist_ok=True)
        os.chdir(d_path)
    except Exception as cwd_error:
        cli.error(f"Unable to change current path: {cwd_error}")


def work(file, destination_dir, temp_dir):
    new_name1 = f"{random.randint(1, 200000)}{os.path.splitext(file)[1]}"
    new_name2 = f"{random.randint(1, 2000000000)}{os.path.splitext(file)[1]}"

    cli.info(f"Renaming {file} -> {new_name1}")
    sp.run(['mv', file, new_name1], check=True)

    cli.info(f"Making A Empty File: {new_name2} in {destination_dir}")
    sp.run(['touch', os.path.join(destination_dir, new_name2)], check=True)

    cli.info(f"Data Copying from {new_name1} to {new_name2}")
    try:

        full_path1 = os.path.join(temp_dir, new_name1)
        full_path2 = os.path.join(destination_dir, new_name2)

        if ' ' in full_path1:
            full_path1 = "'" + full_path1 + "'"
        if ' ' in full_path2:
            full_path2 = "'" + full_path2 + "'"
        command = ['dd', f"if={full_path1}", f"of={full_path2}"]
        cli.root(f"Executing: {' '.join(command)}")
        sp.run(command, check=True)
        
        cli.info(f"Renaming {new_name2} -> {file}")
        sp.run(['mv', full_path2, file], check=True)
        cli.success("Completed!")
    except Exception as e:
        cli.error(f"Error: {e}")

def workaroundResolver() -> None:
    if not WORK_AROUND:
        return

    temp_path = os.path.join(os.path.split(__file__)[0], WORK_AROUND_FOLDER_NAME)

    if not os.path.exists(temp_path):
        return
    
    if os.getcwd() != temp_path:
        os.chdir(temp_path)

    dest_path = loadConfig().get(DOWNLOAD_PATH_KEY, DOWNLOAD)

    try:
        print(f"{cli.info_symbol}{cli.yellow} Coping {temp_path} to {dest_path}")

        os.makedirs(dest_path, exist_ok=True)

        for file in os.listdir(temp_path):

            if not is_windows:
                work(file, dest_path, temp_path)
            else:
                sp.run(['copy', os.path.join(temp_path, file), dest_path], check=True)

        if os.path.exists(temp_path):
            shutil.rmtree(temp_path)
    except PermissionError:

        print(f"{cli.info_symbol}{cli.yellow} Unable to do workaround!\nFile is saved in: {temp_path}")
    except Exception as exception:

        print(f"{cli.root_symbol}{cli.magenta} Unable to do Workaround: {repr(exception)}\nFile Stored in: {temp_path}")


@loading(SPINNER, "Searching...")
def get_results(string: str) -> list[search.Query]:
    """Takes the keyword and returns the list of items related to the keyword!"""
    return search.Search(string).queries


@loading(SPINNER, f"{cli.magenta}Extracting...{cli.reset}")
def get_result(url: str) -> search.Query:
    """Takes an url and returns a video as a Query object"""
    return search.SearchWithUrl(url).video


@loading(SPINNER, f"{cli.cyan}Downloading...{cli.reset}")
def download_helper(q: search.Query, video: bool) -> None:
    try:

        download.Download(q.url, q.title, video)
        print(f"\n{cli.success_symbol}{cli.cyan} {q.title} downloaded!")

    except PermissionError:

        cls()
        global WORK_AROUND
        WORK_AROUND = True

        setPath()
        print(f"{cli.root_symbol}{cli.magenta} Using WorkAround."
              f"\nDownloading in :{os.getcwd()}")

        download_helper(q, video)


@loading(SPINNER, f"{cli.magenta}Extracting Playlist...{cli.reset}")
def extract_playlist(url: str, video: bool) -> download.DownloadPlaylist:
    cls()
    return download.DownloadPlaylist(url, video)


@loading(SPINNER, f"{cli.cyan}Downloading Playlist...{cli.reset}")
def download_playlist(o: download.DownloadPlaylist) -> None:
    try:

        o.download()
        print(f"\n{cli.success_symbol}{cli.cyan} {o.title} downloaded!")

    except PermissionError:

        cls()
        global WORK_AROUND
        WORK_AROUND = True

        setPath()
        print(f"{cli.root_symbol}{cli.magenta} Using WorkAround."
              f"\nDownloading in :{os.getcwd()}")

        o.download()


def path_validate() -> None:
    """Validates path, set new path, change cwd, etc"""

    global WORK_AROUND

    print(f"{cli.root_symbol} Download Path: {cli.green}{loadConfig().get(DOWNLOAD_PATH_KEY, DOWNLOAD)}{cli.reset}")
    p = input(f"{cli.info_symbol} {cli.yellow}Do you want to change the path? (y/n){cli.reset}: \n")
    if p in ['yes', 'y']:
        p = input(f'{cli.input_symbol} {cli.green}Enter the path{cli.reset}: ')
        writeConfig(p)
    setPath()
    cls()


def downloader(q: search.Query = None, url: str = None, video: bool = False, playlist: bool = False) -> None:
    """Download the video/playlist"""
    cls()
    path_validate()

    if playlist and (url is not None):

        # If playlist and playlist url is provided
        playlist_obj = extract_playlist(url, video)
        cli.info(f"Downloading: {playlist_obj.title}")
        download_playlist(playlist_obj)
        return

    elif q is not None:

        # If Query object is provided
        cli.info(f"Downloading: {q.title} [{q.duration}]")
        download_helper(q, video)
        return

    else:

        # Maybe adding some parameters might help?
        cli.root("What a peaceful day, isn't it?")


def show_items(queries: list[search.Query]) -> None:
    """prints the info of videos!"""
    cls()
    for idx, q in enumerate(queries, start=1):
        print(f"{cli.green}{idx}. {cli.cyan}{q.title} {cli.reset}[{cli.magenta}{q.duration}{cli.reset}]")


def get_item(queries: list[search.Query], idx: int) -> search.Query:
    """returns a video element from the list of elements via idx"""
    return queries[idx - 1]


def main() -> None:
    """Main execution starts here!"""
    query = input(f'{cli.input_symbol} {cli.yellow}Enter the query (url, name){cli.reset}:\n')
    video = input(f'{cli.root_symbol} {cli.magenta}Video or Audio?(v/a){cli.reset}:\n').lower()
    video = True if video.lower() in ['v', 'video'] else False
    is_playlist = search.is_playlist(query)
    is_url = search.is_url(query)

    if is_url:
        if is_playlist:
            # downloads the playlist based on given url
            downloader(playlist=True, url=query, video=video)
            return
        else:
            # download the video from the url
            downloader(q=get_result(query), video=video)
            return
    else:
        results = get_results(query)
        show_items(results)
        idx = input(
            f"{cli.input_symbol} {cli.yellow}Choose the video (enter the index) or Retry (r){cli.reset}:\n"
        ).strip()
        if idx.lower() in ["reset", "try-again", "retry", "r"]:
            return
        else:
            idx = int(idx)
        # downloads a single video from the list shown above
        downloader(q=get_item(results, idx), video=video)

        # Workaround completer
        if WORK_AROUND:
            workaroundResolver()

        return


if __name__ == '__main__':
    init_dir = os.getcwd()
    while True:
        WORK_AROUND_FOLDER_NAME = f".temp_{random.randint(0, 100000000000)}"
        try:
            cls()
            main()
            os.chdir(init_dir)
            choice = input(f"{cli.input_symbol} {cli.magenta}Continue?(y/n){cli.reset}:\n").lower()
            if choice in ['yes', 'y']:
                continue
            else:
                break
        except Exception as e:
            cli.error(f"Something went wrong: {repr(e)}")
