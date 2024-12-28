from flask import Flask,Response
from flask_cors import CORS
import json 
import threading
import time

app=Flask(__name__)
CORS(app)

data=0
dataLock=threading.Lock()

def yield_data():
    global data
    while True:
        with dataLock:
            data+=1
        time.sleep(1)

@app.route('/stream')
def expose_data():
    def get_data():
        global data
        locale=None

        while True:
            with dataLock:
                currentData=data
            if locale!=currentData:
                locale=currentData
                yield f'data: {data}\n\n'

            time.sleep(0.5)

    return Response(get_data(),content_type='text/event-stream')


threading.Thread(target=yield_data,daemon=True).start()
app.run(threaded=True,host='0.0.0.0',port=8000)