from scraper import Action,Navigator
from datetime import datetime
from flask import Flask,Response
from flask_cors import CORS
import threading
import time
import json

app=Flask(__name__)
CORS(app)

record=None
recordLock=threading.Lock()


def yield_data():
    global record
    localRecord=None
    
    while True:
        with recordLock:
            currentRecord=record
        
        if localRecord!=currentRecord:
            localRecord=currentRecord

            yield f'data: {record} \n\n'
        
        time.sleep(0.1)

@app.route('/stream')
def expose_data():
    return Response(yield_data(),content_type='text/event-stream')

def fetch_data():
    def loop(instance):
        global record
        driver=instance['driver']
        locator=instance['locator']

        previousMutipliers=None
        dttm=None

        while True:
            latestMultipliers=driver.find_element(locator.CLASS_NAME,'payouts-block').find_elements(locator.CLASS_NAME,'bubble-multiplier')

            if previousMutipliers!=latestMultipliers:
                previousMutipliers=latestMultipliers
                multiplier=float(latestMultipliers[0].text.replace('x',''))
                bets=driver.find_element(locator.XPATH,'//*[@class="all-bets-block d-flex justify-content-between align-items-center px-2 pb-1"]').find_elements(locator.XPATH,'.//div')[0].find_elements(locator.XPATH,'.//div')[1].text

                dttm=datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                data={'noise':multiplier,'bets':bets,'time':dttm}

                with recordLock:
                    record=json.dumps(data,separators=(',',':'))

                print(data)

            time.sleep(0.1)

    mozzartNavigator=Navigator('https://www.mozzartbet.co.ke/en#/casino')

    mozzartActions=[
    Action(action='click',attribute='class="login-link mozzart_ke"'),
    Action(action='write',attribute='placeholder="Mobile number"',inputValue='0113294793'),
    Action(action='send',attribute='placeholder="Password"',inputValue='Chri570ph3r.',delay=0),
    Action(action='click',attribute='alt="Aviator"'),
    Action(action='custom',callback=loop,delay=10)
    ]
    mozzartNavigator.navigate(mozzartActions)

fetch_data()
threading.Thread(target=yield_data,daemon=True).start()
app.run(threaded=True,host='0.0.0.0',port=8000)