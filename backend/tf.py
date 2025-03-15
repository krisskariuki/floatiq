from config import TARGET_MULTIPLIERS,TIME_FRAMES,LOCAL_IP,PRODUCER_PORT,PROCESSOR_PORT
from sseclient import SSEClient
from utils import colors,main_thread
from datetime import datetime
from flask import Flask,Response,request
from flask_cors import CORS
from waitress import serve
from queue import Queue
import json
import sys
import time
import threading
import random

app=Flask(__name__)
CORS(app)

class Transformer:
    def __init__(self):
        
        self.lock=threading.Lock()
        self.clients=set()
        
        self.recv_record={
            'round_id':None,
            'unix_time':int(datetime.now().timestamp()),
            'std_time':datetime.now().isoformat(sep=' ',timespec='seconds'),
            'multiplier':1.00
        }

        self.record_table={f'{timeframe}:{target}':{
            'std_time':datetime.now().isoformat(sep=' ',timespec='seconds'),
            'unix_time':int(datetime.now().timestamp()),
            'cycle_time':int(datetime.now().timestamp()),
            'open':0,
            'high':float('-inf'),
            'low':float('inf'),
            'close':0
        } for timeframe in TIME_FRAMES for target in TARGET_MULTIPLIERS}

        self.series_table={f'{timeframe}:{target}':[] for timeframe in TIME_FRAMES for target in TARGET_MULTIPLIERS}

    def connect(self,sse_url):
        def run_connect():
            try:
                print(f'\n\n{colors.green}connected to: {colors.cyan}{sse_url}\n')
                for item in SSEClient(sse_url):
                    with self.lock:
                        self.recv_record=json.loads(item.data)


            except:
                print(f'\n\n{colors.red}connection error!\n{colors.yellow}failed to connect to: {colors.cyan}{sse_url}\n')
                sys.exit(1)
        
        threading.Thread(target=run_connect,daemon=True).start()
    
    def broadcast(self):
                
        @app.route('/market/latest')
        def get_latest():
            target=request.args.get('target',type=str)
            timeframe=request.args.get('timeframe',type=str)

            key=f'{timeframe}:{target}'
            with self.lock:
                record=self.record_table[key]

            return Response(json.dumps(record,indent=True),mimetype='application/json')
        
        
        @app.route('/market/history')
        def get_history():
            target=request.args.get('target',type=str)
            timeframe=request.args.get('timeframe',type=str)

            key=f'{timeframe}:{target}'
            with self.lock:
                series=self.series_table[key]
            
            return Response(json.dumps(series,indent=True),mimetype='application/json')
        
        @app.route('/market/stream')
        def stream_data():
            target=request.args.get('target',type=str)
            timeframe=request.args.get('timeframe',type=str)

            key=f'{timeframe}:{target}'
            with self.lock:
                record=self.record_table[key]

                def event_stream():
                    nonlocal record
                    queue=Queue()

                    with self.lock:
                        self.clients.add((key,queue))

                    if record:
                        yield f"record:{json.dumps(record,separators=(',',':'))}\n\n"

                    while True:
                        record=queue.get()
                        yield f"data:{json.dumps(record,separators=(',',':'))}\n\n"

                return Response(event_stream(),mimetype='text/event-stream')

        def run_app():
            print(f'\n{colors.green}Started transformer\n{colors.white}server is running on {colors.cyan}http://{LOCAL_IP}:{PROCESSOR_PORT}\n')
            serve(app,host='0.0.0.0',port=PROCESSOR_PORT,channel_timeout=300,threads=50,connection_limit=500)

        threading.Thread(target=run_app,daemon=True).start()

    def transform(self,target_multipliers=[],time_frames=[]):
        local_record=None

        def is_time_to_update(last_reset_time,time_frame):
            now=datetime.now()
            time_unit,time_step=time_frame.split('_')
            time_step=int(time_step)

            elapsed_time=time.time()-last_reset_time

            time_table={
                'second':time_step,
                'minute':time_step*60,
                'hour':time_step*3600,
                'day':time_step*86400
            }

            return elapsed_time >= time_table.get(time_unit,0)

        def update_metrics(record,target,time_frame):
            key=f'{time_frame}:{target}'
            target=float(target)

            multiplier=record['multiplier']

            with self.lock:
                entry=self.record_table.get(key)

            Std_time,Unix_time,Cycle_time,Open,High,Low,Close=entry['std_time'],entry['unix_time'],entry['cycle_time'],entry['open'],entry['high'],entry['low'],entry['close']

            if multiplier > target:
                Close +=target-1
            else:
                Close-=1
            
            Std_time=datetime.now().isoformat(sep=' ',timespec='seconds')
            Unix_time=int(datetime.now().timestamp())
            High=max(Open,High,Close)
            Low=min(Open,Low,Close)

            if is_time_to_update(Cycle_time,time_frame):
                Cycle_time=int(datetime.now().timestamp())
                Open=Close
                High=Close
                Low=Close
            
            record={
            'cycle_time':Cycle_time,'std_time':Std_time,'unix_time':Unix_time,'open':Open,'high':High,'low':Low,'close':Close
            }
            with self.lock:
                for client_key,client_queue in list(self.clients):
                    if client_key==key:
                        try:
                            client_queue.put(record)
                        except:
                            self.clients.remove((client_key,client_queue))

                self.record_table[key]=record
                self.series_table[key].append(record.copy())

        def run_transformer():
            nonlocal local_record
            while True:
                if local_record is None or local_record['round_id']!=self.recv_record['round_id']:
                    local_record=self.recv_record
                    
                    for TIMEFRAME in TIME_FRAMES:
                        for TARGET in TARGET_MULTIPLIERS:
                            update_metrics(local_record,TARGET,TIMEFRAME)

                time.sleep(1)
        
        threading.Thread(target=run_transformer,daemon=True).start()

tf=Transformer()
tf.connect(f'http://{LOCAL_IP}:{PRODUCER_PORT}/simulation/stream')
tf.transform()
tf.broadcast()

main_thread()