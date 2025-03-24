from scraper import Scraper
from config import MOZZART_URL
from utils import main_thread
from credentials import MOZZART_MASTER_PHONE,MOZZART_MASTER_PASSWORD
import os
import argparse

parser=argparse.ArgumentParser(description='for controlling the bots configuration parameters')
parser.add_argument('--headless',action='store_true')
parser.add_argument('--backup',action='store_true')
parser.add_argument('--phone',default=MOZZART_MASTER_PHONE)
parser.add_argument('--password',default=MOZZART_MASTER_PASSWORD)

parser_arguments=parser.parse_args()

scraper=Scraper(target_url=MOZZART_URL,url_identifier='mozzart',wait_time=30,headless=parser_arguments.headless,backup=parser_arguments.backup)

scraper.folder_name='backup'
scraper.base_file_name='mozzart_aviator'

scraper.action(action='click',attribute='class="login-link mozzart_ke"',message='logging in...')
scraper.action(action='write',attribute='placeholder="Mobile number"',message='writing phone input...',input_value=parser_arguments.phone)
scraper.action(action='send',attribute='placeholder="Password"',message='writing password input...',input_value=parser_arguments.password)
scraper.action(action='click',attribute='alt="Aviator"',message='connecting to game engine...',sleep_time=3)
scraper.action(action='callback',callback=scraper.watch_aviator)

scraper.navigate()
scraper.broadcast()

main_thread()