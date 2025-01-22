from selenium_imports import *
from datetime import datetime
from colorama import Fore
import threading
import logging
import json
import time
import os
import argparse

w=Fore.WHITE
g=Fore.GREEN
y=Fore.YELLOW
c=Fore.CYAN
m=Fore.MAGENTA

logging.basicConfig(level=logging.INFO,format='%(asctime)s  %(levelname)s  %(message)s',datefmt='%Y-%m-%d %H:%M:%S')

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

    def manage_data_backup(self,fileName='raw_data'):
        file_id=1
        folderName='raw_data'

        if os.path.exists(f'{folderName}/{fileName}.json'):
            self.fileName=f'{folderName}/{fileName}_{file_id}.json'
            file_id+=1

        else:
            self.fileName=f'{folderName}/{fileName}.json'
        
    def navigate_to_game(self):

        try:
            self.driver.get(self.url)
            logging.info(self.driver.get_window_size())
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
            time.sleep(1)                                         
            gameButton.click()
            logging.info(f'{c}navigating to game engine...{w}')

        except (AttributeError,WebDriverException,StaleElementReferenceException,NoSuchWindowException,TimeoutException) as e:

            if 'no such window' in str(e):
                self.driver.quit()
                logging.error(f'{y}navigation procedure error - no such window exception\n{c}Attempting to fix...{w}')
                self.__init__((self.phone,self.password),self.url,self.headless)
                self.navigate_to_game()

            self.driver.quit()
            logging.error(f'{y}navigation procedure error- {e}\n{c}Attempting to fix...{w}')
            self.__init__((self.phone,self.password),self.url,self.headless)
            self.navigate_to_game()

    def extract_data_from_game_engine(self):
        previousMutipliers=None     
        round_id=1
        dttm=None
        multiplier=0
        bets=0
               
        payoutsBlock=WebDriverWait(self.driver,30).until(EC.presence_of_element_located((By.XPATH,'//*[@class="payouts-block"]')))
        if payoutsBlock:
            logging.info(f'{g}connected to game engine successfully\n\n{w}')

        try:
            while True:
                latestMultipliers=self.driver.find_element(By.CLASS_NAME,'payouts-block').find_elements(By.CLASS_NAME,'bubble-multiplier')

                if previousMutipliers!=latestMultipliers:
                    previousMutipliers=latestMultipliers
                    multiplier=float(latestMultipliers[0].text.replace('x',''))
                    bets=int(self.driver.find_element(By.XPATH,'//*[@class="all-bets-block d-flex justify-content-between align-items-center px-2 pb-1"]').find_elements(By.XPATH,'.//div')[0].find_elements(By.XPATH,'.//div')[1].text)

                    dttm=datetime.now().isoformat(sep=' ',timespec='seconds')
                    data={'id':round_id,'dttm':dttm,'multiplier':multiplier,'bets':bets}
                    self.record=json.dumps(data,separators=(',',':'))
                    self.series.append(data)

                    with open(self.fileName,'w') as file:
                        fileSeries=json.dumps(self.series,indent=True,separators=(',',':'))
                        file.write(fileSeries)

                    print(f'{c}{self.record}{w}')
                    round_id+=1

                time.sleep(0.1)

        except (AttributeError,TypeError,WebDriverException,StaleElementReferenceException,NoSuchWindowException,TimeoutException) as e:

            if 'no such window' in str(e):
                self.driver.quit()
                logging.error(f'{y}game engine error - no such window exception\n{c}Attempting to fix...{w}')
                self.__init__((self.phone,self.password),self.url,self.headless)
                self.start()

            self.driver.quit()
            logging.error(f'{y}game engine error - {e}\n{c}Attempting to fix...{w}')
            self.__init__((self.phone,self.password),self.url,self.headless)
            self.start()        
    
    def start(self):
        source_thread=threading.Thread(target=self.extract_data_from_game_engine)
        self.navigate_to_game()
        self.manage_data_backup(fileName='raw_data')
        source_thread.start()

mozzartGame=Navigator(('0113294793','Chri570ph3r.'),navigator_arguments.browse)
mozzartGame.start()