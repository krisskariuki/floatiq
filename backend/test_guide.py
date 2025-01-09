from flask import Flask, Response
from flask_cors import CORS
import time
import json
import random
import subprocess

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

if __name__ == '__main__':
    # Now start Flask app (main thread)
    app.run(host='localhost', port=8000, debug=True, threaded=True)
