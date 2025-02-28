from scraper import Action,Navigator
from datetime import datetime
from flask import Flask,Response,jsonify
from flask_cors import CORS
import threading
import time
import json
import random

app=Flask(__name__)
CORS(app)

record=None
recordLock=threading.Lock()

series=[]
seriesLock=threading.Lock()


def yield_data():
    global record
    localRecord=None
    
    while True:
        with recordLock:
            currentRecord=record
        
        if localRecord!=currentRecord:
            localRecord=currentRecord
            yield f'data: {record} \n\n'
        
        else:
            multiplier=round(random.uniform(-0.50,0.50),2)
            bets=None
            dttm=datetime.now().timestamp()
            tempRecord={'multiplier':multiplier,'bets':bets,'time':dttm}

            yield f"data: {json.dumps(tempRecord)}\n\n"
        
        time.sleep(1)

def expose():
    @app.route('/raw/stream')
    def expose_data():
        return Response(yield_data(),content_type='text/event-stream')

    @app.route('/raw/latest')
    def latest():
        global record
        return record

    @app.route('/raw/series')
    def history():
        return jsonify(series[::-1])

def fetch_data():
    def source(instance):
        global record,series
        driver=instance['driver']
        locator=instance['locator']
        previousMutipliers=None     


        id=0
        std_dttm=None
        unix_dttm=None
        multiplier=None
        bets=None
        probability=None
        payout=None
        RTP=None

        multiplier_series=[]

        while True:
            latestMultipliers=driver.find_element(locator.CLASS_NAME,'payouts-block').find_elements(locator.CLASS_NAME,'bubble-multiplier')

            if previousMutipliers!=latestMultipliers:
                previousMutipliers=latestMultipliers
                multiplier=float(latestMultipliers[0].text.replace('x',''))
                bets=int(driver.find_element(locator.XPATH,'//*[@class="all-bets-block d-flex justify-content-between align-items-center px-2 pb-1"]').find_elements(locator.XPATH,'.//div')[0].find_elements(locator.XPATH,'.//div')[1].text)

                std_dttm=datetime.now().isoformat(sep=' ',timespec='seconds')
                unix_dttm=datetime.now().timestamp()

                multiplier_series=[item['multiplier'] for item in series]
                occurences=sum(1 for num in multiplier_series if num > multiplier)

                if len(multiplier_series)>0:
                    probability=round((occurences/len(multiplier_series)),2)
                    payout=round((bets*multiplier*probability),2)
                    RTP=round((multiplier*probability),2)
                

                data={'id':id,'std_time':std_dttm,'multiplier':multiplier,'probability':probability,'bets':bets,'payout':payout,'rtp':RTP,'unix_time':unix_dttm}

                with recordLock:
                    record=json.dumps(data,separators=(',',':'))

                with seriesLock:
                    series.append(data)

                with open('db/raw_series.json','w') as file:
                    fileSeries=json.dumps(series,indent=True,separators=(',',':'))
                    file.write(fileSeries)

                print(f'{data}\n')

                id+=1

            time.sleep(0.1)

    mozzartNavigator=Navigator('https://www.mozzartbet.co.ke/en#/casino')

    mozzartActions=[
    Action(action='locate',attribute='class="login-link mozzart_ke"'),
    Action(action='click',attribute='class="login-link mozzart_ke"'),
    
    Action(action='write',attribute='placeholder="Mobile number"',inputValue='0113294793'),
    Action(action='send',attribute='placeholder="Password"',inputValue='Chri570ph3r.',delay=0),

    Action(action='locate',attribute='alt="Aviator"'),
    Action(action='click',attribute='alt="Aviator"'),

    Action(action='locate',attribute='class="payouts-block"'),
    Action(action='custom',attribute='class="payouts-block"',callback=source,delay=15)
    ]
    mozzartNavigator.navigate(mozzartActions)

fetch_data()
threading.Thread(target=yield_data,daemon=True).start()
expose()
app.run(threaded=True,host='0.0.0.0',port=8080)