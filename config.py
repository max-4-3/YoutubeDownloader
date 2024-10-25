import os
from platform import system as platform_name

from utility.cli import CLI
from utility.spinner import Spinner

CONFIG = None
DOWNLOAD = None
SPINNER = None
cli = CLI()
DOWNLOAD_PATH_KEY = "download_path"  # The name of the key for download path
CONFIG_FILE_NAME = "yt_downloader_config.json"
is_windows = True if platform_name().lower() in ['windows', 'nt'] else False


def set_config():
    global CONFIG, DOWNLOAD, SPINNER

    if is_windows:
        CONFIG = os.path.join(
            os.getenv('LOCALAPPDATA'),
            CONFIG_FILE_NAME
        )
    else:
        CONFIG = os.path.join(os.path.split(__file__)[0], "files", CONFIG_FILE_NAME)

    if is_windows:
        DOWNLOAD = os.path.join(os.getenv('USERPROFILE'), "Downloads")
    else:
        DOWNLOAD = os.path.join(os.path.split(__file__)[0], "downloads")

    SPINNER = Spinner(msg="", speed=0.1)


def cls():
    if is_windows:
        os.system('cls')
    else:
        try:
            os.system('clear')
        except PermissionError:
            import subprocess
            subprocess.run('clear')


def loading(spinner: Spinner, message: str = "", speed: float = 0.1):
    def spin(func):

        def wrapper(*args, **kwargs):
            try:
                spinner.msg = message or spinner.msg
                spinner.speed = speed

                if spinner.is_running:
                    spinner.stop()
                spinner.start()
                results = func(*args, **kwargs)
            finally:
                if spinner.is_running:
                    spinner.stop()

            return results

        return wrapper

    return spin


# actually sets the configurations
set_config()

__all__ = (
    CONFIG,
    DOWNLOAD,
    SPINNER,
    DOWNLOAD_PATH_KEY,
    cls,
    loading
)
