from scraper import Scraper
from config import MOZZART_URL
from utils import main_thread
from credentials import MOZZART_MASTER_PHONE,MOZZART_MASTER_PASSWORD
import os
import argparse

parser=argparse.ArgumentParser(description='for controlling the bots configuration parameters')
parser.add_argument('--headless',action='store_true')
parser_arguments=parser.parse_args()

scraper=Scraper(target_url=MOZZART_URL,wait_time=30,headless=parser_arguments.headless)

scraper.folder_name='backup'
scraper.base_file_name='mozzart_aviator'

scraper.action(action='click',attribute='class="login-link mozzart_ke"',message='logging in...')
scraper.action(action='write',attribute='placeholder="Mobile number"',message='writing phone input...',input_value=MOZZART_MASTER_PHONE)
scraper.action(action='send',attribute='placeholder="Password"',message='writing password input...',input_value=MOZZART_MASTER_PASSWORD)
scraper.action(action='click',attribute='alt="Aviator"',message='connecting to game engine...',sleep_time=3)
scraper.action(action='callback',callback=scraper.watch_aviator)

scraper.navigate()
scraper.broadcast()

main_thread()