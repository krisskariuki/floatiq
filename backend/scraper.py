from selenium_imports import *
from datetime import datetime
from colorama import Fore
import time
import threading

w=Fore.WHITE
r=Fore.RED
g=Fore.GREEN
b=Fore.BLUE
y=Fore.YELLOW
c=Fore.CYAN
m=Fore.MAGENTA

class Scraper:
    def __init__(self,target_url:str,headless:bool=False)->None:
        self.target_url=target_url
        self.headless=headless
        self.wait_time=30
        self.record=None
        self.series=None
        self.actions_array=[]
        
        options=webdriver.ChromeOptions()
        service=Service(ChromeDriverManager().install())
        
        headmode_args=['--ignore-certificate-errors','--disable-notifications']
        headless_args=['--headless','--no-sandbox','--disable-gpu','--disable-dev-shm-usage','--enable-unsafe-swiftshader']+headmode_args
        
        args=headless_args if headless else headmode_args
        
        for arg in args:
            options.add_argument(arg)
        options.add_experimental_option('detach',True)

        self.driver=webdriver.Chrome(service=service,options=options)
    
    def action(self,action='locate',attribute='',sleep_time=0,message='',input_value=''):
        action={key:value for key,value in locals().items() if key!="self"}
        self.actions_array.append(action)
    
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
    
    def navigate(self):
        while True:
            try:
                self.driver.get(self.target_url)
                print(f'{c}navigating to {self.target_url}...{w}')
                for action in self.actions_array:
                    try:
                        self.parse(action)

                    except Exception as e:
                        print(f'{r}an error occured during navigation\n{w}')
                        raise
                    
                print(f'{g}all actions completed successfully{w}')

                break

            except Exception as e:
                print(f'{m}{e}\n{c}restarting...{w}')
                self.driver.quit()
                time.sleep(1)
                self.__init__(self.target_url,self.headless)