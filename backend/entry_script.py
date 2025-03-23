from flask import Flask,request,jsonify
from flask_cors import CORS
from utils import main_thread
import subprocess
import threading


app=Flask(__name__)
CORS(app)

def main():
    game_providers_table={
        'mozzartbet':'mozzart_scraper.py',
        'betika':'betika_scraper.py',
        '22bet':'22bet_scraper.py'
    }

    @app.route('/floatiq/login',methods=['POST'])
    def determine_game_provider():
        data=request.get_json()

        game_provider=data['game_provider']
        phone=data['phone']
        password=data['password']

        process=subprocess.Popen(['python',game_providers_table[game_provider],'--phone',phone,'--password',password],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)

        for line in process.stdout:
            print(line,end='')

        return 'request received'
    
    app.run(port='8888')


if __name__=='__main__':
        threading.Thread(target=main,daemon=True).start()
        main_thread()