from selenium_imports import *
from datetime import datetime
from colorama import Fore
from time import sleep
from dotenv import load_dotenv
import threading
import logging
import json
import os
import argparse
import pandas as pd

load_dotenv()
PHONE=os.getenv(PHONE)
PASSWORD=os.getenv(PASSWORD)

w=Fore.WHITE
g=Fore.GREEN
y=Fore.YELLOW
c=Fore.CYAN
b=Fore.LIGHTBLACK_EX

logging.basicConfig(level=logging.INFO,format='%(message)s')
navigator_parser=argparse.ArgumentParser(description='for controlling the bots configuration parameters')
navigator_parser.add_argument('--browse',action='store_false')
navigator_arguments=navigator_parser.parse_args()

class Navigator:
    def __init__(self,credentials,headless=False):
        self.headless=headless
        self.url='https://www.mozzartbet.co.ke/en#/casino'
        self.phone=credentials[0]
        self.password=credentials[1]

        self.fileName=None
        self.record={}
        self.series=[]

        options=webdriver.ChromeOptions()
        service=Service(ChromeDriverManager().install())

        headModeArgs=['--ingore-certificate-errors','--disable-notifications']
        headlessArgs=['--headless','--no-sandbox','--disable-gpu','--disable-dev-shm-usage','--enable-unsafe-swiftshader']+headModeArgs

        args=headlessArgs if headless else headModeArgs

        for arg in args:
            options.add_argument(arg)
        options.add_experimental_option('detach',True)
        
        self.driver=webdriver.Chrome(options=options,service=service)

    def manage_data_backup(self,fileName='raw_data',formats=['json','csv']):
        file_id=0
        folderName='raw'

        file_id+=1 if (os.path.exists(f'{folderName}/{format}/{fileName}_{file_id}.{format}') for format in formats) else file_id

        for format in formats:
            file_to_check=f'{folderName}/{format}/{fileName}_{file_id}.{format}'

            directory=os.path.dirname(file_to_check)
            os.makedirs(directory,exist_ok=True)

            self.fileName=file_to_check
            
            if format=='json':
                with open(self.fileName,'w') as file:
                    json.dump(self.series,file,indent=True,separators=(',',':'))

            elif format=='csv':
                df=pd.DataFrame(self.series)
                df.to_csv(self.fileName,index=False)

    def navigate_to_game(self):
        try:
            self.driver.get(self.url)
            logging.info(f'{c}navigating to {self.url}...{w}')

            loginLink=WebDriverWait(self.driver,30).until(EC.element_to_be_clickable((By.XPATH,'//*[@class="login-link mozzart_ke"]')))
            logging.info(f'{c}logging in...{w}')
            loginLink.click()

            phoneInput=WebDriverWait(self.driver,30).until(EC.presence_of_element_located((By.XPATH,'//*[@placeholder="Mobile number"]')))
            logging.info(f'{c}writing phone input...{w}')
            phoneInput.send_keys(self.phone)

            passwordInput=WebDriverWait(self.driver,30).until(EC.presence_of_element_located((By.XPATH,'//*[@placeholder="Password"]')))
            logging.info(f'{c}writing password input...{w}')
            passwordInput.send_keys(self.password + Keys.RETURN)

            gameButton=WebDriverWait(self.driver,30).until(EC.element_to_be_clickable((By.XPATH,'//*[@alt="Aviator"]')))
            sleep(1)                                         
            gameButton.click()
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
        def check_for_new_data(recent):
            nonlocal old
            timestamp=None
            multiplier=0
            bets=0

            if old!=recent:
                    old=recent
                    multiplier=float(recent[0].text.replace('x',''))
                    bets=int(self.driver.find_element(By.XPATH,'//*[@class="all-bets-block d-flex justify-content-between align-items-center px-2 pb-1"]').find_elements(By.XPATH,'.//div')[0].find_elements(By.XPATH,'.//div')[1].text)

                    timestamp=datetime.now().isoformat(sep=' ',timespec='seconds')
                    data={'multiplier':multiplier,'bets':bets,'timestamp':timestamp}
                    self.record=json.dumps(data,separators=(',',':'))
                    self.series.append(data)

                    print(f'{b}{self.record}{w}\n')
                    self.manage_data_backup('raw',['json','csv'])
            
        try:
            payoutsBlock=WebDriverWait(self.driver,30).until(EC.presence_of_element_located((By.XPATH,'//*[@class="payouts-block"]')))
            if payoutsBlock:
                logging.info(f'{g}connected to game engine successfully\n\n{w}')

            while True:
                latestMultipliers=self.driver.find_element(By.CLASS_NAME,'payouts-block').find_elements(By.CLASS_NAME,'bubble-multiplier')
                check_for_new_data(latestMultipliers)
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
    
    def start(self):
        source_thread=threading.Thread(target=self.extract_data_from_game_engine)
        self.navigate_to_game()
        source_thread.start()

mozzartGame=Navigator((PHONE,PASSWORD),navigator_arguments.browse)
mozzartGame.start()