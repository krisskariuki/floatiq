from selenium_imports import *
from datetime import datetime
from colorama import Fore
from pathlib import Path
import pandas as pd
import time
import sys
import os

w=Fore.WHITE
r=Fore.RED
g=Fore.GREEN
y=Fore.YELLOW
c=Fore.CYAN
m=Fore.MAGENTA
b=Fore.LIGHTBLACK_EX

class Scraper:
    def __init__(self,target_url:str,headless:bool=False,wait_time:int=10)->None:

        self.target_url=target_url
        self.headless=headless
        self.wait_time=wait_time

        self.file_name=None
        self.record=None
        self.series=[]
        
        self.actions_array=[]
        self.chromedriver_path=ChromeDriverManager().install()
        self.start_driver()
        
    def start_driver(self):
        options=webdriver.ChromeOptions()
        service=Service(self.chromedriver_path)
        
        headmode_args=['--ignore-certificate-errors','--disable-notifications']
        headless_args=['--headless','--no-sandbox','--disable-gpu','--disable-dev-shm-usage','--enable-unsafe-swiftshader']+headmode_args
        
        args=headless_args if self.headless else headmode_args
        
        for arg in args:
            options.add_argument(arg)
        options.add_experimental_option('detach',True)

        self.driver=webdriver.Chrome(service=service,options=options)
    
    def restart_driver(self):
        try:
            self.driver.quit()
        except:
            pass
        time.sleep(1)
        self.start_driver()

    def manage_backup(self,folder_name='db',file_name='raw'):
        file_id=0

        while (os.path.exists(f'{folder_name}/{file_name}_{file_id}.csv')):
            file_id+=1

        file_to_check=f'{folder_name}/{file_name}_{file_id}.csv'

        directory=os.path.dirname(file_to_check)
        os.makedirs(directory,exist_ok=True)

        self.file_name=file_to_check

    def action(self,action='locate',attribute='',sleep_time=0,message='',input_value=''):
        action={key:value for key,value in locals().items() if key!="self"}
        self.actions_array.append(action)
    
    def watch(self):
        old,round_id,multiplier=None,0,0

        def check_for_new_data(recent):
            nonlocal old,round_id,multiplier

            if old!=recent:
                    old=recent
                    round_id+=1
                    multiplier=float(recent[0].text.replace('x','').replace(',',''))
                    std_time=datetime.now().isoformat(sep=' ',timespec='seconds')
                    unix_time=int(datetime.now().timestamp())

                    data={'round_id':round_id,'multiplier':multiplier,'std_time':std_time,'unix_time':unix_time}
                    self.record=data
                    self.series.append(data)
                    
                    # pd.DataFrame([data]).to_csv(self.file_name, mode='a', index=False, header=not Path(self.file_name).exists())

                    print(f'{b}{self.record}{w}\n')
        try:
            payouts_block=WebDriverWait(self.driver,self.wait_time).until(EC.presence_of_element_located((By.XPATH,'//*[@class="payouts-block"]')))
            if payouts_block:
                print(f'{g}connected to game engine successfully\n\n{w}')

            while True:
                latest_multipliers=self.driver.find_element(By.CLASS_NAME,'payouts-block').find_elements(By.CLASS_NAME,'bubble-multiplier')
                check_for_new_data(latest_multipliers)
                time.sleep(0.1)
        except Exception as e:
            print(f'{r}game engine error!\n{c}restarting...{w}')
            self.restart_driver()
                

    def parse(self,action):
        def locate():
            element=WebDriverWait(self.driver,self.wait_time).until(EC.presence_of_element_located((By.XPATH,f'//*[@{action["attribute"]}]')))
            if element:
                print(f'{g}element located{w}')
                return True
            else:
                print(f'{r}element not located{w}')
                return False
            
        def click():
            element=WebDriverWait(self.driver,self.wait_time).until(EC.element_to_be_clickable((By.XPATH,f'//*[@{action["attribute"]}]')))
            element.click()
        
        def write():
            element=WebDriverWait(self.driver,self.wait_time).until(EC.presence_of_element_located((By.XPATH,f'//*[@{action["attribute"]}]')))
            element.send_keys(action['input_value'])
        
        def send():
            element=WebDriverWait(self.driver,self.wait_time).until(EC.presence_of_element_located((By.XPATH,f'//*[@{action["attribute"]}]')))
            element.send_keys(action['input_value']+Keys.RETURN)

        
        def execute(function):
            time.sleep(action['sleep_time'])
            if action['message']:
                print(f'{c}{action["message"]}{w}')
                
            function()

        action_table={
            'locate':locate,
            'click':click,
            'write':write,
            'send':send
            }
        
        execute(action_table[action['action']])
    
    def navigate(self,callback='',retries=5):
        while retries>0:
            try:
                self.driver.get(self.target_url)
                print(f'{c}navigating to {self.target_url}...{w}')
                for action in self.actions_array:
                    try:
                        self.parse(action)

                    except Exception as e:
                        print(f'{y}navigation procedure error!\n{w}')
                        raise
                    
                if callable(callback):
                    callback()
                else:
                    print(f'{g}navigation procedure successful{w}')
                    return

            except Exception as e:
                print(f'{b}[{retries}]\n{c}restarting...{w}')
                retries-=1
                self.restart_driver()
        
        print(f'{r}max retries reached{w}')
        sys.exit(1)