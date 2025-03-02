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
    def __init__(self,sourceUrl,token,timeframe):
        self.source=SSEClient(sourceUrl)
        self.flop=float(token['flop'])
        self.time_unit=timeframe["unit"]
        self.time_step=timeframe["interval"]
        
        self.id=0
        self.multiplier=0
        self.Open=0
        self.High=float('-inf')
        self.Low=float('inf')
        self.Close=0
        self.Coef=0
        self.traffic=0
        self.Dttm=datetime.now().timestamp()
        self.record={}
        self.series=[]
        
        threading.Thread(target=self.TRANSFORM,daemon=True).start()
        self.SERVE_SERIES()
        self.SERVE_LATEST()
        self.SERVE_STREAM()
        
    def TIMER(self):
        timerRef={
            'second':lambda T:datetime.now().second%T==0,
            'minute':lambda T:datetime.now().minute%T==0 and datetime.now().second==0,
            'hour':lambda T:datetime.now().hour%T==0 and datetime.now().minute==0 and datetime.now().second==0,
            'day':lambda T:datetime.now().day%T==0 and datetime.now().hour==0 and datetime.now().minute==0 and datetime.now().second==0,
        }
        return timerRef[self.time_unit](self.time_step)
            
    def GENERATOR(self):
        while True:
            yield f"data:{json.dumps(self.record)}\n\n"
            time.sleep(1)
            
    def TRANSFORM(self):
        for record in self.source:
            record=json.loads(record.data)
            
            self.multiplier=record['multiplier']

            if self.multiplier>=1:
                if self.multiplier>self.flop:
                    self.Coef+=self.flop-1
                    self.Close+=self.flop-1
                else:
                    self.Coef-=1
                    self.Close-=1
            else:
                self.Close=self.Coef+round(random.uniform(-0.5,0.5),2)
                
            self.High=max(self.Open,self.High,self.Close)
            self.Low=min(self.Open,self.Low,self.Close)
            self.record={'time':self.Dttm,'multiplier':self.multiplier,'coef':self.Coef,'open':round(self.Open,2),'high':round(self.High,2),'low':round(self.Low,2),'close':round(self.Close,2)}
            
            if self.TIMER():
                self.Dttm=datetime.now().timestamp()
                self.Open=self.Close
                self.High=float('-inf')
                self.Low=float('inf')
                
                self.series.append(self.record)
                
            time.sleep(1)
            
    def SERVE_SERIES(self):
        EPoint=f"series/{timeframe['name']}/{token['name']}"
        url=f"/market/{EPoint}"

        app.add_url_rule(url,endpoint=EPoint,view_func=lambda:jsonify(self.series))
        
    def SERVE_LATEST(self):
        EPoint=f"latest/{timeframe['name']}/{token['name']}"
        url=f"/market/{EPoint}"

        app.add_url_rule(url,endpoint=EPoint,view_func=lambda:jsonify(self.record))
    
    def SERVE_STREAM(self):
        EPoint=f"stream/{timeframe['name']}/{token['name']}"
        url=f"/market/{EPoint}"

        app.add_url_rule(url,endpoint=EPoint,view_func=lambda:Response(self.GENERATOR(),mimetype='text/event-stream'))

with open('config/format.json','r') as file:
    format_data=json.load(file)

timeframes=format_data['timeframes']
tokens=format_data['tokens']

for timeframe in timeframes:
    for token in tokens:
        Transformer('http://127.0.0.1:8080/raw/stream',token,timeframe)
        
if __name__=='__main__':
    app.run(debug=True,host='0.0.0.0',port=8000)