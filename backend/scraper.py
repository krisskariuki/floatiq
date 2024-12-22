from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException,StaleElementReferenceException,NoSuchWindowException,TimeoutException

from flask import Flask,Response
from flask_cors import CORS
from datetime import datetime
from colorama import Fore
import time
import pytz
import os
import json
import argparse

w=Fore.WHITE
b=Fore.BLUE
g=Fore.GREEN
r=Fore.RED
m=Fore.MAGENTA
c=Fore.CYAN

class Scraper:
    def __init__(self,url,credentials,headless:bool):
        options=webdriver.ChromeOptions()
        service=Service(ChromeDriverManager().install())
        
        headmodeArgs=['--ignore-certificate-errors','--disable-notifications']
        headlessArgs=['--headless','--no-sandbox','--disable-gpu','--disable-dev-shm-usage',' --enable-unsafe-swiftshader']+headmodeArgs
        
        sleepTime=5 if headless else 10
        args=headlessArgs if headless else headmodeArgs
        
        for arg in args:
            options.add_argument(arg)
        options.add_experimental_option('detach',True)

        self.driver=webdriver.Chrome(service=service,options=options)

        self.url=url
        self.phone=credentials[0]
        self.password=credentials[1]

        self.noise=''
        self.record={}
        self.series=[]
        self.sleepTime=sleepTime

        self.SOURCE()

    def EVENT(self,attr='xpath',value='',method='click',click=False,timeout=60):
        methods={'id':By.ID,'class':By.CLASS_NAME,'xpath':By.XPATH}
        getBy={'locate':EC.presence_of_element_located((methods[attr],value)),'click':EC.element_to_be_clickable((methods[attr],value))}

        result=WebDriverWait(self.driver,timeout).until(getBy[method]).click() if click else WebDriverWait(self.driver,timeout).until(getBy[method])

        return result
    
    def NAVIGATE(self):
        self.driver.get(self.url)
        print(f'{c}navigating to {self.url}...{w}')

        self.EVENT('xpath','//*[@class="mbet-icon active casino"]','click',True)
        print(f'{c}logging in...{w}')
        time.sleep(self.sleepTime)

        self.EVENT('class','login-link','click',True)
        time.sleep(self.sleepTime)

        self.driver.find_element(By.XPATH,'//*[@placeholder="Mobile number"]').send_keys(self.phone)
        self.driver.find_element(By.XPATH,'//*[@placeholder="Password"]').send_keys(self.password)

        self.EVENT('class','login-button','click',True)
        time.sleep(self.sleepTime)
        print(f'{c}connecting to game engine...{w}')

        self.EVENT('xpath','//*[@alt="Aviator"]','click',True)

    def SOURCE(self):
        self.NAVIGATE()
        time.sleep(self.sleepTime)

        if self.EVENT('class','payouts-block'):
            print(f'{g}process completed successfully{w}')


        previousArray=None
        dttm=None

        while True:
            multipliersBlock=self.EVENT('class','payouts-block','locate')
            latestArray=multipliersBlock.find_elements(By.CLASS_NAME,'bubble-multiplier')

            try:
                if previousArray!=latestArray:
                    previousArray=latestArray
                    noise=float(latestArray[0].text.replace('x',''))
                    dttm=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
                    self.noise=noise
                    self.record={'noise':noise,'time':dttm}
                    self.series.append(self.record)
                    
                    print(f'{c}{self.record}{w}')

            except (TimeoutException,StaleElementReferenceException,NoSuchWindowException,ValueError):
                if 'session deleted because of page crash' in str(e):
                    self.NAVIGATE()
                else:raise
            
            time.sleep(1)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description='used to determine in which mode - headless or browser to use in the scraping process')
    parser.add_argument(
        '--browse',
        action='store_false',
        help='use if you want a browser window to open'
    )
    args=parser.parse_args()

    Scraper('https://www.mozzartbet.co.ke/en#/',('0113294793','Chri570ph3r.'),args.browse)