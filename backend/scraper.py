from selenium_imports import *
from datetime import datetime
from colorama import Fore,init
from pathlib import Path
import pandas as pd
from flask import Flask,Response,jsonify
from flask_cors import CORS
import time
import sys
import os
import json
import threading

init(autoreset=True)
w=Fore.WHITE
r=Fore.RED
g=Fore.GREEN
y=Fore.YELLOW
c=Fore.CYAN
m=Fore.MAGENTA
b=Fore.LIGHTBLACK_EX


app=Flask(__name__)
CORS(app)
# consider implementing an action for callbacks so that custom & internal functions can be pushed to the actions_array. This might solve many blockades & complexities
class Scraper:
    def __init__(self,target_url:str,headless:bool=False,wait_time:int=10,retries:int=5)->None:

        self.target_url=target_url
        self.headless=headless
        self.wait_time=wait_time
        self.retries=retries

        self.record_lock=threading.Lock()
        self.series_lock=threading.Lock()
        
        self.round_id=0
        self.file_name=None
        self.folder_name='backup'
        self.base_file_name='file'
        self.record=None
        self.series=[]
        
        self.actions_array=[]
        self.start_driver()
        
    def start_driver(self):
        options=uc.ChromeOptions()
        width,height=800,1080

        headmode_args=['--ignore-certificate-errors','--disable-notifications']
        headless_args=['--headless','--no-sandbox','--disable-gpu','--disable-dev-shm-usage','--enable-unsafe-swiftshader',f'--window-size={width},{height}']+headmode_args
        
        args=headless_args if self.headless else headmode_args
        
        for arg in args:
            options.add_argument(arg)

        self.driver=uc.Chrome(options=options)
        self.driver.set_window_size(width,height)
        stealth(driver=self.driver,platform='Win32',fix_hairline=True)
    
    def restart_driver(self):
        try:
            self.driver.quit()
        except:
            pass
        time.sleep(1)
        self.start_driver()
    
    def manage_backup(self):
        os.makedirs(self.folder_name,exist_ok=True)

        if self.file_name is None:
            file_id=datetime.now().strftime('%Y%m%d_%H%M')
            self.file_name=f"{self.folder_name}/{self.base_file_name}_{file_id}.csv"

            if not os.path.exists(self.file_name):
                pd.DataFrame(columns=['self.round_id', 'multiplier', 'std_time', 'unix_time']).to_csv(self.file_name,index=False)
                print(f'{g}backup file initialized: {self.file_name}')

    def save_record(self):
        with self.record_lock:
            if self.record and isinstance(self.record,dict):
                pd.DataFrame([self.record]).to_csv(self.file_name,mode='a',index=False,header=False)

    def action(self,action='locate',attribute='',sleep_time=0,message='',input_value='',callback=None,args=[]):
        action={key:value for key,value in locals().items() if key!="self"}
        self.actions_array.append(action)
    
    def expose_data(self):      
        @app.route('/mozzart_aviator/latest',methods=['GET'])
        def get_latest():
            with self.record_lock:
                return jsonify(self.record)

        @app.route('/mozzart_aviator/history',methods=['GET'])
        def get_history():
            with self.series_lock:
                return jsonify(self.series)

        @app.route('/mozzart_aviator/stream',methods=['GET'])
        def stream_data():
            def event_stream():
                last_seen=None
                while True:
                    with self.record_lock:
                        if self.record and self.record!=last_seen:
                            last_seen=self.record.copy()
                            yield f"data:{json.dumps(last_seen,separators=(',',':'))}\n\n"
                    time.sleep(1)
            return Response(event_stream(),mimetype='text/event-stream')

        def run_app():
            app.run(host='0.0.0.0',port=8080,threaded=True)
        
        threading.Thread(target=run_app,daemon=True).start()
        
    def watch_aviator(self):
        old=None

        def check_for_new_data(recent):
            nonlocal old

            if old!=recent:
                    old=recent
                    self.round_id+=1
                    multiplier=float(recent[0].text.replace('x','').replace(',',''))
                    std_time=datetime.now().isoformat(sep=' ',timespec='seconds')
                    unix_time=int(datetime.now().timestamp())

                    data={'self.round_id':self.round_id,'multiplier':multiplier,'std_time':std_time,'unix_time':unix_time}
                    with self.record_lock,self.series_lock:
                        self.record=data
                        self.series.append(data)

                    if self.file_name:
                        self.save_record()

                    print(f'{b}{json.dumps(self.record,separators=(",",":"))}\n')
        def run_aviator():
            try:
                payouts_block=WebDriverWait(self.driver,self.wait_time).until(EC.presence_of_element_located((By.XPATH,'//*[@class="payouts-block"]')))
                if payouts_block:
                    print(f'{g}connected to game engine successfully')
                    self.manage_backup()

                while True:
                    try:
                        latest_multipliers=self.driver.find_element(By.CLASS_NAME,'payouts-block').find_elements(By.CLASS_NAME,'bubble-multiplier')
                        check_for_new_data(latest_multipliers)
                        time.sleep(1)
                    except:
                        raise
            except Exception as e:
                print(f'{r}game engine error!\n{y}{e}\n{c}restarting...')
                self.navigate()
            
        threading.Thread(target=run_aviator).start()

    def parse_action(self,action):
        def locate():
            element=WebDriverWait(self.driver,self.wait_time).until(EC.presence_of_element_located((By.XPATH,f'//*[@{action["attribute"]}]')))
            if element:
                print(f'{g}element located')
                return True
            else:
                print(f'{r}element not located')
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

        def callback():
            if callable(action['callback']):
                action['callback'](*(action['args']))
            else:
                raise TypeError("callback is not of type 'function'")

        def execute(function):
            time.sleep(action['sleep_time'])
            if action['message']:
                print(f'{c}{action["message"]}')
                
            function()

        action_table={
            'locate':locate,
            'click':click,
            'write':write,
            'send':send,
            'callback':callback
            }
        
        execute(action_table[action['action']])
    
    def navigate(self):
        while self.retries>0:
            try:
                self.driver.get(self.target_url)
                print(f'{c}navigating to {self.target_url}...')
                for action in self.actions_array:
                    try:
                        self.parse_action(action)

                    except Exception as e:
                        print(f'{y}navigation procedure error!\n{y}{e}\n')
                        raise

                print(f'{g}navigation procedure successful')
                return

            except:
                print(f'{b}[{self.retries}]\n{c}restarting...')
                self.retries-=1
                self.restart_driver()
        
        print(f'{r}max retries reached')
        sys.exit(1)