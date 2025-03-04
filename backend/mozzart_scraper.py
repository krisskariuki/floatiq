from scraper import Scraper
from dotenv import load_dotenv
import os
import argparse

load_dotenv()
PHONE=os.getenv('PHONE')
PASSWORD=os.getenv('PASSWORD')

parser=argparse.ArgumentParser(description='for controlling the bots configuration parameters')
parser.add_argument('--browse',action='store_false')
parser_arguments=parser.parse_args()

mozzart_scraper=Scraper(target_url='https://www.mozzartbet.co.ke/en#/casino',wait_time=30,headless=parser_arguments.browse)

mozzart_scraper.action(action='click',attribute='class="login-link mozzart_ke"',message='logging in...')
mozzart_scraper.action(action='write',attribute='placeholder="Mobile number"',message='writing phone input...',input_value=PHONE)
mozzart_scraper.action(action='send',attribute='placeholder="Password"',message='writing password input...',input_value=PASSWORD)
mozzart_scraper.action(action='click',attribute='alt="Aviator"',message='connecting to game engine...',sleep_time=1)

mozzart_scraper.manage_backup('db','mozzart-aviator')

mozzart_scraper.navigate(mozzart_scraper.watch_aviator)