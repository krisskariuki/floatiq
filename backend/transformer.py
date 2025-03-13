from sseclient import SSEClient
from datetime import datetime
from utils import colors,main_thread
from config import LOCAL_IP,PRODUCER_PORT,TARGET_MULTIPLIERS,TIME_FRAMES
import json
import time
import threading
import sys

def start_program_at_0sec():
    while datetime.now().second!=0:
        remaining=60-datetime.now().second
        print(f"Starting in: {colors.cyan}{remaining}{colors.white} seconds",end="\r")
        time.sleep(0.5)

class Transformer:
    def __init__(self):
        self.recv_record={}
        self.data_store={}
        for timeframe in TIME_FRAMES:
            for target in TARGET_MULTIPLIERS:
                self.data_store[f"{timeframe}|{target}"]={
                    'std_time':datetime.now().isoformat(sep=' ',timespec='seconds'),
                    'unix_time':int(datetime.now().timestamp()),
                    'open':0,
                    'high':0,
                    'low':0,
                    'close':0
                    }

    def connect(self,source_url):
        def run_connect():
            try:
                for item in SSEClient(source_url):
                    self.recv_record=json.loads(item.data)

                print(f'\n\n{colors.green}connected to: {colors.cyan}{self.source_url}\n')

            except :
                print(f'\n\n{colors.red}connection error!\n{colors.yellow}failed to connect to: {colors.cyan}{self.source_url}\n')
                sys.exit(1)
            
            threading.Thread(target=run_connect,daemon=True).start()


    def run_transformer(self,target_multipliers,time_frames):
        local_record=None
        last_reset_time=time.time()

        def timer(time_frame):
            nonlocal last_reset_time
            time_unit,time_step=time_frame.split('_')
            time_step=int(time_step)
            
            current_time=time.time()
            elapsed_time=current_time-last_reset_time

            time_map={
                "second":time_step,
                "minute":time_step*60,
                "hour":time_step*3600,
                "day":time_step*86400,
            }

            if elapsed_time>=time_map.get(time_unit):
                last_reset_time=current_time
                return True
            return False
        
        def update_metrics():
            Open=0
            High=float('-inf')
            Low=float('inf')
            Close=0
            std_time=datetime.now().isoformat(sep=' ',timespec='seconds')
            unix_time=int(datetime.now().timestamp())
            interval_time=std_time

            record={}
            series=[]

            while True:
                received_record=json.loads(item.data)

                Id=received_record['round_id']
                multiplier=received_record['multiplier']
                std_time=received_record['std_time']
                unix_time=received_record['unix_time']

                if multiplier>target_multiplier:
                    Close+=target_multiplier-1
                else:
                    Close-=1

                High=max(Open,High,Close)
                Low=min(Open,Low,Close)
                record={'id':Id,'interval_time':interval_time,'std_time':std_time,'unix_time':unix_time,'multiplier':multiplier,'open':round(Open,2),'high':round(High,2),'low':round(Low,2),'close':round(Close,2)}

                if timer(time_frame):
                    interval_time=std_time
                    Open=Close
                    High=float('-inf')
                    Low=float('inf')
                    
                    series.append(record)
                    print(f'{colors.cyan}reset has occured!')

                print(f'{colors.grey}round_id:{Id} | time:{std_time} | open:{Open} | high:{High} | low:{Low} | close:{Close} | multiplier:{multiplier}')
                time.sleep(1)

            return record,series
        
        threading.Thread(target=generate_metrics,daemon=True).start()

# start_program_at_0sec()
mozzart_transformer=Transformer()
mozzart_transformer.connect(f'http://{LOCAL_IP}:{PRODUCER_PORT}/simulation/stream')
main_thread()
