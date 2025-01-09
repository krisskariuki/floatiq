from selenium_imports import *
from datetime import datetime
import time
import threading

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
            element=WebDriverWait(self.driver,60).until(EC.presence_of_element_located((By.XPATH,f'//*[@{action.attribute}]')))
            if not element:
                print('no element with the provided attribute was found')
            
            print(f"element with the provided attribue was found : {element.get_attribute('outerHTML')}")
        
        def click()->None:
            WebDriverWait(self.driver,60).until(EC.element_to_be_clickable((By.XPATH,f'//*[@{action.attribute}]'))).click()
        
        def write()->None:
            self.driver.find_element(By.XPATH,f'//*[@{action.attribute}]').send_keys(action.inputValue)
        
        def send()->None:
            self.driver.find_element(By.XPATH,f'//*[@{action.attribute}]').send_keys(action.inputValue + Keys.RETURN)
        
        def extract()->None:
            print(self.driver.find_element(By.XPATH,f'//*[@{action.attribute}]').text)

        def custom()->None:
            threading.Thread(target=action.callback,args=({'driver':self.driver,'locator':By},)).start()

        def apply_delay(function):
            time.sleep(action.delay)
            function()

        actionHashMap={
            'locate':locate,
            'click':click,
            'write':write,
            'send':send,
            'extract':extract,
            'custom':custom
            }
        
        return apply_delay(actionHashMap[action.action])

    
    def navigate(self,actions):
        self.driver.get(self.webUrl)

        for action in actions:
            self.action(action)