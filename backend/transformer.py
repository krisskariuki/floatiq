from flask import Flask,Response,jsonify
from flask_cors import CORS
from datetime import datetime
from  sseclient import SSEClient
import time
import json

class Transformer:
    def __init__(self,formatFile,sseUrl):
        with open(formatFile,'r') as file:
            dataFormat=json.load(file)

        self.tokens=dataFormat['tokens']
        self.timeframes=dataFormat['timeframes']
        self.rawRecords=SSEClient(sseUrl)


    def start(self):
        self.processor(self.tokens[0],self.timeframes[0])
            
    def processor(self,token,timeframe):
        tokenFlop=float(token['flop'])
        timeUnit=timeframe['unit']
        timeInterval=timeframe['interval']
        Open,High,Low,Close,volume=0.00,float('-inf'),float('inf'),0.00,0.00
        multiplier,bets,dttm=0,0,0
        record={}
        series=[]

        timerHashMap={
            'second':lambda:datetime.now().second,
            'minute':lambda:datetime.now().minute,
            'hour':lambda:datetime.now().hour
        }

        while True:

            for item in self.rawRecords:
                item=json.loads(str(item))
                multiplier,bets,dttm=item['noise'],item['bets'],item['time']
        
            currentTime=timerHashMap[timeUnit]()

            if multiplier>tokenFlop:
                Close+=tokenFlop-1
            else:
                Close-=1
            High=max(Open,High,Close)
            Low=min(Open,Low,Close)

            if currentTime % timeInterval == 0:
                Open=Close
                High=float('-inf')
                Low=float('inf')
            
            record={'open':Open,'high':High,'low':Low,'close':Close}
            series.append(record)

            print(record)
            time.sleep(1)

            
            

newTransformer=Transformer('format.json','http://localhost:8000/raw/stream')
newTransformer.start()