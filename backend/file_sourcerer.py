from flask import Flask, Response
from flask_cors import CORS
import time
import json
import threading
import random

app = Flask(__name__)
CORS(app)

sourceFilePath = '../db/mozzart.json'
with open(sourceFilePath, 'r') as sourceFile:
    sourceData = json.load(sourceFile)[::-1]

def emitter():
    i = 0
    noise = 0
    sleepTime = 0
    randomNoise = round(random.uniform(0.01, 0.99), 2)

    while True:
        noise = sourceData[i][0]
        sleepTime = 20 * noise ** 0.2

        timer = time.time()

        while time.time() - timer < sleepTime:
            randomNoise = round(random.uniform(0.01, 0.99), 2)

            yield f"data:{json.dumps(randomNoise)}\n\n"
            time.sleep(1)

        yield f"data:{noise}\n\n"

        i += 1
        if i > len(sourceData):
            i = 0

@app.route('/floatIQ/stream/noise')
def streamNoise():
    return Response(emitter(), mimetype='text/event-stream')

def run_flask_app():
    app.run(host='localhost', port=8000, debug=True, threaded=True)

if __name__ == '__main__':
    # Run Flask app in a separate thread
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.start()
