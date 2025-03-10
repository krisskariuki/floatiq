from scraper import main_thread,b,c,y,g,w
from flask import Flask, Response
from flask_cors import CORS
from datetime import datetime
from waitress import serve
import time
import json
import pandas as pd
import threading
import argparse
import socket

ip_address=socket.gethostbyname(socket.gethostname())
port='8080'

parser=argparse.ArgumentParser(description='simulate historic data using')
parser.add_argument('source',type=str)
parser.add_argument('--unalive',action='store_false')
parser_args=parser.parse_args()

app = Flask(__name__)
CORS(app)

class Simulator:
    def __init__(self,filepath,run_live=True):
        self.run_live=run_live
        self.record={}
        self.record_lock=threading.Lock()

        self.series=pd.read_csv(filepath).to_dict(orient='split')['data']
        
        threading.Thread(target=self.yield_data,daemon=True).start()
    
    def start_server(self):
        @app.route('/simulation/stream')
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
        
        def run_server():
            print(f'\n{g}Started simulation\n{w}server is running on {c}http://{ip_address}:{port}\n')
            serve(app,host='0.0.0.0',port=port,channel_timeout=300,threads=50,connection_limit=500)
        
        threading.Thread(target=run_server,daemon=True).start()

    def yield_data(self):
        i=0
        sleep_time=0

        while True:
            recv_record=self.series[i]
            round_id=recv_record[0]
            multiplier=recv_record[1]
            std_time=datetime.now().isoformat(sep=' ',timespec='seconds') if self.run_live else recv_record[2]
            unix_time=int(datetime.now().timestamp()) if self.run_live else recv_record[3]

            sleep_time=25*multiplier**0.2
            time.sleep(sleep_time)

            with self.record_lock:
                self.record={'round_id':round_id,'multiplier':multiplier,'std_time':std_time,'unix_time':unix_time}

            print(f'{b}round_id:{round_id} | std_time:{std_time} | multiplier:{multiplier}')

            i+=1
            if i>=len(self.series):

                print(f'{y}End of simulation!')
                break

simulator=Simulator(filepath=parser_args.source,run_live=parser_args.unalive)
simulator.start_server()

main_thread()