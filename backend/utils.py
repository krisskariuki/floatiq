from colorama import Fore,init
import sys
import time

init(autoreset=True)
white=Fore.WHITE
red=Fore.RED
green=Fore.GREEN
yellow=Fore.YELLOW
cyan=Fore.CYAN
magenta=Fore.MAGENTA
brown=Fore.LIGHTBLACK_EX

class Colors:
    def __init__(self):
        self.white=Fore.WHITE
        self.red=Fore.RED
        self.green=Fore.GREEN
        self.yellow=Fore.YELLOW
        self.cyan=Fore.CYAN
        self.magenta=Fore.MAGENTA
        self.brown=Fore.LIGHTBLACK_EX

colors=Colors()

def main_thread():
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f'\n{colors.yellow}exiting program ...\n')
        sys.exit(0)