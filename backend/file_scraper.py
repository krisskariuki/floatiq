from scraper import main_thread
from flask import Flask, Response
from flask_cors import CORS
import time
import json
import pandas as pd
import threading

app = Flask(__name__)
CORS(app)

class File_sourcer:
    def __init__(self,filepath):
        self.record={}
        self.record_lock=threading.Lock()

        self.series=pd.read_csv(filepath).to_dict(orient='split',index=False)['data']
        
        threading.Thread(target=self.yield_data,daemon=True).start()
    
    def start_server(self):
        @app.route('/file_source/stream')
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
        
        def run_flask():
            app.run(host='0.0.0.0',port=8080,threaded=True)
        
        threading.Thread(target=run_flask,daemon=True).start()

    def yield_data(self):
        i=0
        sleep_time=0

        while True:
            multiplier=self.series[i][0]
            std_time=self.series[i][1]
            unix_time=self.series[i][2]

            sleep_time=20*multiplier**0.2

            with self.record_lock:
                self.record={'multiplier':multiplier,'std_time':std_time,'unix_time':unix_time}

            time.sleep(sleep_time)

            i+=1
            if i>len(self.series):
                break

file_sourcer=File_sourcer('db/mozzart.csv')
file_sourcer.start_server()

main_thread()