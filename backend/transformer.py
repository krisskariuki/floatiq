from scraper import main_thread,w,c,r,g,b,y
from sseclient import SSEClient
from datetime import datetime
from colorama import init
import json
import time
import threading
import sys
import socket

ip_address=socket.gethostbyname(socket.gethostname())

def start_program_at_0sec():
    while datetime.now().second!=0:
        remaining=60-datetime.now().second
        print(f"Starting in: {c}{remaining}{w} seconds",end="\r")
        time.sleep(0.5)

init(autoreset=True)

class Transformer:
    def __init__(self,source_url):
        self.source_url=source_url
        self.sse_source=''
        self.dataset={}
    def connect(self):
        try:
            self.sse_source=SSEClient(self.source_url)
            print(f'\n\n{g}connected to: {c}{self.source_url}\n')
        except :
            print(f'\n\n{r}connection error!\n{y}failed to connect to: {c}{self.source_url}\n')
            sys.exit(1)

    
    def transform(self,resource_file):
        with open(resource_file,'r') as file:
            resource_table=json.load(file)

        time_frames=resource_table['time_frames']
        tokens=resource_table['tokens']

        for time_frame in time_frames:
            for token in tokens:
                self.generate_metrics(token['flop'],time_frame['name'])

    def quantifier(self,target_multiplier,time_frame):
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
        
        def generate_metrics():
            Open=0
            High=float('-inf')
            Low=float('inf')
            Close=0
            std_time=datetime.now().isoformat(sep=' ',timespec='seconds')
            unix_time=int(datetime.now().timestamp())
            interval_time=std_time

            record={}
            series=[]

            for item in self.sse_source:
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
                    print(f'{c}reset has occured!')

                print(f'{b}round_id:{Id} | time:{std_time} | multiplier:{multiplier} | open:{Open} | high:{High} | low:{Low} | close:{Close}')
                time.sleep(1)

            return record,series
        
        threading.Thread(target=generate_metrics,daemon=True).start()

start_program_at_0sec()
transformer=Transformer(f'http://{ip_address}:8080/mozzart_aviator/stream')
transformer.connect()
transformer.quantifier(5,'minute_10')

main_thread()