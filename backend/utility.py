from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException,StaleElementReferenceException,NoSuchWindowException,TimeoutException

class Utility:
    def __init__(self,webUrl:str,headless:bool)->None:
        self.webUrl=webUrl
        options=webdriver.ChromeOptions()
        service=Service(ChromeDriverManager().install())
        
        headmodeArgs=['--ignore-certificate-errors','--disable-notifications']
        headlessArgs=['--headless','--no-sandbox','--disable-gpu','--disable-dev-shm-usage',' --enable-unsafe-swiftshader']+headmodeArgs
        
        self.sleepTime=5 if headless else 10
        args=headlessArgs if headless else headmodeArgs
        
        for arg in args:
            options.add_argument(arg)
        options.add_experimental_option('detach',True)

        self.driver=webdriver.Chrome(service=service,options=options)

    def navigate(self):
        self.driver.get(self.webUrl)

        WebDriverWait(self.driver,10).until(By.XPATH,'//*[@name="q"]').send_keys('hello world'+Keys.RETURN)
        WebDriverWait(self.driver,10).until(By.XPATH,'//*[@class="YmvwI"]').click()


google=Utility('https://google.com')
google.navigate()