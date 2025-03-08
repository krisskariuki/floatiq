from scraper import Scraper,main_thread
from dotenv import load_dotenv
import os
import argparse

load_dotenv()
PHONE=os.getenv('PHONE')
PASSWORD=os.getenv('PASSWORD')

parser=argparse.ArgumentParser(description='for controlling the bots configuration parameters')
parser.add_argument('--headless',action='store_true')
parser_arguments=parser.parse_args()

scraper=Scraper(target_url='https://www.mozzartbet.co.ke/en#/casino',wait_time=30,headless=parser_arguments.headless)

scraper.folder_name='db'
scraper.base_file_name='mozzart_aviator'

scraper.action(action='click',attribute='class="login-link mozzart_ke"',message='logging in...')
scraper.action(action='write',attribute='placeholder="Mobile number"',message='writing phone input...',input_value=PHONE)
scraper.action(action='send',attribute='placeholder="Password"',message='writing password input...',input_value=PASSWORD)
scraper.action(action='click',attribute='alt="Aviator"',message='connecting to game engine...',sleep_time=1)
scraper.action(action='callback',callback=scraper.watch_aviator)

scraper.navigate()
scraper.expose_data()

main_thread()