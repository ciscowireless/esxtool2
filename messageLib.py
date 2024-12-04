import colorama


class Status():

    def __init__(self):

        self.ok = f"[ {colorama.Fore.GREEN}  OK  {colorama.Fore.RESET} ]  "
        self.no = f"[ {colorama.Fore.RED}  NO  {colorama.Fore.RESET} ]  "
        self.info = f"[ {colorama.Fore.YELLOW} INFO {colorama.Fore.RESET} ]  "
