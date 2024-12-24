from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException,StaleElementReferenceException,NoSuchWindowException,TimeoutException

from datetime import datetime
import time

class Action:
    def __init__(self,action:str='locate',attribute:str='',delay:int=5,inputValue:str=None)->None:
        self.action=action
        self.attribute=attribute
        self.delay=delay
        self.inputValue=inputValue

class Navigator:
    def __init__(self,webUrl:str,headless:bool=False)->None:
        self.webUrl=webUrl
        self.data=None
        options=webdriver.ChromeOptions()
        service=Service(ChromeDriverManager().install())
        
        headmodeArgs=['--ignore-certificate-errors','--disable-notifications']
        # headlessArgs=['--headless','--no-sandbox','--disable-gpu','--disable-dev-shm-usage',' --enable-unsafe-swiftshader']+headmodeArgs
        
        args=headmodeArgs
        # args=headlessArgs if headless else headmodeArgs
        
        for arg in args:
            options.add_argument(arg)
        options.add_experimental_option('detach',True)

        self.driver=webdriver.Chrome(service=service,options=options)

    def action(self,action):
        
        def locate():
            time.sleep(action.delay)
            if not WebDriverWait(self.driver,60).until(EC.presence_of_element_located((By.XPATH,f'//*[@{action.attribute}]'))):
                return "unable to locate an element with the provided attribute"
            return True
        
        def click()->None:
            time.sleep(action.delay)
            WebDriverWait(self.driver,60).until(EC.element_to_be_clickable((By.XPATH,f'//*[@{action.attribute}]'))).click()
        
        def write()->None:
            time.sleep(action.delay)
            self.driver.find_element(By.XPATH,f'//*[@{action.attribute}]').send_keys(action.inputValue)
        
        def send()->None:
            time.sleep(action.delay)
            self.driver.find_element(By.XPATH,f'//*[@{action.attribute}]').send_keys(action.inputValue + Keys.RETURN)
        
        def extract()->None:
            time.sleep(action.delay)
            print(self.driver.find_element(By.XPATH,f'//*[@{action.attribute}]').text)

        def loop()->None:
            time.sleep(action.delay)
            previousValues=None
            dttm=None

            while True:
                latestValues=self.driver.find_element(By.CLASS_NAME,'payouts-block').find_elements(By.CLASS_NAME,'bubble-multiplier')

                if previousValues!=latestValues:
                    previousValues=latestValues
                    noise=float(latestValues[0].text.replace('x',''))
                    dttm=datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                    self.data={'noise':noise,'time':dttm}

                    print(self.data)

                time.sleep(0.5)
        
        actionHashMap={
            'locate':locate,
            'click':click,
            'write':write,
            'send':send,
            'extract':extract,
            'loop':loop
            }
        
        return actionHashMap[action.action]()

    
    def navigate(self,actions):
        self.driver.get(self.webUrl)

        for action in actions:
            self.action(action)