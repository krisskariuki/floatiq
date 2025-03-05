from flask import Flask,jsonify,Response
from flask_cors import CORS
from datetime import datetime
from sseclient import SSEClient
import time
import json
import threading
import random

app=Flask(__name__)
CORS(app)

class Transformer:
    def __init__(self,source_url,token,time_frame):
        self.sse_source=SSEClient(source_url)
        self.flop=float(token['flop'])
        self.time_unit=time_frame["unit"]
        self.time_step=time_frame["interval"]
        
        self.record={}
        self.series=[]
        
    def start(self):
        threading.Thread(target=self.transform,daemon=True).start()

    def timer(self):
        timer_table={
            'second':lambda T:datetime.now().second%T==0,
            'minute':lambda T:datetime.now().minute%T==0 and datetime.now().second==0,
            'hour':lambda T:datetime.now().hour%T==0 and datetime.now().minute==0 and datetime.now().second==0,
            'day':lambda T:datetime.now().day%T==0 and datetime.now().hour==0 and datetime.now().minute==0 and datetime.now().second==0,
        }
        return timer_table[self.time_unit](self.time_step)
            
    def generator(self):
        while True:
            yield f"data:{json.dumps(self.record)}\n\n"
            time.sleep(1)
            
    def transform(self):
        multiplier=0
        Open=0
        High=float('-inf')
        Low=float('inf')
        Close=0
        Coeff=0
        std_time=datetime.now().strftime('%Y-%m-%d %H:M%:%S')
        unix_time=datetime.now().timestamp()
        
        for item in self.sse_source:
            record=json.loads(item.data)
            
            multiplier=record['multiplier']
            std_time=record['std_time']

            if multiplier>=1:
                if multiplier>self.flop:
                    Coeff+=self.flop-1
                    Close+=self.flop-1
                else:
                    Coeff-=1
                    Close-=1
            else:
                Close=Coeff+round(random.uniform(-0.5,0.5),2)
                
            High=max(Open,High,Close)
            Low=min(Open,Low,Close)
            self.record={'std_time':std_time,'unix_time':unix_time,'multiplier':multiplier,'coef':Coeff,'open':round(Open,2),'high':round(High,2),'low':round(Low,2),'close':round(Close,2)}
            
            if self.timer():
                unix_time=datetime.now().timestamp()
                Open=Close
                High=float('-inf')
                Low=float('inf')
                
                self.series.append(self.record)
                
            time.sleep(1)
    def expose(self):
        def serve_series():
            EPoint=f"series/{time_frame['name']}/{token['name']}"
            url=f"/market/{EPoint}"

            app.add_url_rule(url,endpoint=EPoint,view_func=lambda:jsonify(self.series))
            
        def serve_latest():
            EPoint=f"latest/{time_frame['name']}/{token['name']}"
            url=f"/market/{EPoint}"

            app.add_url_rule(url,endpoint=EPoint,view_func=lambda:jsonify(self.record))
        
        def serve_stream():
            EPoint=f"stream/{time_frame['name']}/{token['name']}"
            url=f"/market/{EPoint}"
            app.add_url_rule(url,endpoint=EPoint,view_func=lambda:Response(self.generator(),mimetype='text/event-stream'))

        app.run(debug=True,host='0.0.0.0',port=8000)

with open('config/format.json','r') as file:
    format_data=json.load(file)

time_frames=format_data['time_frames']
tokens=format_data['tokens']

for time_frame in time_frames:
    for token in tokens:
        transformer=Transformer('http://127.0.0.1:8080/raw/stream',token,time_frame)
        transformer.start()
        transformer.expose()