from selenium_imports import *
from datetime import datetime
import pandas as pd
from flask import Flask,Response,jsonify,request
from flask_cors import CORS
from queue import Queue
from waitress import serve
from config import PRODUCER_PORT
from utils import colors
import time
import sys
import os
import json
import threading

app=Flask(__name__)
CORS(app)

class Scraper:
    def __init__(self,target_url:str,headless:bool=False,backup:bool=False,wait_time:int=10,retries:int=5,window_size=(800,1080))->None:

        self.target_url=target_url
        self.headless=headless
        self.wait_time=wait_time
        self.retries=retries
        self.window_size=window_size

        self.lock=threading.Lock()

        self.active_trade=False
        self.target_multiplier=1.01
        self.bet_amount=5.00

        self.account_balance=0.00
        self.round_id=0
        self.file_name=None
        self.backup=backup
        self.folder_name='backup'
        self.base_file_name='file'
        self.record=None
        self.series=[]

        self.valid_accounts={
            'kriss_kariuki':'Chri570ph3r.'
        }
        self.clients=set()
        
        self.actions_array=[]
        self.start_driver()
        
    def start_driver(self):
        options=uc.ChromeOptions()
        width,height=self.window_size

        headmode_args=['--ignore-certificate-errors','--disable-notifications']
        headless_args = [
        "--headless=new",
        "--disable-dev-shm-usage",
        "--disable-background-networking",
        "--disable-renderer-backgrounding",
        "--disable-background-timer-throttling",
        "--disable-backgrounding-occluded-windows",
        "--disable-extensions",
        "--disable-popup-blocking",
        ] + headmode_args
        
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
                print(f'{colors.green}backup file initialized: {self.file_name}')

    def save_record(self):
        with self.lock:
            if self.record and isinstance(self.record,dict):
                pd.DataFrame([self.record]).to_csv(self.file_name,mode='a',index=False,header=False)

    def action(self,action='locate',attribute='',sleep_time=0,message='',input_value='',callback=None,choice_index=0,args=[]):
        action={key:value for key,value in locals().items() if key!="self"}
        self.actions_array.append(action)
    
    def broadcast(self):      
        @app.route('/producer/aviator/latest',methods=['GET'])
        def get_latest():
            with self.lock:
                return jsonify(self.record)

        @app.route('/producer/aviator/history',methods=['GET'])
        def get_history():
            with self.lock:
                return jsonify(self.series)

        @app.route('/producer/aviator/stream',methods=['GET'])
        def stream_data():
            def event_stream():
                queue=Queue()
                self.clients.add(queue)

                with self.lock:
                    if self.record:
                        yield f"data:{json.dumps(self.record,separators=(',',':'))}\n\n"
                
                while True:
                    record=queue.get()
                    yield f"data:{json.dumps(record,separators=(',',':'))}\n\n"
                    time.sleep(1)

            return Response(event_stream(),mimetype='text/event-stream')
        
        @app.route('/producer/account/stream')
        def stream_account():
            local_balance=None

            def event_stream():
                nonlocal local_balance
                while True:
                    if local_balance!=self.account_balance:
                        local_balance=self.account_balance

                        yield f"data:{json.dumps(local_balance,separators=(',',':'))}\n\n"

                    time.sleep(1)

            return Response(event_stream(),mimetype='text/event-stream')


        @app.route('/producer/account/trade',methods=['POST'])
        def toggle_active_trade():
            req=request.get_json()

            bet_amount=req['bet_amount']
            multiplier=req['multiplier']
            active_trade=req['active_trade']

            with self.lock:
                self.active_trade=active_trade
                self.target_multiplier=multiplier
                self.bet_amount=bet_amount

            return 'trade placed successfully'


        def start_server():
            serve(app,host='0.0.0.0',port=PRODUCER_PORT,channel_timeout=300,threads=50,backlog=1000,connection_limit=500)
        
        threading.Thread(target=start_server,daemon=True).start()
        
    def watch_aviator(self):
        old_multiplier,old_balance=None,None

        def track_multiplier(recent_multiplier):
            nonlocal old_multiplier

            if old_multiplier!=recent_multiplier:
                    old_multiplier=recent_multiplier
                    self.round_id+=1
                    multiplier=float(recent_multiplier[0].text.replace('x','').replace(',',''))
                    std_time=datetime.now().isoformat(sep=' ',timespec='seconds')
                    unix_time=int(datetime.now().timestamp())

                    data={'round_id':self.round_id,'multiplier':multiplier,'std_time':std_time,'unix_time':unix_time}
                    with self.lock:
                        self.record=data
                        self.series.append(data)
                        
                    if self.file_name:
                        self.save_record()
                    
                    for client in list(self.clients):
                        try:
                            client.put(self.record)
                        except:
                            self.clients.remove(client)

                    print(f'{colors.grey}round_id: {self.round_id} | std_time: {std_time} | multiplier: {multiplier}')

        def track_account_balance(recent_balance):
            nonlocal old_balance
            recent_balance=float(recent_balance.text.replace(',','').strip())

            if old_balance!=recent_balance:
                old_balance=recent_balance

                with self.lock:
                    self.account_balance=recent_balance
                
                print(f'balance: {self.account_balance}')


        def run_aviator():
            try:
                payouts_block=WebDriverWait(self.driver,self.wait_time).until(EC.presence_of_element_located((By.XPATH,'//*[@class="payouts-block"]')))
                account_balance_element=WebDriverWait(self.driver,self.wait_time).until(EC.presence_of_element_located((By.XPATH,'//div[contains(@class,"balance")]//span[contains(@class,"amount")]')))
                # account_balance=float(account_balance.text)
                manualbet_option=WebDriverWait(self.driver,self.wait_time).until(EC.presence_of_element_located((By.XPATH,'//button[normalize-space(text())="Bet"]')))
                autobet_option=WebDriverWait(self.driver,self.wait_time).until(EC.presence_of_element_located((By.XPATH,'//button[normalize-space(text())="Auto"]')))
                amount_input,multiplier_input=WebDriverWait(self.driver,self.wait_time).until(EC.presence_of_all_elements_located((By.XPATH,'//*[@inputmode="decimal"]')))
                autobet_start_button=WebDriverWait(self.driver,self.wait_time).until(EC.presence_of_element_located((By.XPATH,'//div[@class="auto-bet"]//div[@class="input-switch off"]')))
                autocashout_start_button=WebDriverWait(self.driver,self.wait_time).until(EC.presence_of_element_located((By.XPATH,'//div[@class="cash-out-switcher"]//div[@class="input-switch off"]')))
                
                is_autocashout_active=True

                if payouts_block:
                    print(f'{colors.green}connected to game engine successfully')
                    if self.backup:
                        self.manage_backup()

                def automate_trade():
                    nonlocal is_autocashout_active
                    if is_autocashout_active:
                        autobet_option.click()
                        autocashout_start_button.click()

                        amount_value=amount_input.get_attribute('value')
                        for _ in range(len(amount_value.split())):
                            amount_input.send_keys(Keys.CONTROL,Keys.BACKSPACE)

                        amount_input.send_keys(self.bet_amount+Keys.RETURN)


                        multiplier_value=multiplier_input.get_attribute('value')
                        for _ in range(len(multiplier_value.split())):
                            multiplier_input.send_keys(Keys.CONTROL,Keys.BACKSPACE)
                        
                        multiplier_input.send_keys(self.target_multiplier+Keys.RETURN)

                        autobet_start_button.click()

                        is_autocashout_active=False
                        # autocashout_stop_button=WebDriverWait(self.driver,self.wait_time).until(EC.presence_of_element_located((By.XPATH,'//div[@class="cash-out-switcher"]//div[@class="input-switch"]')))
                        # autobet_stop_button=WebDriverWait(self.driver,self.wait_time).until(EC.presence_of_element_located((By.XPATH,'//div[@class="auto-bet"]//div[@class="input-switch"]')))

                while True:
                    try:
                        latest_multipliers=self.driver.find_element(By.CLASS_NAME,'payouts-block').find_elements(By.CLASS_NAME,'bubble-multiplier')
                        latest_balance=self.driver.find_element(By.XPATH,'//div[contains(@class,"balance")]//span[contains(@class,"amount")]')

                        track_multiplier(latest_multipliers)
                        track_account_balance(latest_balance)

                        if self.active_trade:
                            try:
                                automate_trade()
                            except:
                                automate_trade()


                        time.sleep(1)
                    except:
                        raise
            except Exception as e:
                print(f'{colors.red}game engine error!\n{colors.yellow}{e}')
                self.navigate()
            
        threading.Thread(target=run_aviator,daemon=True).start()

    def parse_action(self,action):
        def locate():
            element=WebDriverWait(self.driver,self.wait_time).until(EC.presence_of_element_located((By.XPATH,f'//*[@{action["attribute"]}]')))
            if element:
                print(f'{colors.green}element located')
                return True
            else:
                print(f'{colors.red}element not located')
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
        
        def click_from_list():
            element=WebDriverWait(self.driver,self.wait_time).until(EC.visibility_of_all_elements_located((By.XPATH,f'//*[@{action["attribute"]}]')))[action['choice_index']]
            element.click()
        
        def switch_to_iframe():
            element=WebDriverWait(self.driver,self.wait_time).until(EC.element_to_be_clickable((By.XPATH,f'//*[@{action["attribute"]}]')))
            self.driver.switch_to.frame(element)

        def callback():
            if callable(action['callback']):
                action['callback'](*(action['args']))
            else:
                raise TypeError("callback is not of type 'function'")

        def execute(function):
            time.sleep(action['sleep_time'])
            if action['message']:
                print(f'{colors.cyan}{action["message"]}')
                
            function()

        action_table={
            'locate':locate,
            'click':click,
            'click_from_list':click_from_list,
            'write':write,
            'send':send,
            'switch_to_iframe':switch_to_iframe,
            'callback':callback
            }
        
        execute(action_table[action['action']])
    
    def navigate(self):
        while self.retries>0:
            try:
                self.driver.get(self.target_url)
                print(f'{colors.cyan}navigating to {self.target_url}...')
                for action in self.actions_array:
                    try:
                        self.parse_action(action)

                    except Exception as e:
                        print(f'{colors.yellow}navigation procedure error!\n{colors.yellow}{e}\n')
                        raise

                print(f'{colors.green}navigation procedure successful')
                return

            except:
                print(f'{colors.grey}[{self.retries}]\n{colors.cyan}restarting...')
                self.retries-=1
                self.restart_driver()
        
        print(f'{colors.red}max retries reached')
        sys.exit(1)