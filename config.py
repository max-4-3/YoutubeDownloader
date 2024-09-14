import os
from platform import system as platform_name

from utility.spinner import Spinner

# the yt_downloader_config.json path
if platform_name().lower() in ['windows', 'nt']:
    CONFIG = os.path.join(
        os.getenv('LOCALAPPDATA'),
        'yt_downloader_config.json'
    )
else:
    CONFIG = "files/yt_downloader_config.json"

# the default download path
if platform_name().lower() in ['windows', 'nt']:
    DOWNLOAD = os.path.join(os.getenv('HOMEPATH'), "Downloads")
else:
    DOWNLOAD = "downloads"

# loading spinner
SPINNER = Spinner("", speed=0.1)


def cls():
    if platform_name().lower() in ['windows', 'nt']:
        os.system('cls')
    else:
        try:
            os.system('clear')
        except PermissionError:
            import subprocess
            subprocess.run('clear')

