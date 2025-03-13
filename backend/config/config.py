from dotenv import load_dotenv
import os
import socket

load_dotenv()

MOZZART_URL=os.getenv('MOZZART_URL','https://www.mozzartbet.co.ke/en#/casino')

TARGET_MULTIPLIERS=os.getenv('TARGET_MULTIPLIERS',"2.00,3.00,5.00,10.00").split(',')
TIME_FRAMES=os.getenv('TIME_FRAMES',"minute_10,minute_30,hour_1,hour_4,hour_6,hour_12,day_1").split(',')

LOCAL_IP=os.getenv('LOCAL_IP',socket.gethostbyname(socket.gethostname()))
PRODUCER_PORT=int(os.getenv('EVENT_PRODUCER_PORT',8080))
PROCESSOR_PORT=int(os.getenv('EVENT_PROCESSOR_PORT',8000))
