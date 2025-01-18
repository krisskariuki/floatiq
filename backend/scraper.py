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

class Action:
    def __init__(self,action:str='locate',attribute:str='',delay:int=5,inputValue:str=None,callback=None)->None:
        self.action=action
        self.attribute=attribute
        self.delay=delay
        self.inputValue=inputValue
        self.callback=callback

class Navigator:
    def __init__(self,webUrl:str,headless:bool=False)->None:
        self.webUrl=webUrl
        self.data=None
        options=webdriver.ChromeOptions()
        service=Service(ChromeDriverManager().install())
        
        headmodeArgs=['--ignore-certificate-errors','--disable-notifications']
        headlessArgs=['--headless','--no-sandbox','--disable-gpu','--disable-dev-shm-usage',' --enable-unsafe-swiftshader']+headmodeArgs
        
        args=headlessArgs if headless else headmodeArgs
        
        for arg in args:
            options.add_argument(arg)
        options.add_experimental_option('detach',True)

        self.driver=webdriver.Chrome(service=service,options=options)
                
    def action(self,action):                
        def locate():
            state=False
            element=WebDriverWait(self.driver,60).until(EC.presence_of_element_located((By.XPATH,f'//*[@{action.attribute}]')))

            if element:
                state=True
                print(f'{g}{self.driver.title}{w}')

            else :
                print('unable to locate element')

            return state
        
        def click()->None:
            state=False
            element=WebDriverWait(self.driver,60).until(EC.element_to_be_clickable((By.XPATH,f'//*[@{action.attribute}]')))

            if element:
                state=True
                element.click()

            return state
        
        def write()->None:
            state=False
            element=WebDriverWait(self.driver,60).until(EC.presence_of_element_located((By.XPATH,f'//*[@{action.attribute}]')))

            if element:
                state=True
                element.send_keys(action.inputValue)

            return state
        
        def send()->None:
            state=False
            element=WebDriverWait(self.driver,60).until(EC.presence_of_element_located((By.XPATH,f'//*[@{action.attribute}]')))
            
            if element:
                state=True
                element.send_keys(action.inputValue+Keys.RETURN)

            return state

        def custom()->None:
            try:
                state=False
                element=WebDriverWait(self.driver,60).until(EC.presence_of_element_located((By.XPATH,f'//*[@{action.attribute}]')))

                if element:
                    state=True
                return state
            
            finally:
                threading.Thread(target=action.callback,args=({'driver':self.driver,'locator':By},)).start()

        def apply_delay(function):
            # while action.delay > 0:
            #     if function():
            #         break
            #     action.delay-=1
                time.sleep(action.delay)
                function()

        actionHashMap={
            'locate':locate,
            'click':click,
            'write':write,
            'send':send,
            'custom':custom
            }
        
        return apply_delay(actionHashMap[action.action])

    
    def navigate(self,actions):
        self.driver.get(self.webUrl)

        for action in actions:
            self.action(action)