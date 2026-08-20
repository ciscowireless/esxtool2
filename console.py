"""Coloured console output helpers."""

import colorama

colorama.init()

_OK = f"[ {colorama.Fore.GREEN}  OK  {colorama.Fore.RESET} ]  "
_NO = f"[ {colorama.Fore.RED}  NO  {colorama.Fore.RESET} ]  "
_INFO = f"[ {colorama.Fore.YELLOW} INFO {colorama.Fore.RESET} ]  "

GREEN = colorama.Fore.GREEN
RED = colorama.Fore.RED
YELLOW = colorama.Fore.YELLOW
CYAN = colorama.Fore.CYAN
RESET = colorama.Fore.RESET


def ok(msg: str) -> None:
    print(f"{_OK}{msg}")


def error(msg: str) -> None:
    print(f"{_NO}{msg}")


def info(msg: str) -> None:
    print(f"{_INFO}{msg}")


def green(text: object) -> str:
    return f"{GREEN}{text}{RESET}"


def red(text: object) -> str:
    return f"{RED}{text}{RESET}"


def yellow(text: object) -> str:
    return f"{YELLOW}{text}{RESET}"
