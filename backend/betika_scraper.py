from scraper import Scraper
from config import BETIKA_URL
from utils import main_thread
from credentials import BETKIA_KRISS_PHONE,BETIKA_KRISS_PASSWORD
import os
import argparse

parser=argparse.ArgumentParser(description='for controlling the bots configuration parameters')
parser.add_argument('--headless',action='store_true')
parser.add_argument('--backup',action='store_true')
parser_arguments=parser.parse_args()

scraper=Scraper(target_url=BETIKA_URL,wait_time=30,headless=parser_arguments.headless,backup=parser_arguments.backup)

scraper.folder_name='backup'
scraper.base_file_name='betika_aviator'

scraper.action(action='click',attribute='href="/en-ke/login?next=%2F"',message='logging in...')
scraper.action(action='write',attribute='placeholder="e.g. 0712 234567"',message='writing phone input...',input_value=BETKIA_KRISS_PHONE)
scraper.action(action='send',attribute='type="password"',message='writing password input...',input_value=BETIKA_KRISS_PASSWORD)
scraper.action(action='click',attribute='class="session__form__button__container"')
scraper.action(action='click',attribute='href="/en-ke/aviator"',message='connecting to game engine...',sleep_time=3)
scraper.action(action='switch_to_iframe',attribute='id="aviator-iframe')
scraper.action(action='callback',callback=scraper.watch_aviator)

scraper.navigate()
scraper.broadcast()

main_thread()