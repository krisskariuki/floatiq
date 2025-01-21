from selenium_imports import *
from datetime import datetime
from colorama import Fore
import threading
import logging
import json
import time
import os

w=Fore.WHITE
g=Fore.GREEN
y=Fore.YELLOW
c=Fore.CYAN
m=Fore.MAGENTA

class Navigator:
    def __init__(self,credentials,targetUrl,headless=False):
        self.url=targetUrl
        self.phone=credentials[0]
        self.password=credentials[1]

        self.balance=0
        self.stake=1

        self.fileName=None
        self.target_multiplier=2.0
        self.target_multiplier_rtp=0
        self.selection_multipliers_rtps=[]
        self.selection_multipliers=[1.2,1.5,1.75,2.0,2.25,2.5,3.0,3.5,4.0,5.0,6.0,7.0,8.0,9.0,10.0]
        self.record={}
        self.series=[]

        options=webdriver.ChromeOptions()
        service=Service(ChromeDriverManager().install())

        headModeArgs=['--ingore-certificate-errors','--disable-notifications']
        headlessArgs=['--headless','--no-sandbox','--disable-gpu','--disable-dev-shm-usage','--enable-unsafe-swiftshader']

        args=headlessArgs if headless else headModeArgs

        for arg in args:
            options.add_argument(arg)
        options.add_experimental_option('detach',True)
        
        self.driver=webdriver.Chrome(options=options,service=service)

        logging.basicConfig(level=logging.INFO,format='%(asctime)s | %(levelname)s | %(message)s',datefmt='%Y-%m-%d %H:%M:%S')

    def manage_data_backup(self,fileName):
        file_id=1
        if os.path.exists(f'raw_data/{fileName}.json'):
            self.fileName=f'raw_data/{fileName}_{file_id}.json'
            file_id+=1

        else:
            self.fileName=f'raw_data/{fileName}.json'
        
    def predict_multiplier(self,multiplier_choices,multipliers_array):
        rtp=0
        rtp_series=[]

        if len(multipliers_array) > 0:
            for target_multiplier in multiplier_choices:
                count=sum(1 for num in multipliers_array if num > target_multiplier)

                probability=round((count/len(multipliers_array)),2)
                rtp=target_multiplier*probability

                rtp_series.append(round(rtp,2))
                self.selection_multipliers_rtps.append([target_multiplier,round(rtp,4)])

                selected_rtp_index=rtp_series.index(max(rtp_series))
                self.target_multiplier=multiplier_choices[selected_rtp_index]
                self.target_multiplier_rtp=rtp_series[selected_rtp_index]

    def execute_trade(self,outcome_multiplier,predicted_multiplier):
        if outcome_multiplier > predicted_multiplier:
            self.balance+=(self.stake*predicted_multiplier)-self.stake
        else:
            self.balance-=self.stake

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
            time.sleep(1)                                         
            gameButton.click()
            logging.info(f'{c}navigating to game engine...{w}')

        except (AttributeError,WebDriverException,StaleElementReferenceException,NoSuchWindowException,TimeoutException) as e:

            if 'no such window' in str(e):
                self.driver.quit()
                logging.error(f'{y}navigation procedure error - no such window exception\n{c}Attempting to fix...{w}')
                self.__init__((self.phone,self.password),self.url)
                self.navigate_to_game()

            self.driver.quit()
            logging.error(f'{y}navigation procedure error- {e}\n{c}Attempting to fix...{w}')
            self.__init__((self.phone,self.password),self.url)
            self.navigate_to_game()


    def source(self):
        previousMutipliers=None     
        round_id=1
        sliding_window=22
        std_dttm=None
        multiplier=0
        bets=0
        probability=0
        payout=0
        RTP=0

               
        payoutsBlock=WebDriverWait(self.driver,30).until(EC.presence_of_element_located((By.XPATH,'//*[@class="payouts-block"]')))
        if payoutsBlock:
            logging.info(f'{g}connected to game engine successfully{w}')

        try:
            while True:
                latestMultipliers=self.driver.find_element(By.CLASS_NAME,'payouts-block').find_elements(By.CLASS_NAME,'bubble-multiplier')

                if previousMutipliers!=latestMultipliers:
                    previousMutipliers=latestMultipliers
                    multiplier=float(latestMultipliers[0].text.replace('x',''))
                    bets=int(self.driver.find_element(By.XPATH,'//*[@class="all-bets-block d-flex justify-content-between align-items-center px-2 pb-1"]').find_elements(By.XPATH,'.//div')[0].find_elements(By.XPATH,'.//div')[1].text)

                    std_dttm=datetime.now().isoformat(sep=' ',timespec='seconds')

                    multiplier_series=[item['multiplier'] for item in self.series][-sliding_window:]
                    occurences=sum(1 for num in multiplier_series if num > multiplier)

                    if len(multiplier_series)>0:
                        probability=occurences/len(multiplier_series)
                        payout=bets*multiplier*probability
                        RTP=multiplier*probability

                        self.execute_trade(multiplier,self.target_multiplier)
                        self.predict_multiplier(self.selection_multipliers,multiplier_series)



                    data={'id':round_id,'std_time':std_dttm,'multiplier':multiplier,'probability':round(probability,6),'bets':bets,'payout':round(payout,2),'multiplier_rtp':round(RTP,2),'next_multiplier':self.target_multiplier,'next_multiplier_rtp':round(self.target_multiplier_rtp,2),'balance':round(self.balance,2)}

                    self.record=json.dumps(data,separators=(',',':'))
                    self.series.append(data)

                    with open(self.fileName,'w') as file:
                        fileSeries=json.dumps(self.series,indent=True,separators=(',',':'))
                        file.write(fileSeries)

                    print(f'{w}{data}\n{w}')
                    round_id+=1
                    self.selection_rtps=[]

                time.sleep(0.1)

        except (AttributeError,TypeError,WebDriverException,StaleElementReferenceException,NoSuchWindowException,TimeoutException) as e:

            if 'no such window' in str(e):
                self.driver.quit()
                logging.error(f'{y}game engine error - no such window exception\n{c}Attempting to fix...{w}')
                self.__init__((self.phone,self.password),self.url)
                self.start()

            self.driver.quit()
            logging.error(f'{y}game engine error - {e}\n{c}Attempting to fix...{w}')
            self.__init__((self.phone,self.password),self.url)
            self.start()        
    
    def start(self):
        source_thread=threading.Thread(target=self.source)
        self.navigate_to_game()
        self.manage_data_backup('raw_data')
        source_thread.start()

mozzartGame=Navigator(('0113294793','Chri570ph3r.'),'https://www.mozzartbet.co.ke/en#/casino')
mozzartGame.start()