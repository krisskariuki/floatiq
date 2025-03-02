from selenium_imports import *
from datetime import datetime
from colorama import Fore
from time import sleep
from dotenv import load_dotenv
from flask import Flask,Response,jsonify
from flask_cors import CORS
from pathlib import Path
import threading
import logging
import json
import random
import os
import argparse
import pandas as pd

load_dotenv()
PHONE=os.getenv('PHONE')
PASSWORD=os.getenv('PASSWORD')

w=Fore.WHITE
g=Fore.GREEN
y=Fore.YELLOW
c=Fore.CYAN
b=Fore.LIGHTBLACK_EX

logging.basicConfig(level=logging.INFO,format='%(message)s')
navigator_parser=argparse.ArgumentParser(description='for controlling the bots configuration parameters')
navigator_parser.add_argument('--browse',action='store_false')
navigator_arguments=navigator_parser.parse_args()

app=Flask(__name__)
CORS(app)

class Navigator:
    def __init__(self,credentials,headless=False):
        self.headless=headless
        self.url='https://www.mozzartbet.co.ke/en#/casino'
        self.phone=credentials[0]
        self.password=credentials[1]

        self.file_name=None
        self.record=None
        self.series=[]

        self.record_lock=threading.Lock()
        self.series_lock=threading.Lock()

        options=webdriver.ChromeOptions()
        service=Service(ChromeDriverManager().install())

        headmode_args=['--ingore-certificate-errors','--disable-notifications']
        healess_args=['--headless','--no-sandbox','--disable-gpu','--disable-dev-shm-usage','--enable-unsafe-swiftshader']+headmode_args

        args=healess_args if headless else headmode_args

        for arg in args:
            options.add_argument(arg)
        options.add_experimental_option('detach',True)
        
        self.driver=webdriver.Chrome(options=options,service=service)

    def manage_data_backup(self,folder_name='db',file_name='raw'):
        file_id=0

        while (os.path.exists(f'{folder_name}/{file_name}_{file_id}.csv')):
            file_id+=1

        file_to_check=f'{folder_name}/{file_name}_{file_id}.csv'

        directory=os.path.dirname(file_to_check)
        os.makedirs(directory,exist_ok=True)

        self.file_name=file_to_check

    def navigate_to_game(self):
        try:
            self.driver.get(self.url)
            logging.info(f'{c}navigating to {self.url}...{w}')

            login_link=WebDriverWait(self.driver,30).until(EC.element_to_be_clickable((By.XPATH,'//*[@class="login-link mozzart_ke"]')))
            logging.info(f'{c}logging in...{w}')
            login_link.click()

            phone_input=WebDriverWait(self.driver,30).until(EC.presence_of_element_located((By.XPATH,'//*[@placeholder="Mobile number"]')))
            logging.info(f'{c}writing phone input...{w}')
            phone_input.send_keys(self.phone)

            password_input=WebDriverWait(self.driver,30).until(EC.presence_of_element_located((By.XPATH,'//*[@placeholder="Password"]')))
            logging.info(f'{c}writing password input...{w}')
            password_input.send_keys(self.password + Keys.RETURN)

            game_button=WebDriverWait(self.driver,30).until(EC.element_to_be_clickable((By.XPATH,'//*[@alt="Aviator"]')))
            sleep(1)                                         
            game_button.click()
            logging.info(f'{c}navigating to game engine...{w}')

        except (AttributeError,WebDriverException,StaleElementReferenceException,NoSuchWindowException,TimeoutException) as e:

            if 'no such window' in str(e):
                self.driver.quit()
                logging.error(f'{y}navigation procedure error - no such window exception\n{c}Attempting to fix...{w}')
                self.__init__((self.phone,self.password),self.headless)
                self.navigate_to_game()

            self.driver.quit()
            logging.error(f'{y}navigation procedure error- {e}\n{c}Attempting to fix...{w}')
            self.__init__((self.phone,self.password),self.headless)
            self.navigate_to_game()

    def extract_data_from_game_engine(self):
        old=None
        round_id=0

        def check_for_new_data(recent):
            nonlocal old,round_id
            multiplier=0

            if old!=recent:
                    old=recent
                    round_id+=1
                    multiplier=float(recent[0].text.replace('x','').replace(',',''))
                    std_time=datetime.now().isoformat(sep=' ',timespec='seconds')
                    unix_time=int(datetime.now().timestamp())

                    data={'round_id':round_id,'multiplier':multiplier,'std_time':std_time,'unix_time':unix_time}
                    self.record=data
                    self.series.append(data)

                    pd.DataFrame([data]).to_csv(self.file_name, mode='a', index=False, header=not Path(self.file_name).exists())

                    print(f'{b}{self.record}{w}\n')
            
        try:
            payouts_block=WebDriverWait(self.driver,30).until(EC.presence_of_element_located((By.XPATH,'//*[@class="payouts-block"]')))
            if payouts_block:
                logging.info(f'{g}connected to game engine successfully\n\n{w}')

            while True:
                latest_multipliers=self.driver.find_element(By.CLASS_NAME,'payouts-block').find_elements(By.CLASS_NAME,'bubble-multiplier')
                check_for_new_data(latest_multipliers)
                sleep(0.1)

        except (AttributeError,TypeError,WebDriverException,StaleElementReferenceException,NoSuchWindowException,TimeoutException) as e:

            if 'no such window' in str(e):
                self.driver.quit()
                logging.error(f'{y}game engine error - no such window exception\n{c}Attempting to fix...{w}')
                self.__init__((self.phone,self.password),self.headless)
                self.start()

            self.driver.quit()
            logging.error(f'{y}game engine error - {e}\n{c}Attempting to fix...{w}')
            self.__init__((self.phone,self.password),self.headless)
            self.start()        
    
    def yield_data(self):
        local_record=None
        
        while True:
            with self.record_lock:
                current_record=self.record
            
            if local_record!=current_record:
                local_record=current_record
            
            else:
                multiplier=round(random.uniform(-0.50,0.50),2)
                std_time=datetime.now().isoformat(sep=' ',timespec='seconds')
                unix_time=int(datetime.now().timestamp())
                self.record={'multiplier':multiplier,'std_time':std_time,'unix_time':unix_time}
            
            sleep(0.5)

    def expose(self):
        @app.route('/raw/stream')
        def stream():
            def streamer():
                local_record=None
                while True:
                    if self.record!=local_record:
                        local_record=self.record
                        yield f"data: {json.dumps(self.record,separators=(',',':'))}\n\n"
                    sleep(0.1)
                
            return Response(streamer(),content_type='text/event-stream')

        @app.route('/raw/latest')
        def latest():
            return self.record

        @app.route('/raw/series')
        def history():
            return jsonify(self.series)
        
        app.run(threaded=True,host='0.0.0.0',port=8080)
    
    def start(self):
        source_thread=threading.Thread(target=self.extract_data_from_game_engine)
        yielder_thread=threading.Thread(target=self.yield_data,daemon=True)
        expose_thread=threading.Thread(target=self.expose,daemon=True)

        self.manage_data_backup()
        self.navigate_to_game()

        source_thread.start()
        yielder_thread.start()
        expose_thread.start()

mozzartGame=Navigator((PHONE,PASSWORD),navigator_arguments.browse)
mozzartGame.start()