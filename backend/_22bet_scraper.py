from scraper import Scraper
from config import BET22_URL
from utils import main_thread
from credentials import BET22_KRISS_PHONE,BET22_KRISS_PASSWORD
import os
import argparse

parser=argparse.ArgumentParser(description='for controlling the bots configuration parameters')
parser.add_argument('--headless',action='store_true')
parser.add_argument('--backup',action='store_true')
parser_arguments=parser.parse_args()

scraper=Scraper(target_url=BET22_URL,wait_time=30,headless=parser_arguments.headless,backup=parser_arguments.backup,window_size=(1200,800))

scraper.folder_name='backup'
scraper.base_file_name='betika_aviator'

scraper.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
scraper.action(action='click',attribute='id="curLoginForm"',message='logging in...')
scraper.action(action='write',attribute='placeholder=" 712 123456"',message='writing phone input...',input_value=BET22_KRISS_PHONE,sleep_time=3.20)
scraper.action(action='send',attribute='placeholder="Password"',message='writing password input...',input_value=BET22_KRISS_PASSWORD)
scraper.action(action='click',attribute='class="enter_button_main"')
scraper.action(action='click',attribute='href="/othergames?product=849&game=68089"',message='connecting to game engine...',sleep_time=1.03)
scraper.action(action='switch_to_iframe',attribute='id="game_place_game"')
scraper.action(action='callback',callback=scraper.watch_aviator)

scraper.navigate()
scraper.broadcast()

main_thread()   