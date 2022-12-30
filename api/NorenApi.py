import json
import requests
import threading
import websocket
import logging
import enum
import datetime
import hashlib
import time
import urllib
from time import sleep
from datetime import datetime as dt

logger = logging.getLogger(__name__)

class ProductType:
    Delivery = 'C'
    Intraday = 'I'
    Normal   = 'M'
    CF       = 'M'

class FeedType:
    TOUCHLINE = 1    
    SNAPQUOTE = 2
    
class PriceType:
    Market = 'MKT'
    Limit = 'LMT'
    StopLossLimit = 'SL-LMT'
    StopLossMarket = 'SL-MKT'

class BuyorSell:
    Buy = 'B'
    Sell = 'S'
    
def reportmsg(msg):
    #print(msg)
    logger.debug(msg)

def reporterror(msg):
    #print(msg)
    logger.error(msg)

def reportinfo(msg):
    #print(msg)
    logger.info(msg)

class NorenApi:
    __service_config = {
      'host': 'http://wsapihost/',
      'routes': {
          'authorize': '/QuickAuth',
          'logout': '/Logout',
          'placeorder': '/PlaceOrder',
          'modifyorder': '/ModifyOrder',
          'cancelorder': '/CancelOrder',
          'exitorder': '/ExitSNOOrder',
          'orderbook': '/OrderBook',
          'tradebook': '/TradeBook',          
          'positions': '/InteropPositionBook',
          'scripinfo': '/GetSecurityInfo',
          'getquotes': '/GetQuotes',
          'getclients': '/GetClients',
      },
      'websocket_endpoint': 'wss://wsendpoint/',
      'eoddata_endpoint' : 'http://eodhost/'
    }

    def __init__(self, host, websocket, eodhost):
        self.__service_config['host'] = host
        self.__service_config['websocket_endpoint'] = websocket
        self.__service_config['eoddata_endpoint'] = eodhost

        self.__websocket = None
        self.__websocket_connected = False
        self.__ws_mutex = threading.Lock()
        self.__on_error = None
        self.__on_disconnect = None
        self.__on_open = None
        self.__subscribe_callback = None
        self.__order_update_callback = None
        self.__subscribers = {}
        self.__market_status_messages = []
        self.__exchange_messages = []

    def __ws_run_forever(self):
        
        while self.__stop_event.is_set() == False:
            try:
                self.__websocket.run_forever( ping_interval=3,  ping_payload='{"t":"h"}')
            except Exception as e:
                logger.warning(f"websocket run forever ended in exception, {e}")
            
            sleep(0.1) # Sleep for 100ms between reconnection.

    def __ws_send(self, *args, **kwargs):
        while self.__websocket_connected == False:
            sleep(0.05)  # sleep for 50ms if websocket is not connected, wait for reconnection
        with self.__ws_mutex:
            ret = self.__websocket.send(*args, **kwargs)
        return ret

    def __on_close_callback(self, wsapp, close_status_code, close_msg):
        reportmsg(close_status_code)
        reportmsg(wsapp)

        self.__websocket_connected = False
        if self.__on_disconnect:
            self.__on_disconnect()

    def __on_open_callback(self, ws=None):
        self.__websocket_connected = True

        #prepare the data
        values              = { "t": "c" }
        values["uid"]       = self.__username        
        values["actid"]     = self.__username
        values["susertoken"]    = self.__susertoken
        values["source"]    = 'API'                

        payload = json.dumps(values)

        reportmsg(payload)
        self.__ws_send(payload)

        #self.__resubscribe()
        

    def __on_error_callback(self, ws=None, error=None):
        if(type(ws) is not websocket.WebSocketApp): # This workaround is to solve the websocket_client's compatiblity issue of older versions. ie.0.40.0 which is used in upstox. Now this will work in both 0.40.0 & newer version of websocket_client
            error = ws
        if self.__on_error:
            self.__on_error(error)

    def __on_data_callback(self, ws=None, message=None, data_type=None, continue_flag=None):
        #print(ws)
        #print(message)
        #print(data_type)
        #print(continue_flag)

        res = json.loads(message)

        if(self.__subscribe_callback is not None):
            if res['t'] == 'tk' or res['t'] == 'tf':
                self.__subscribe_callback(res)
                return
            if res['t'] == 'dk' or res['t'] == 'df':
                self.__subscribe_callback(res)
                return

        if(self.__on_error is not None):
            if res['t'] == 'ck' and res['s'] != 'OK':
                self.__on_error(res)
                return

        if(self.__order_update_callback is not None):
            if res['t'] == 'om':
                self.__order_update_callback(res)
                return

        if self.__on_open:
            if res['t'] == 'ck' and res['s'] == 'OK':
                self.__on_open()
                return


    def start_websocket(self, subscribe_callback = None, 
                        order_update_callback = None,
                        socket_open_callback = None,
                        socket_close_callback = None,
                        socket_error_callback = None):        
        """ Start a websocket connection for getting live data """
        self.__on_open = socket_open_callback
        self.__on_disconnect = socket_close_callback
        self.__on_error = socket_error_callback
        self.__subscribe_callback = subscribe_callback
        self.__order_update_callback = order_update_callback
        self.__stop_event = threading.Event()
        url = self.__service_config['websocket_endpoint'].format(access_token=self.__susertoken)
        reportmsg('connecting to {}'.format(url))

        self.__websocket = websocket.WebSocketApp(url,
                                                on_data=self.__on_data_callback,
                                                on_error=self.__on_error_callback,
                                                on_close=self.__on_close_callback,
                                                on_open=self.__on_open_callback)
        #th = threading.Thread(target=self.__send_heartbeat)
        #th.daemon = True
        #th.start()
        #if run_in_background is True:
        self.__ws_thread = threading.Thread(target=self.__ws_run_forever)
        self.__ws_thread.daemon = True
        self.__ws_thread.start()
        
    def close_websocket(self):
        if self.__websocket_connected == False:
            return
        self.__stop_event.set()        
        self.__websocket_connected = False
        self.__websocket.close()
        self.__ws_thread.join()

    def login(self, userid, password, twoFA, vendor_code, api_secret, imei):
        config = NorenApi.__service_config

        #prepare the uri
        url = f"{config['host']}{config['routes']['authorize']}" 
        reportmsg(url)

        #Convert to SHA 256 for password and app key
        pwd = hashlib.sha256(password.encode('utf-8')).hexdigest()
        u_app_key = '{0}|{1}'.format(userid, api_secret)
        app_key=hashlib.sha256(u_app_key.encode('utf-8')).hexdigest()
        #prepare the data
        values              = { "source": "API" , "apkversion": "1.0.0"}
        values["uid"]       = userid
        values["pwd"]       = pwd
        values["factor2"]   = twoFA
        values["vc"]        = vendor_code
        values["appkey"]    = app_key        
        values["imei"]      = imei        

        payload = 'jData=' + json.dumps(values)
        reportmsg("Req:" + payload)

        res = requests.post(url, data=payload)
        reportmsg("Reply:" + res.text)

        resDict = json.loads(res.text)
        if resDict['stat'] != 'Ok':            
            return None
        
        self.__username   = userid
        self.__accountid  = userid
        self.__password   = password
        self.__susertoken = resDict['susertoken']
        #reportmsg(self.__susertoken)

        return resDict

    def set_session(self, userid, password, usertoken):
        
        self.__username   = userid
        self.__accountid  = userid
        self.__password   = password
        self.__susertoken = usertoken

        reportmsg(f'{userid} session set to : {self.__susertoken}')

        return True

    def logout(self):
        config = NorenApi.__service_config

        #prepare the uri
        url = f"{config['host']}{config['routes']['logout']}" 
        reportmsg(url)
        #prepare the data
        values              = {'ordersource':'API'}
        values["uid"]       = self.__username
        
        payload = 'jData=' + json.dumps(values) + f'&jKey={self.__susertoken}'
        
        reportmsg(payload)

        res = requests.post(url, data=payload)
        reportmsg(res.text)

        resDict = json.loads(res.text)
        if resDict['stat'] != 'Ok':            
            return None

        self.__username   = None
        self.__accountid  = None
        self.__password   = None
        self.__susertoken = None

        return resDict

    def get_clients(self):
        config = NorenApi.__service_config

        #prepare the uri
        url = f"{config['host']}{config['routes']['getclients']}" 
        reportmsg(url)
        #prepare the data
        values              = {'ordersource':'API'}
        values["uid"]       = self.__username
        
        payload = 'jData=' + json.dumps(values) + f'&jKey={self.__susertoken}'
        
        reportmsg(payload)

        res = requests.post(url, data=payload)
        reportmsg(res.text)

        resDict = json.loads(res.text)
        if resDict['stat'] != 'Ok':            
            return None

        return resDict

    def place_order(self, act_id, buy_or_sell, product_type,
                    exchange, tradingsymbol, quantity, discloseqty,
                    price_type, price=0.0, trigger_price=None,
                    retention='DAY', amo='NO', remarks=None, bookloss_price = 0.0, bookprofit_price = 0.0, trail_price = 0.0):
        config = NorenApi.__service_config

        #prepare the uri
        url = f"{config['host']}{config['routes']['placeorder']}" 
        reportmsg(url)
        #prepare the data
        values              = {'ordersource':'API'}
        values["uid"]       = self.__username
        values["actid"]     = act_id
        values["trantype"]  = buy_or_sell
        values["prd"]       = product_type
        values["exch"]      = exchange
        values["tsym"]      = urllib.parse.quote_plus(tradingsymbol)
        values["qty"]       = str(quantity)
        values["dscqty"]    = str(discloseqty)        
        values["prctyp"]    = price_type
        values["prc"]       = str(price)
        values["trgprc"]    = str(trigger_price)
        values["ret"]       = retention
        values["remarks"]   = remarks
        values["amo"]       = amo
        
        #if cover order or high leverage order
        if product_type == 'H':            
            values["blprc"]       = str(bookloss_price)
            #trailing price
            if trail_price != 0.0:
                values["trailprc"] = str(trail_price)

        #bracket order
        if product_type == 'B':            
            values["blprc"]       = str(bookloss_price)
            values["bpprc"]       = str(bookprofit_price)
            #trailing price
            if trail_price != 0.0:
                values["trailprc"] = str(trail_price)

        payload = 'jData=' + json.dumps(values) + f'&jKey={self.__susertoken}'
        
        reportmsg(payload)

        res = requests.post(url, data=payload)
        reportmsg(res.text)

        resDict = json.loads(res.text)
        if resDict['stat'] != 'Ok':            
            return None

        return resDict

    def modify_order(self, orderno, exchange, tradingsymbol, newquantity,
                    newprice_type, newprice=0.0, newtrigger_price=None, bookloss_price = 0.0, bookprofit_price = 0.0, trail_price = 0.0):
        config = NorenApi.__service_config

        #prepare the uri
        url = f"{config['host']}{config['routes']['modifyorder']}" 
        print(url)

        #prepare the data
        values                  = {'ordersource':'API'}
        values["uid"]           = self.__username
        values["norenordno"]    = str(orderno)
        values["exch"]          = exchange
        values["tsym"]          = urllib.parse.quote_plus(tradingsymbol)
        values["qty"]           = str(newquantity)
        values["prctyp"]        = newprice_type        
        values["prc"]           = str(newprice)

        if (newprice_type == 'SL-LMT') or (newprice_type == 'SL-MKT'):
            if (newtrigger_price != None):
                values["trgprc"] = str(newtrigger_price)
            else:
                reporterror('trigger price is missing')
                return None

        #if cover order or high leverage order
        if bookloss_price != 0.0:            
            values["blprc"]       = str(bookloss_price)
        #trailing price
        if trail_price != 0.0:
            values["trailprc"] = str(trail_price)         
        #book profit of bracket order   
        if bookprofit_price != 0.0:
            values["bpprc"]       = str(bookprofit_price)
        
        payload = 'jData=' + json.dumps(values) + f'&jKey={self.__susertoken}'
        
        reportmsg(payload)

        res = requests.post(url, data=payload)
        reportmsg(res.text)

        resDict = json.loads(res.text)
        if resDict['stat'] != 'Ok':            
            return None

        return resDict

    def cancel_order(self, orderno):
        config = NorenApi.__service_config

        #prepare the uri
        url = f"{config['host']}{config['routes']['cancelorder']}" 
        print(url)

        #prepare the data
        values              = {'ordersource':'API'}
        values["uid"]       = self.__username
        values["norenordno"]    = str(orderno)
        
        payload = 'jData=' + json.dumps(values) + f'&jKey={self.__susertoken}'
        
        reportmsg(payload)

        res = requests.post(url, data=payload)
        print(res.text)

        resDict = json.loads(res.text)
        if resDict['stat'] != 'Ok':            
            return None

        return resDict

    def exit_order(self, orderno, product_type):
        config = NorenApi.__service_config

        #prepare the uri
        url = f"{config['host']}{config['routes']['exitorder']}" 
        print(url)

        #prepare the data
        values              = {'ordersource':'API'}
        values["uid"]       = self.__username
        values["norenordno"]    = orderno
        values["prd"]           = product_type
        
        payload = 'jData=' + json.dumps(values) + f'&jKey={self.__susertoken}'
        
        reportmsg(payload)

        res = requests.post(url, data=payload)
        reportmsg(res.text)

        resDict = json.loads(res.text)
        if resDict['stat'] != 'Ok':            
            return None

        return resDict

    def get_order_book(self):
        config = NorenApi.__service_config

        #prepare the uri
        url = f"{config['host']}{config['routes']['orderbook']}" 
        reportmsg(url)

        #prepare the data
        values              = {'ordersource':'API'}
        values["uid"]       = self.__username
        
        
        payload = 'jData=' + json.dumps(values) + f'&jKey={self.__susertoken}'
        
        reportmsg(payload)

        res = requests.post(url, data=payload)
        reportmsg(res.text)

        resDict = json.loads(res.text)
        
        #error is a json with stat and msg wchih we printed earlier.
        if type(resDict) != list:                            
                return None

        return resDict

    def get_trade_book(self):
        config = NorenApi.__service_config

        #prepare the uri
        url = f"{config['host']}{config['routes']['tradebook']}" 
        reportmsg(url)

        #prepare the data
        values              = {'ordersource':'API'}
        values["uid"]       = self.__username
        
        payload = 'jData=' + json.dumps(values) + f'&jKey={self.__susertoken}'
        
        reportmsg(payload)

        res = requests.post(url, data=payload)
        reportmsg(res.text)

        resDict = json.loads(res.text)
        
        #error is a json with stat and msg wchih we printed earlier.
        if type(resDict) != list:                            
                return None

        return resDict

    def get_security_info(self, exchange, token):
        config = NorenApi.__service_config

        #prepare the uri
        url = f"{config['host']}{config['routes']['scripinfo']}" 
        reportmsg(url)        
        
        values              = {}
        values["uid"]       = self.__username
        values["exch"]      = exchange
        values["token"]     = token       
        
        payload = 'jData=' + json.dumps(values) + f'&jKey={self.__susertoken}'
        
        reportmsg(payload)

        res = requests.post(url, data=payload)
        reportmsg(res.text)

        resDict = json.loads(res.text)

        if resDict['stat'] != 'Ok':            
            return None        

        return resDict

    def get_quotes(self, exchange, token):
        config = NorenApi.__service_config

        #prepare the uri
        url = f"{config['host']}{config['routes']['getquotes']}" 
        reportmsg(url)        
        
        values              = {}
        values["uid"]       = self.__username
        values["exch"]      = exchange
        values["token"]     = token       
        
        payload = 'jData=' + json.dumps(values) + f'&jKey={self.__susertoken}'
        
        reportmsg(payload)

        res = requests.post(url, data=payload)
        reportmsg(res.text)

        resDict = json.loads(res.text)

        if resDict['stat'] != 'Ok':            
            return None        

        return resDict
        
    def get_positions(self):
        config = NorenApi.__service_config

        #prepare the uri
        url = f"{config['host']}{config['routes']['positions']}" 
        reportmsg(url)        
        
        values              = {}
        values["uid"]       = self.__username
        
        payload = 'jData=' + json.dumps(values) + f'&jKey={self.__susertoken}'
        
        reportmsg(payload)

        res = requests.post(url, data=payload)
        reportmsg(res.text)

        resDict = json.loads(res.text)

        if type(resDict) != list:                            
            return None

        return resDict


