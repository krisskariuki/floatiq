from selenium_imports import *
from datetime import datetime
from colorama import Fore
import time
import threading
import json
import os

w=Fore.WHITE
r=Fore.RED
g=Fore.GREEN
b=Fore.BLUE
y=Fore.YELLOW
c=Fore.CYAN
m=Fore.MAGENTA

class Navigator:
    def __init__(self,credentials,targetUrl,headless=False):
        self.url=targetUrl
        self.phone=credentials[0]
        self.password=credentials[1]

        self.fileName=None
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
        self.driver.get(self.url)

    def manage_data_backup(self,fileName):
        file_id=1
        if os.path.exists(f'raw_data/{fileName}.json'):
            self.fileName=f'raw_data/{fileName}_{file_id}.json'
            file_id+=1

        else:
            self.fileName=f'raw_data/{fileName}.json'
        

    def navigate_to_game(self):
        print(f'{c}navigating to {self.url}...{w}')

        loginLink=WebDriverWait(self.driver,30).until(EC.element_to_be_clickable((By.XPATH,'//*[@class="login-link mozzart_ke"]')))
        print(f'{c}logging in...{w}')
        loginLink.click()


        phoneInput=WebDriverWait(self.driver,30).until(EC.presence_of_element_located((By.XPATH,'//*[@placeholder="Mobile number"]')))
        print(f'{c}writing phone input...{w}')
        phoneInput.send_keys(self.phone)

        passwordInput=WebDriverWait(self.driver,30).until(EC.presence_of_element_located((By.XPATH,'//*[@placeholder="Password"]')))
        print(f'{c}writing password input...{w}')
        passwordInput.send_keys(self.password + Keys.RETURN)

        gameButton=WebDriverWait(self.driver,30).until(EC.element_to_be_clickable((By.XPATH,'//*[@alt="Aviator"]')))
        time.sleep(1)                                         
        gameButton.click()
        print(f'{c}navigating to game engine...{w}')

    
    def start(self):
        try:
            self.navigate_to_game()

        except (WebDriverException,StaleElementReferenceException,NoSuchWindowException,TimeoutException) as e:
            print(f'{y} an error occured.Attempting to fix... {w}')
            self.navigate_to_game()

        payoutsBlock=WebDriverWait(self.driver,30).until(EC.presence_of_element_located((By.XPATH,'//*[@class="payouts-block"]')))
        if payoutsBlock:
            print(f'{g}connected to game engine successfully{w}')
        
        previousMutipliers=None     
        round_id=1
        std_dttm=None
        unix_dttm=None
        multiplier=None
        bets=None
        probability=None
        payout=None
        RTP=None

        multiplier_series=[]

        self.manage_data_backup('raw_data')

        try:
            while True:
                latestMultipliers=self.driver.find_element(By.CLASS_NAME,'payouts-block').find_elements(By.CLASS_NAME,'bubble-multiplier')

                if previousMutipliers!=latestMultipliers:
                    previousMutipliers=latestMultipliers
                    multiplier=float(latestMultipliers[0].text.replace('x',''))
                    bets=int(self.driver.find_element(By.XPATH,'//*[@class="all-bets-block d-flex justify-content-between align-items-center px-2 pb-1"]').find_elements(By.XPATH,'.//div')[0].find_elements(By.XPATH,'.//div')[1].text)

                    std_dttm=datetime.now().isoformat(sep=' ',timespec='seconds')
                    unix_dttm=datetime.now().timestamp()

                    multiplier_series=[item['multiplier'] for item in self.series]
                    occurences=sum(1 for num in multiplier_series if num > multiplier)

                    if len(multiplier_series)>0:
                        probability=round((occurences/len(multiplier_series)),2)
                        payout=round((bets*multiplier*probability),2)
                        RTP=round((multiplier*probability),2)
                    

                    data={'id':round_id,'std_time':std_dttm,'multiplier':multiplier,'probability':probability,'bets':bets,'payout':payout,'rtp':RTP,'unix_time':unix_dttm}

                    self.record=json.dumps(data,separators=(',',':'))

                    self.series.append(data)

                    with open(self.fileName,'w') as file:
                        fileSeries=json.dumps(self.series,indent=True,separators=(',',':'))
                        file.write(fileSeries)

                    print(f'{w}{data}\n{w}')
                    round_id+=1
                time.sleep(0.1)

        except (WebDriverException,StaleElementReferenceException,NoSuchWindowException,TimeoutException) as e:
            print(f'{y} an error occured.Attempting to fix... {w}')
            self.navigate_to_game()

mozzartGame=Navigator(('0113294793','Chri570ph3r.'),'https://www.mozzartbet.co.ke/en#/casino')
mozzartGame.start()