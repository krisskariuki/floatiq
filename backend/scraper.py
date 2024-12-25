from selenium_imports import *
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
        headlessArgs=['--headless','--no-sandbox','--disable-gpu','--disable-dev-shm-usage',' --enable-unsafe-swiftshader']+headmodeArgs
        
        args=headmodeArgs
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

        def loop()->None:
            previousMutipliers=None
            dttm=None

            while True:
                latestMultipliers=self.driver.find_element(By.CLASS_NAME,'payouts-block').find_elements(By.CLASS_NAME,'bubble-multiplier')

                if previousMutipliers!=latestMultipliers:
                    previousMutipliers=latestMultipliers
                    multiplier=float(latestMultipliers[0].text.replace('x',''))
                    bets=self.driver.find_element(By.XPATH,'//*[@class="all-bets-block d-flex justify-content-between align-items-center px-2 pb-1"]').find_elements(By.XPATH,'.//div')[0].find_elements(By.XPATH,'.//div')[1].text

                    dttm=datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                    self.data={'time':dttm,'noise':multiplier,'bets':bets}

                    print(self.data)

                time.sleep(0.5)
        
        def apply_delay(function):
            time.sleep(action.delay)
            function()

        actionHashMap={
            'locate':locate,
            'click':click,
            'write':write,
            'send':send,
            'extract':extract,
            'loop':loop
            }
        
        return apply_delay(actionHashMap[action.action])

    
    def navigate(self,actions):
        self.driver.get(self.webUrl)

        for action in actions:
            self.action(action)