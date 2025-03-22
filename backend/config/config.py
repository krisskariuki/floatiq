from dotenv import load_dotenv
import os
import socket

load_dotenv()

MOZZART_URL=os.getenv('MOZZART_URL','https://www.mozzartbet.co.ke/en#/casino')
BETIKA_URL=os.getenv('BETIKA_URL','https://www.betika.com/en-ke/')
DY68F_URL=os.getenv('DY68F','https://a.dy68fo0tball.com/#/pages/login/index')

TARGET_MULTIPLIERS=os.getenv('TARGET_MULTIPLIERS',"2.00,3.00,5.00,10.00,15.00,20.00,25.00,30.00,35.00,40.00,45.00,50.00").split(',')
TIME_FRAMES=os.getenv('TIME_FRAMES',"minute_5,minute_10,minute_30,hour_1,hour_4,hour_6,hour_12,day_1").split(',')

LOCAL_IP=os.getenv('LOCAL_IP',socket.gethostbyname(socket.gethostname()))
PRODUCER_PORT=int(os.getenv('PRODUCER_PORT',8080))
PROCESSOR_PORT=int(os.getenv('PROCESSOR_PORT',8000))
PRODUCER_STREAM=os.getenv('PRODUCER_STREAM','simulation/stream')