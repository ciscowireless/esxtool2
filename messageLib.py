import colorama


def ok():
    print(f"[ {colorama.Fore.GREEN}  OK  {colorama.Fore.RESET} ]  ", end = "")


def info():
    print(f"[ {colorama.Fore.YELLOW} INFO {colorama.Fore.RESET} ]  ", end = "")


def no():
    print(f"[ {colorama.Fore.RED}  NO  {colorama.Fore.RESET} ]  ", end = "")