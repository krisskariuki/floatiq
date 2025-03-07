from flask import Flask, Response
from flask_cors import CORS
import time
import json
import random
import pandas as pd

app = Flask(__name__)
CORS(app)

class File_sourcer:
    def __init__(self,filepath):
        self.series=pd.read_csv(filepath).to_dict(orient='split',index=False)['data']
    
    def start_server(self):
        @app.route('/raw/stream')
        def live_stream():
            return Response(self.yield_data(), mimetype='text/event-stream')
        
        app.run(host='0.0.0.0',port=8080,threaded=True)
    
    def yield_data(self):
        i=0
        multiplier=0
        sleep_time=0
        noise=round(random.uniform(0.01, 0.99),2)

        while True:
            multiplier=self.series[i][0]
            std_time=self.series[i][1]

            sleep_time=20*multiplier**0.2

            timer=time.time()

            while time.time()-timer<sleep_time:
                noise=round(random.uniform(0.01, 0.99),2)

                yield f"data: {json.dumps({'multiplier':noise,'std_time':std_time},separators=(',',':'))}\n\n"
                time.sleep(1)

            yield f"data: {json.dumps({'multiplier':multiplier,'std_time':std_time},separators=(',',':'))}\n\n"

            i+=1
            if i>len(self.series):
                i=0

file_sourcer=File_sourcer('db/c77.csv')
file_sourcer.start_server()