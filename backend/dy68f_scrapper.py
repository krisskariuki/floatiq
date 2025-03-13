from scraper import Scraper
from config import DY68F_URL
from credentials import DY68F_EMAIL,DY68F_PASSWORD
import argparse

parser=argparse.ArgumentParser(description='for controlling the bots configuration parameters')
parser.add_argument('--headless',action='store_true')
parser_arguments=parser.parse_args()

dy68f_scrapper=Scraper(target_url=DY68F_URL,wait_time=30,headless=parser_arguments.headless)

dy68f_scrapper.action(action='write',attribute='type="text"',input_value=DY68F_EMAIL,message='writing phone input...')
dy68f_scrapper.action(action='send',attribute='type="password"',input_value=DY68F_PASSWORD,message='writing passwrod input...')
dy68f_scrapper.action(action='click',attribute='class="loginin btncolor"',message='going to homepage...')
dy68f_scrapper.action(action='click_from_list',attribute='class="list-item"',message='choosing game...')
dy68f_scrapper.action(action='click_from_list',attribute='class="btns"',message='selecting project...')
dy68f_scrapper.action(action='click',attribute='class="btns"',message='placing amount...')
dy68f_scrapper.action(action='click',attribute='class="confirms btncolor"',message='placing trade order...')


dy68f_scrapper.navigate()