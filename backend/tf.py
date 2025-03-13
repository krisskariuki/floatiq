from config import TARGET_MULTIPLIERS,TIME_FRAMES,PRODUCER_PORT,LOCAL_IP
from sseclient import SSEClient
from utils import colors,main_thread
from datetime import datetime
import json
import sys
import time
import threading

class Transformer:
    def __init__(self):
        self.recv_record=None
        self.data_store={}

        for timeframe in TIME_FRAMES:
            for target in TARGET_MULTIPLIERS:
                self.data_store[f'{timeframe}|{target}']=(
                    {
                    'open':0,
                    'high':float('-inf'),
                    'low':float('inf'),
                    'close':0,
                    'cumsum':0
                    })
    
    def connect(self,sse_url):
        def run_connect():
            try:
                print(f'\n\n{colors.green}connected to: {colors.cyan}{sse_url}\n')
                for item in SSEClient(sse_url):
                    self.recv_record=json.loads(item.data)


            except:
                print(f'\n\n{colors.red}connection error!\n{colors.yellow}failed to connect to: {colors.cyan}{sse_url}\n')
                sys.exit(1)
        
        threading.Thread(target=run_connect,daemon=True).start()
    
    def transform(self,target_multipliers=[],time_frames=[]):
        local_record=None
        Open,High,Low,Close,Cumsum=0,float('-inf'),float('inf'),0,0

        
        def is_time_to_update(time_frame):
            now=datetime.now()
            time_unit,time_step=time_frame.split('_')
            time_step=int(time_step)

            time_table={
                'second':lambda:now.second % time_step==0,
                'minute':lambda:now.minute % time_step==0 and now.second==0,
                'hour':lambda:now.hour % time_step==0 and now.minute==0 and now.second==0,
                'day':lambda:now.day % time_step==0 and now.hour==0 and now.minute==0 and now.second==0 
            }

            return time_table[time_unit]()

        def update_metrics(record,target,time_frame):
            nonlocal Open,High,Low,Close,Cumsum
            if record['multiplier'] > target:
                Close +=target-1
            else:
                Close-=1
            
            High=max(Open,High,Close)
            Low=min(Open,Low,Close)
            Cumsum+=record['multiplier']

            if is_time_to_update(time_frame):
                Open=Close
                High=float('-inf')
                Low=float('inf')
                Cumsum=0

                print(f"{colors.cyan}reset has occurred")

            print(f"std_time:{record['std_time']} | open:{Open} | High:{High} | low:{Low} | close:{Close} | cumsum:{round(Cumsum,2)} multiplier:{record['multiplier']}")

            return Open,High,Low,Close,Cumsum
        

        def run_transformer():
            nonlocal local_record
            while True:
                if local_record!=self.recv_record:
                    local_record=self.recv_record
                    update_metrics(self.recv_record,3,'minute_5')
                    
                time.sleep(1)
        
        threading.Thread(target=run_transformer,daemon=True).start()

tf=Transformer()
tf.connect(f'http://{LOCAL_IP}:{PRODUCER_PORT}/simulation/stream')
tf.transform()

main_thread()