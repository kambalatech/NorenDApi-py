from api_helper import NorenApiPy, get_time
import datetime
import logging
import time
import yaml
import pandas as pd

#sample
logging.basicConfig(level=logging.DEBUG)

#flag to tell us if the websocket is open
socket_opened = False

#application callbacks
def event_handler_order_update(message):
    print("order event: " + str(message))


def event_handler_quote_update(message):
    #e   Exchange
    #tk  Token
    #lp  LTP
    #pc  Percentage change
    #v   volume
    #o   Open price
    #h   High price
    #l   Low price
    #c   Close price
    #ap  Average trade price

    print("quote event: {0}".format(time.strftime('%d-%m-%Y %H:%M:%S')) + str(message))
    

def open_callback():
    global socket_opened
    socket_opened = True
    print('app is connected')
    
    api.subscribe('NSE|11630')
    #api.subscribe(['NSE|22', 'BSE|522032'])

#end of callbacks

def get_time(time_string):
    data = time.strptime(time_string,'%d-%m-%Y %H:%M:%S')

    return time.mktime(data)

#start of our program
api = NorenApiPy()

#use following if yaml isnt used
#user    = <uid>
#pwd     = <password>
#factor2 = <2nd factor>
#vc      = <vendor code>
#apikey  = <secret key>
#imei    = <imei>

#ret = api.login(userid = user, password = pwd, twoFA=factor2, vendor_code=vc, api_secret=apikey, imei=imei)

#yaml for parameters
with open('cred.yml') as f:
    cred = yaml.load(f, Loader=yaml.FullLoader)
    print(cred)

ret = api.login(userid = cred['user'], password = cred['pwd'], twoFA=cred['factor2'], vendor_code=cred['vc'], api_secret=cred['apikey'], imei=cred['imei'])

if ret != None:   
    while True:  
        print('m => get quotes')
        print('p => contract info n properties')    
        print('q => quit')

        prompt1=input('what shall we do? ').lower()                    
        

        if prompt1 == 'p':
            exch  = 'NSE'
            token = '22'
            ret = api.get_security_info(exchange=exch, token=token)
            print(ret)

        elif prompt1 == 'm':
            exch  = 'NSE'
            token = '22'
            ret = api.get_quotes(exchange=exch, token=token)
            print(ret)

        else:
            ret = api.logout()
            print(ret)
            print('Fin') #an answer that wouldn't be yes or no
            break

    
