from colorama import Fore, init, Style


class CLI:
    def __init__(self):
        init(autoreset=True)
        self.error_symbol = "[-]"
        self.success_symbol = "[+]"
        self.info_symbol = "[?]"
        self.input_symbol = "[>]"
        self.root_symbol = "[#]"
        self.magenta = Fore.LIGHTMAGENTA_EX
        self.yellow = Fore.LIGHTYELLOW_EX
        self.cyan = Fore.LIGHTCYAN_EX
        self.red = Fore.LIGHTRED_EX
        self.green = Fore.LIGHTGREEN_EX
        self.reset = Fore.RESET

    def error(self, text: str):
        print(f"{self.error_symbol} {self.magenta}{Style.BRIGHT}{text}{Fore.RESET}")

    def success(self, text: str):
        print(f"{self.success_symbol} {self.cyan}{Style.BRIGHT}{text}{Fore.RESET}")

    def info(self, text: str):
        print(f"{self.info_symbol} {self.yellow}{Style.BRIGHT}{text}{Fore.RESET}")

    def input(self, text: str):
        print(f"{self.input_symbol} {self.green}{Style.BRIGHT}{text}{Fore.RESET}")

    def root(self, text: str):
        print(f"{self.root_symbol} {self.red}{Style.NORMAL}{text}{Fore.RESET}")
