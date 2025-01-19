from colorama import Fore,init
import json
import random

init()
w=Fore.WHITE
c=Fore.LIGHTBLACK_EX
m=Fore.LIGHTBLUE_EX
p=Fore.LIGHTMAGENTA_EX

def get_range(num):
    ranges=[
        (1.0,2.0,'min'),
        (2.0,10.0,'mid'),
        (10.0,float('inf'),'max')
    ]

    for start,end,range in ranges:
        if start<= num <=end:
            return range
    
def process_data(fileUrl):
    with open(fileUrl,'r') as file:
        rawData=json.load(file)
    
    stake=1
    price=0
    color=w

    multiplier_series=[item['multiplier'] for item in rawData]
    price_series=[]
    color_series=[]

    for num in multiplier_series:
        multiplier=num
        Lambda=1/multiplier
        target=round((random.expovariate(Lambda))+1,2)

        multiplier_range=get_range(multiplier)

        if multiplier_range=='min':
            color=c
        elif multiplier_range=='mid':
            color=m
        elif multiplier_range=='max':
            color=p

        if multiplier > target:
            price+=(target*stake)-stake
        else:
            price-=stake
        
        price_series.append(round(price,2))
        color_series.append(p)

        print(f'{color}{multiplier}')

    # print(price_series)

process_data('db/raw_series.json')
