from scraper import Scraper
from config import BETIKA_URL
from utils import main_thread
from credentials import BETIKA_KRISS_PHONE,BETIKA_KRISS_PASSWORD
import os
import argparse
import random

parser=argparse.ArgumentParser(description='for controlling the bots configuration parameters')
parser.add_argument('--headless',action='store_true')
parser.add_argument('--backup',action='store_true')
parser.add_argument('--phone',default=BETIKA_KRISS_PHONE)
parser.add_argument('--password',default=BETIKA_KRISS_PASSWORD)
parser_arguments=parser.parse_args()

scraper=Scraper(target_url=BETIKA_URL,wait_time=30,headless=parser_arguments.headless,backup=parser_arguments.backup,window_size=(1200,800))

scraper.folder_name='backup'
scraper.base_file_name='betika_aviator'

scraper.action(action='click',attribute='href="/en-ke/login?next=%2F"',message='logging in...')
scraper.action(action='write',attribute='type="text"',message='writing phone input...',input_value=parser_arguments.phone,sleep_time=random.uniform(2,5))
scraper.action(action='send',attribute='type="password"',message='writing password input...',input_value=parser_arguments.password)
scraper.action(action='click',attribute='class="session__form__button__container"')
scraper.action(action='click',attribute='href="/en-ke/aviator"',message='connecting to game engine...',sleep_time=random.uniform(2,5))
scraper.action(action='switch_to_iframe',attribute='id="aviator-iframe"')
scraper.action(action='callback',callback=scraper.watch_aviator)

scraper.navigate()
scraper.broadcast()

main_thread()   