from scraper import Scraper
from dotenv import load_dotenv
from flask import Flask,Response,jsonify
from flask_cors import CORS
import os
import argparse
import threading
import time
import json

load_dotenv()
PHONE=os.getenv('PHONE')
PASSWORD=os.getenv('PASSWORD')

app=Flask(__name__)
CORS(app)

parser=argparse.ArgumentParser(description='for controlling the bots configuration parameters')
parser.add_argument('--headless',action='store_true')
parser_arguments=parser.parse_args()

scraper=Scraper(target_url='https://www.mozzartbet.co.ke/en#/casino',wait_time=30,headless=parser_arguments.headless)

scraper.folder_name='db'
scraper.base_file_name='mozzart_aviator'

scraper.action(action='click',attribute='class="login-link mozzart_ke"',message='logging in...')
scraper.action(action='write',attribute='placeholder="Mobile number"',message='writing phone input...',input_value=PHONE)
scraper.action(action='send',attribute='placeholder="Password"',message='writing password input...',input_value=PASSWORD)
scraper.action(action='click',attribute='alt="Aviator"',message='connecting to game engine...',sleep_time=1)

@app.route('/mozzart_aviator/latest',methods=['GET'])
def get_latest():
    with scraper.record_lock:
        return jsonify(scraper.record)

@app.route('/mozzart_aviator/history',methods=['GET'])
def get_history():
    with scraper.series_lock:
        return jsonify(scraper.series)

@app.route('/mozzart_aviator/stream',methods=['GET'])
def stream_data():
    def event_stream():
        last_seen=None
        while True:
            with scraper.record_lock:
                if scraper.record and scraper.record!=last_seen:
                    last_seen=scraper.record.copy()
                    yield f"data:{json.dumps(last_seen,separators=(',',':'))}\n\n"
            time.sleep(1)
    return Response(event_stream(),mimetype='text/event-stream')

def run_app():
    app.run(host='0.0.0.0',port=8080,threaded=True)

threading.Thread(target=scraper.navigate,args=(scraper.watch_aviator,)).start()
threading.Thread(target=run_app,daemon=True).start()