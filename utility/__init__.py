from platform import system as platform_name

is_windows = True if platform_name().lower() in ['windows', 'nt'] else False
