# NorenApi

Api used to connect to NorenOMS
****

## Build

to build this package and install it on your server please use 

``` pip install -r requirements.txt ```


****

## API 
```NorenApi```
- [login](#md-login)
- [logout](#md-logout)

Symbols
- [get_security_info](#md-get_security_info)
- [get_quotes](#md-get_quotes)
- [get_clients](#md-get_clients)

Orders and Trades
- [place_order](#md-place_order)
- [modify_order](#md-modify_order)
- [cancel_order](#md-cancel_order)
- [exit_order](#md-exit_order)
- [get_orderbook](#md-get_orderbook)
- [get_tradebook](#md-get_tradebook)

Holdings and Limits
- [get_positions](#md-get_positions)

Example
- [getting started](#md-example-basic)
- [Market Functions](#md-example-market)
- [Orders and Trade](#md-example-orders)

#### <a name="md-login"></a> login(userid, password, twoFA, vendor_code, api_secret, imei)
connect to the broker, only once this function has returned successfully can any other operations be performed
Example: 
```
#credentials
user    = <uid>
pwd     = <password>
factor2 = <2nd factor>
vc      = <vendor code>
app_key = <secret key>
imei    = <imei>

ret = api.login(userid=uid, password=pwd, twoFA=factor2, vendor_code=vc, api_secret=app_key, imei=imei)
```
Request Details :

|Json Fields|Possible value|Description|
| --- | --- | ---|
|apkversion*||Application version.|
|uid*||User Id of the login user|
|pwd*||Sha256 of the user entered password.|
|factor2*||DOB or PAN as entered by the user. (DOB should be in DD-MM-YYYY)|
|vc*||Vendor code provided by noren team, along with connection URLs|
|appkey*||Sha256 of  uid|vendor_key|
|imei*||Send mac if users logs in for desktop, imei is from mobile|
|addldivinf||Optional field, Value must be in below format:|iOS - iosInfo.utsname.machine - iosInfo.systemVersion|Android - androidInfo.model - androidInfo.version|examples:|iOS - iPhone 8.0 - 9.0|Android - Moto G - 9 PKQ1.181203.01|
|ipaddr||Optional field|
|source|API||


Response Details :


|Json Fields|Possible value|Description|
| --- | --- | ---|
|stat|Ok or Not_Ok|Login Success Or failure status|
|susertoken||It will be present only on login success. This data to be sent in subsequent requests in jKey field and web socket connection while connecting. |
|lastaccesstime||It will be present only on login success.|
|spasswordreset|Y |If Y Mandatory password reset to be enforced. Otherwise the field will be absent.|
|exarr||Json array of strings with enabled exchange names|
|uname||User name|
|prarr||Json array of Product Obj with enabled products, as defined below.|
|actid||Account id|
|email||Email Id|
|brkname||Broker id|
|emsg||This will be present only if Login fails.|(Redirect to force change password if message is “Invalid Input : Password Expired” or “Invalid Input : Change Password”)|


Sample Success Response :
{
    "request_time": "20:18:47 19-05-2020",
    "stat": "Ok",
    "susertoken": "3b97f4c67762259a9ded6dbd7bfafe2787e662b3870422ddd343a59895f423a0",
    "lastaccesstime": "1589899727"
}

Sample Failure Response :
{
    "request_time": "20:32:14 19-05-2020",
    "stat": "Not_Ok",
    "emsg": "Invalid Input : Wrong Password"
}

#### <a name="md-logout"></a> logout()
Terminate the session

Example: 
```
ret = api.logout()
```

Request Details :

|Json Fields|Possible value|Description|
| --- | --- | ---|
|uid*||User Id of the login user|

Response Details :
Response data will be in json format with below fields.
|Json Fields|Possible value|Description|
| --- | --- | ---|
|stat|Ok or Not_Ok|Logout Success Or failure status|
|request_time||It will be present only on successful logout.|
|emsg||This will be present only if Logout fails.|

Sample Success Response :
{
   "stat":"Ok",
   "request_time":"10:43:41 28-05-2020"
}

Sample Failure Response :
{
   "stat":"Not_Ok",
   "emsg":"Server Timeout :  "
}


#### <a name="md-place_order"></a> place_order(buy_or_sell, product_type,exchange, tradingsymbol, quantity, discloseqty, price_type, price=0.0, trigger_price=None, retention='DAY', amo='NO', remarks=None)
place an order to oms

Example: 

```
ret = api.place_order(buy_or_sell='B', product_type='C',
                        exchange='NSE', tradingsymbol='CANBK-EQ', 
                        quantity=1, discloseqty=0,price_type='SL-LMT', price=200.00, trigger_price=199.50,
                        retention='DAY', remarks='my_order_001')
```
Request Details :

|Json Fields|Possible value|Description|
| --- | --- | ---|
|uid*||Logged in User Id|
|actid*||Login users account ID|
|exch*|NSE  / NFO / BSE / MCX|Exchange (Select from ‘exarr’ Array provided in User Details response)|
|tsym*||Unique id of contract on which order to be placed. (use url encoding to avoid special char error for symbols like M&M)|
|qty*||Order Quantity |
|prc*||Order Price|
|trgprc||Only to be sent in case of SL / SL-M order.|
|dscqty||Disclosed quantity (Max 10% for NSE, and 50% for MCX)|
|prd*|C / M / H|Product name (Select from ‘prarr’ Array provided in User Details response, and if same is allowed for selected, exchange. Show product display name, for user to select, and send corresponding prd in API call)|
|trantype*|B / S|B -> BUY, S -> SELL|
|prctyp*|LMT / MKT  / SL-LMT / SL-MKT / DS / 2L / 3L||||
|ret*|DAY / EOS / IOC |Retention type (Show options as per allowed exchanges) |
|remarks||Any tag by user to mark order.|
|ordersource|MOB / WEB / TT |Used to generate exchange info fields.|
|bpprc||Book Profit Price applicable only if product is selected as B (Bracket order ) |
|blprc||Book loss Price applicable only if product is selected as H and B (High Leverage and Bracket order ) |
|trailprc||Trailing Price applicable only if product is selected as H and B (High Leverage and Bracket order ) |
|amo||Yes , If not sent, of Not “Yes”, will be treated as Regular order. |
|tsym2||Trading symbol of second leg, mandatory for price type 2L and 3L (use url encoding to avoid special char error for symbols like M&M)|
|trantype2||Transaction type of second leg, mandatory for price type 2L and 3L|
|qty2||Quantity for second leg, mandatory for price type 2L and 3L|
|prc2||Price for second leg, mandatory for price type 2L and 3L|
|tsym3||Trading symbol of third leg, mandatory for price type 3L (use url encoding to avoid special char error for symbols like M&M)|
|trantype3||Transaction type of third leg, mandatory for price type 3L|
|qty3||Quantity for third leg, mandatory for price type 3L|
|prc3||Price for third leg, mandatory for price type 3L|


Response Details :

Response data will be in json format with below fields.

|Json Fields|Possible value|Description|
| --- | --- | ---|
|stat|Ok or Not_Ok|Place order success or failure indication.|
|request_time||Response received time.|
|norenordno||It will be present only on successful Order placement to OMS.|
|emsg||This will be present only if Order placement fails|

Sample Success Response:
{
    "request_time": "10:48:03 20-05-2020",
    "stat": "Ok",
    "norenordno": "20052000000017"
}

Sample Error Response :
{
    "stat": "Not_Ok",
    "request_time": "20:40:01 19-05-2020",
    "emsg": "Error Occurred : 2 \"invalid input\""
}

#### <a name="md-modify_order"></a> modify_order(orderno, exchange, tradingsymbol, newquantity,newprice_type, newprice, newtrigger_price, amo):
modify the quantity pricetype or price of an order

Example: 

```
orderno = ret['norenordno'] #from placeorder return value
ret = api.modify_order(exchange='NSE', tradingsymbol='CANBK-EQ', orderno=orderno,
                                   newquantity=2, newprice_type='MKT', newprice=0.00)
## sl modification
ret = api.modify_order(exchange='NSE', tradingsymbol='CANBK-EQ', orderno=orderno,
                                   newquantity=2, newprice_type='SL-LMT', newprice=201.00, newtrigger_price=200.00)
```

Request Details :

|Json Fields|Possible value|Description|
| --- | --- | ---|
|exch*||Exchange|
|norenordno*||Noren order number, which needs to be modified|
|prctyp|LMT / MKT / SL-MKT / SL-LMT|This can be modified.|
|prc||Modified / New price|
|qty||Modified / New Quantity||Quantity to Fill / Order Qty - This is the total qty to be filled for the order. Its Open Qty/Pending Qty plus Filled Shares (cumulative for the order) for the order.|* Please do not send only the pending qty in this field|
|tsym*||Unque id of contract on which order was placed. Can’t be modified, must be the same as that of original order. (use url encoding to avoid special char error for symbols like M&M)|
|ret|DAY / IOC / EOS|New Retention type of the order |
||||
|trgprc||New trigger price in case of SL-MKT or SL-LMT|
|uid*||User id of the logged in user.|
|bpprc||Book Profit Price applicable only if product is selected as B (Bracket order ) |
|blprc||Book loss Price applicable only if product is selected as H and B (High Leverage and Bracket order ) |
|trailprc||Trailing Price applicable only if product is selected as H and B (High Leverage and Bracket order ) |

Response Details :

Response data will be in json format with below fields.

|Json Fields|Possible value|Description|
| --- | --- | ---|
|stat|Ok or Not_Ok|Modify order success or failure indication.|
|result||Noren Order number of the order modified.|
|request_time||Response received time.|
|emsg||This will be present only if Order modification fails|

Sample Success Response :
{
     "request_time":"14:14:08 26-05-2020",
     "stat":"Ok",
     "result":"20052600000103"
}

Sample Failure Response :
{
   "request_time":"16:03:29 28-05-2020",
   "stat":"Not_Ok",
   "emsg":"Rejected : ORA:Order not found"
}

#### <a name="md-cancel_order"></a> cancel_order(orderno)
cancel an order

Example:

```
orderno = ret['norenordno'] #from placeorder return value
ret = api.cancel_order(orderno=orderno)
```

Request Details :

|Json Fields|Possible value|Description|
| --- | --- | ---|
|norenordno*||Noren order number, which needs to be modified|
|uid*||User id of the logged in user.|

Response Details :

Response data will be in json format with below fields.

|Json Fields|Possible value|Description|
| --- | --- | ---|
|stat|Ok or Not_Ok|Cancel order success or failure indication.|
|result||Noren Order number of the canceled order.|
|request_time||Response received time.|
|emsg||This will be present only if Order cancelation fails|

Sample Success Response :
{
   "request_time":"14:14:10 26-05-2020",
   "stat":"Ok",
   "result":"20052600000103"
}

Sample Failure Response :
{
   "request_time":"16:01:48 28-05-2020",
   "stat":"Not_Ok",
   "emsg":"Rejected : ORA:Order not found to Cancel"
}


#### <a name="md-exit_order"></a> exit_order(orderno)
exits a cover or bracket order

Request Details :

|Json Fields|Possible value|Description|
| --- | --- | ---|
|norenordno*||Noren order number, which needs to be modified|
|prd*|H / B |Allowed for only H and B products (Cover order and bracket order)|
|uid*||User id of the logged in user.|

Response Details :

Response data will be in json format with below fields.

|Json Fields|Possible value|Description|
| --- | --- | ---|
|stat|Ok or Not_Ok|Cancel order success or failure indication.|
|dmsg||Display message, (will be present only in case of success).|
|request_time||Response received time.|
|emsg||This will be present only if Order cancelation fails|


#### <a name="md-get_orderbook"></a>  Order Book
List of Orders placed for the account

Example :
```
ret = api.get_order_book()
print(ret)
```
Request Details :

|Json Fields|Possible value|Description|
| --- | --- | ---|
|uid*||Logged in User Id|
|prd|H / M / ...|Product name|

Response Details :

Response data will be in json Array of objects with below fields in case of success.

|Json Fields|Possible value|Description|
| --- | --- | ---|
|stat|Ok or Not_Ok|Order book success or failure indication.|
|exch||Exchange Segment|
|tsym||Trading symbol / contract on which order is placed.|
|norenordno||Noren Order Number|
|prc||Order Price|
|qty||Order Quantity|
|prd||Display product alias name, using prarr returned in user details.|
|status|||
|trantype|B / S|Transaction type of the order|
|prctyp|LMT / MKT|Price type|
|fillshares||Total Traded Quantity of this order|
|avgprc||Average trade price of total traded quantity |
|rejreason||If order is rejected, reason in text form|
|exchordid||Exchange Order Number|
|cancelqty||Canceled quantity for order which is in status cancelled.|
|remarks||Any message Entered during order entry.|
|dscqty||Order disclosed quantity.|
|trgprc||Order trigger price|
|ret|DAY / IOC / EOS|Order validity|
|uid|||
|actid|||
|bpprc||Book Profit Price applicable only if product is selected as B (Bracket order ) |
|blprc||Book loss Price applicable only if product is selected as H and B (High Leverage and Bracket order ) |
|trailprc||Trailing Price applicable only if product is selected as H and B (High Leverage and Bracket order ) |
|amo||Yes / No|
|pp||Price precision|
|ti||Tick size|
|ls||Lot size|
|token||Contract Token|
|norentm|||
|ordenttm|||
|exch_tm|||
|snoordt||0 for profit leg and 1 for stoploss leg|
|snonum||This field will be present for product H and B; and only if it is profit/sl order.|

Response data will be in json format with below fields in case of failure:

|Json Fields|Possible value|Description|
| --- | --- | ---|
|stat|Not_Ok|Order book failure indication.|
|request_time||Response received time.|
|emsg||Error message|

Sample Success Output :
Success response :
[
      {
“stat” : “Ok”,
“exch” : “NSE” ,
“tsym” : “ACC-EQ” ,
“norenordno” : “20062500000001223”,
               “prc” : “127230”,
               “qty” : “100”,
               “prd” : “C”,
“status”: “Open”,
               “trantype” : “B”,
 “prctyp” : ”LMT”,
               “fillshares” : “0”,
               “avgprc” : “0”,
“exchordid” : “250620000000343421”,
 “uid” : “VIDYA”, 
 “actid” : “CLIENT1”,
 “ret” : “DAY”,
 “amo” : “Yes”
     },
    {
“stat” : “Ok”,
“exch” : “NSE” ,
“tsym” : “ABB-EQ” ,
“norenordno” : “20062500000002543”,
               “prc” : “127830”,
            “qty” : “50”,
               “prd” : “C”,
“status”: “REJECT”,
              “trantype” : “B”,
“prctyp” : ”LMT”,
             “fillshares” : “0”,
             “avgprc” : “0”,
              “rejreason” : “Insufficient funds”
“uid” : “VIDYA”, 
“actid” : “CLIENT1”,
“ret” : “DAY”,
“amo” : “No”
    }
]

Sample Failure Response :
{
   "stat":"Not_Ok",
   "emsg":"Session Expired : Invalid Session Key"
}

#### <a name="md-get_tradebook"></a>  Trade Book 
List of Trades of the account

Example:
```
ret = api.get_trade_book()
print(ret)
```

Request Details :

|Json Fields|Possible value|Description|
| --- | --- | ---|
|uid*||Logged in User Id|

Response Details :

Response data will be in json Array of objects with below fields in case of success.

|Json Fields|Possible value|Description|
| --- | --- | ---|
|stat|Ok or Not_Ok|Order book success or failure indication.|
|exch||Exchange Segment|
|tsym||Trading symbol / contract on which order is placed.|
|norenordno||Noren Order Number|
|qty||Order Quantity|
|prd||Display product alias name, using prarr returned in user details.|
|trantype|B / S|Transaction type of the order|
|prctyp|LMT / MKT|Price type|
|fillshares||Total Traded Quantity of this order|
|avgprc||Average trade price of total traded quantity |
|exchordid||Exchange Order Number|
|remarks||Any message Entered during order entry.|
|ret|DAY / IOC / EOS|Order validity|
|uid|||
|actid|||
|pp||Price precision|
|ti||Tick size|
|ls||Lot size|
|cstFrm||Custom Firm|
|fltm||Fill Time|
|flid||Fill ID|
|flqty||Fill Qty|
|flprc||Fill Price|
|ordersource||Order Source|
|token||Token|

Response data will be in json format with below fields in case of failure:

|Json Fields|Possible value|Description|
| --- | --- | ---|
|stat|Not_Ok|Order book failure indication.|
|request_time||Response received time.|
|emsg||Error message|

Sample Success Output :

[
   {
       "stat": "Ok",
       "norenordno": "20121300065715",
       "uid": "GURURAJ",
       "actid": "GURURAJ",
       "exch": "NSE",
       "prctyp": "LMT",
       "ret": "DAY",
       "prd": "M",
       "flid": "102",
       "fltm": "01-01-1980 00:00:00",
       "trantype": "S",
       "tsym": "ACCELYA-EQ",
       "qty": "180",
       "token": "7053",
       "fillshares": "180",
       "flqty": "180",
       "pp": "2",
       "ls": "1",
       "ti": "0.05",
       "prc": "800.00",
       "flprc": "800.00",
       "norentm": "19:59:32 13-12-2020",
       "exch_tm": "00:00:00 01-01-1980",
       "remarks": "WC TEST Order",
       "exchordid": "6857"
   },
   {
       "stat": "Ok",
       "norenordno": "20121300065716",
       "uid": "GURURAJ",
       "actid": "GURURAJ",
       "exch": "NSE",
       "prctyp": "LMT",
       "ret": "DAY",
       "prd": "M",
       "flid": "101",
       "fltm": "01-01-1980 00:00:00",
       "trantype": "B",
       "tsym": "ACCELYA-EQ",
       "qty": "180",
       "token": "7053",
       "fillshares": "180",
       "flqty": "180",
       "pp": "2",
       "ls": "1",
       "ti": "0.05",
       "prc": "800.00",
       "flprc": "800.00",
       "norentm": "19:59:32 13-12-2020",
       "exch_tm": "00:00:00 01-01-1980",
       "remarks": "WC TEST Order",
       "exchordid": "6858"
   }
]

#### <a name="md-get_positions"></a> get_positions()

retrieves the overnight and day positions as a list

Example: 
```
ret = api.get_positions()
mtm = 0
pnl = 0
for i in ret:
    mtm += float(i['urmtom'])
    pnl += float(i['rpnl'])
    day_m2m = mtm + pnl
print(f'{day_m2m} is your Daily MTM')
```

Request Details :

|Json Fields|Possible value|Description|
| --- | --- | ---|
|uid*||Logged in User Id|

Response Details :

Response data will be in json format with Array of Objects with below fields in case of success.

|Json Fields|Possible value|Description|
| --- | --- | ---|
|stat|Ok or Not_Ok|Position book success or failure indication.|
|exch||Exchange segment|
|tsym||Trading symbol / contract.|
|token||Contract token|
|uid||User Id|
|actid||Account Id|
|prd||Product name to be shown.|
|daybuyqty||Day Buy Quantity|
|daysellqty||Day Sell Quantity|
|daybuyamt||Day Buy Amount|
|daysellamt||Day Sell Amount|
|cfbuyqty||Carry Forward Buy Quantity|
|cfsellqty||Carry Forward Sell Quantity|
|cfbuyamt||Carry Forward Buy Amount|
|cfsellamt||Carry Forward Sell Amount|
|openbuyqty||Open Buy Quantity|
|opensellqty||Open Sell Quantity|
|openbuyamt||Open Buy Amount|
|opensellamt||Open Sell Amount|
|instname||Instrument Name|
|upload_prc||Upload Price|
|Child_orders||Array Object,|

child_orders Obj format
|Json Fields|Possible value|Description|
| --- | --- | ---|
|exch||Exchange segment|
|token||Contract token|
|daybuyqty||Day Buy Quantity|
|daysellqty||Day Sell Quantity|
|daybuyamt||Day Buy Amount|
|daysellamt||Day Sell Amount|
|cfbuyqty||CF Buy Quantity|
|cfsellqty||CF Sell Quantity|
|cfbuyamt||CF Buy Amount|
|cfsellamt||CF Sell Amount
|openbuyqty||Open Buy Quantity|
|opensellqty||Open Sell Quantity|
|openbuyamt||Open Buy Amount|
|opensellamt||Open Sell Amount|
|upload_prc||Upload Price|


Response data will be in json format with below fields in case of failure:

|Json Fields|Possible value|Description|
| --- | --- | ---|
|stat|Not_Ok|Position book request failure indication.|
|request_time||Response received time.|
|emsg||Error message|


Sample Success Response :
[
{
"stat":"Ok",
"actid":"TESTINV1",
"exch":"EQT",
"token":"PRAKASH",
"prd":"I",
"openbuyqty":"00",
"opensellqty":"09",
"openbuyamt":"00",
"opensellamt":"54000",
"daybuyqty":"01",
"daysellqty":"01",
"daybuyamt":"6000",
"daysellamt":"6000",
"cfbuyqty":"00",
"cfsellqty":"00",
"cfbuyamt":"00",
"cfsellamt":"6000",
"child_orders":[
                {
                "exch":"NSE",
                "token":"2708",
                "openbuyqty":"00",
                "opensellqty":"09",
                "openbuyamt":"00",
                "opensellamt":"54000",
                "daybuyqty":"00",
                "daysellqty":"01",
                "daybuyamt":"00",
                "daysellamt":"6000",
                "cfbuyqty":"00",
                "cfsellqty":"00",
                "cfbuyamt":"00",
                "cfsellamt":"00",
                "upload_prc":"00"
                },
                {
                "exch":"BSE",
                "token":"506022",
                "openbuyqty":"00",
                "opensellqty":"00",
                "openbuyamt":"00",
                "opensellamt":"00",
                "daybuyqty":"01",
                "daysellqty":"00",
                "daybuyamt":"6000",
                "daysellamt":"00",
                "cfbuyqty":"00",
                "cfsellqty":"00",
                "cfbuyamt":"00",
                "cfsellamt":"00",
                "upload_prc":"00"
                }
                ]
}
]
Sample Failure Response :
{
    "stat":"Not_Ok",
    "request_time":"14:14:11 26-05-2020",
    "emsg":"Error Occurred : 5 \"no data\""
}


#### <a name="md-get_security_info"></a> get_security_info(exchange, token):
gets the complete details and its properties 

Example:
```
exch  = 'NSE'
token = '22'
ret = api.get_security_info(exchange=exch, token=token)
```
Request Details :

|Json Fields|Possible value|Description|
| --- | --- | ---|
|uid*||Logged in User Id|
|exch||Exchange |
|token||Contract Token|

Response Details :

Response data will have below fields.

|Json Fields|Possible value|Description|
| --- | --- | ---|
|request_time||It will be present only in a successful response.|
|stat|Ok or Not_Ok|Market watch success or failure indication.|
|exch|NSE, BSE, NFO ...|Exchange |
|tsym||Trading Symbol|
|cname||Company Name|
|symnam||Symbol Name|
|seg||Segment|
|exd||Expiry Date|
|instname||Intrument Name|
|strprc||Strike Price |
|optt||Option Type|
|isin||ISIN|
|ti ||Tick Size |
|ls||Lot Size |
|pp||Price precision|
|mult||Multiplier|
|gp_nd||gn/gd * pn/pd|
|prcunt||Price Units |
|prcqqty||Price Quote Qty|
|trdunt||Trade Units   |
|delunt||Delivery Units|
|frzqty||Freeze Qty|
|gsmind||scripupdate   Gsm Ind|
|elmbmrg||Elm Buy Margin|
|elmsmrg||Elm Sell Margin|
|addbmrg||Additional Long Margin|
|addsmrg||Additional Short Margin|
|splbmrg||Special Long Margin    |
|splsmrg||Special Short Margin|
|delmrg||Delivery Margin |
|tenmrg||Tender Margin|
|tenstrd||Tender Start Date|
|tenendd||Tender End Eate|
|exestrd||Exercise Start Date|
|exeendd||Exercise End Date |
|elmmrg||Elm Margin |
|varmrg||Var Margin |
|expmrg||Exposure Margin|
|token||Contract Token  |
|prcftr_d||((GN / GD) * (PN/PD))|

Sample Success Response :
{
      "request_time": "17:43:38 31-10-2020",
       "stat": "Ok",
   "exch": "NSE",
   "tsym": "ACC-EQ",
   "cname": "ACC LIMITED",
   "symname": "ACC",
   "seg": "EQT",
   "instname": "EQ",
   "isin": "INE012A01025",
   "pp": "2",
   "ls": "1",
   "ti": "0.05",
   "mult": "1",
   "prcftr_d": "(1 / 1 ) * (1 / 1)",
   "trdunt": "",
   "delunt": "ACC",
   "token": "22",
   "varmrg": "40.00"
}

Sample Failure Response :
{
    "stat":"Not_Ok",
    "request_time":"10:50:54 10-12-2020",
    "emsg":"Error Occurred : 5 \"no data\""
}

#### <a name="md-get_quotes"></a> get_quotes(exchange, token):
gets the complete details and its properties 

Example: 
```
exch  = 'NSE'
token = '22'
ret = api.get_quotes(exchange=exch, token=token)
```

Request Details :

|Json Fields|Possible value|Description|
| --- | --- | ---|
|uid*||Logged in User Id|
|exch||Exchange |
|token||Contract Token|

Response Details :

Response data will be in json format with below fields.

|Json Fields|Possible value|Description|
| --- | --- | ---|
|stat|Ok or Not_Ok|Watch list update success or failure indication.|
|request_time||It will be present only in a successful response.|
|exch|NSE, BSE, NFO ...|Exchange |
|tsym||Trading Symbol|
|cname||Company Name|
|symname||Symbol Name|
|seg||Segment|
|instname||Instrument Name|
|isin||ISIN|
|pp||Price precision|
|ls||Lot Size |
|ti||Tick Size |
|mult||Multiplier|
|uc||Upper circuit limitlc|
|lc||Lower circuit limit|
|prcftr_d||Price factor|((GN / GD) * (PN/PD))|
|token||Token|
|lp||LTP|
|o||Open Price|
|h||Day High Price|
|l||Day Low Price|
|v||Volume|
|ltq||Last trade quantity|
|ltt||Last trade time|
|bp1||Best Buy Price 1|
|sp1||Best Sell Price 1|
|bp2||Best Buy Price 2|
|sp2||Best Sell Price 2|
|bp3||Best Buy Price 3|
|sp3||Best Sell Price 3|
|bp4||Best Buy Price 4|
|sp4||Best Sell Price 4|
|bp5||Best Buy Price 5|
|sp5||Best Sell Price 5|
|bq1||Best Buy Quantity 1|
|sq1||Best Sell Quantity 1|
|bq2||Best Buy Quantity 2|
|sq2||Best Sell Quantity 2|
|bq3||Best Buy Quantity 3|
|sq3||Best Sell Quantity 3|
|bq4||Best Buy Quantity 4|
|sq4||Best Sell Quantity 4|
|bq5||Best Buy Quantity 5|
|sq5||Best Sell Quantity 5|
|bo1||Best Buy Orders 1|
|so1||Best Sell Orders 1|
|bo2||Best Buy Orders 2|
|so2||Best Sell Orders 2|
|bo3||Best Buy Orders 3|
|so3||Best Sell Orders 3|
|bo4||Best Buy Orders 4|
|so4||Best Sell Orders 4|
|bo5||Best Buy Orders 5|
|so5||Best Sell Orders 5|


Sample Success Response :
{
    "request_time":"12:05:21 18-05-2021",
"stat":"Ok"
,"exch":"NSE",
"tsym":"ACC-EQ",
"cname":"ACC LIMITED",
"symname":"ACC",
"seg":"EQT",
"instname":"EQ",
"isin":"INE012A01025",
"pp":"2",
"ls":"1",
"ti":"0.05",
"mult":"1",
"uc":"2093.95",
"lc":"1713.25",
"prcftr_d":"(1 / 1 ) * (1 / 1)",
"token":"22",
"lp":"0.00",
"h":"0.00",
"l":"0.00",
"v":"0",
"ltq":"0",
"ltt":"05:30:00",
"bp1":"2000.00",
"sp1":"0.00",
"bp2":"0.00",
"sp2":"0.00",
"bp3":"0.00",
"sp3":"0.00",
"bp4":"0.00",
"sp4":"0.00",
"bp5":"0.00",
"sp5":"0.00",
"bq1":"2",
"sq1":"0",
"bq2":"0",
"sq2":"0",
"bq3":"0",
"sq3":"0",
"bq4":"0",
"sq4":"0",
"bq5":"0",
"sq5":"0",
"bo1":"2",
"so1":"0",
"bo2":"0",
"so2":"0",
"bo3":"0",
"so3":"0",
"bo4":"0",
"so4":"0",
"bo5":"0",
"So5":"0"
}

Sample Failure Response :
{
    "stat":"Not_Ok",
    "request_time":"10:50:54 10-12-2020",
    "emsg":"Error Occurred : 5 \"no data\""
}


#### <a name="md-get_clients"></a> get_clients():

Example: 
```
ret = api.get_clients()
```

Request Details :

|Json Fields|Possible value|Description|
| --- | --- | ---|
|uid*||Logged in User Id|

Response Details :

Response data will be in json format with below fields.

|Json Fields|Possible value|Description|
| --- | --- | ---|
|stat|Ok or Not_Ok|Watch list update success or failure indication.|
|request_time||Requested Time|
|entities||Json array of strings with account id and exch ist |
|emsg||This will be present only in case of errors. |

entities Obj format
|Json Fields|Possible value|Description|
| --- | --- | ---|
|exch||Exchange name|
|part_id||Part Id|

Sample Success Response :
{
"stat": "Ok",
"request_time": "09:49:37 19-07-2022",
"entities": [
{
"acct_id": "GURURAJ",
"exch_list": [
{
"exch": "CDS",
"part_id": ""
},
{
"exch": "NSE","part_id": ""
},
{
"exch": "NFO",
"part_id": ""
},
{
"exch": "MCX",
"part_id": ""
},
{
"exch": "BSE",
"part_id": ""
},
{
"exch": "NCX",
"part_id": ""
},
{
"exch": "BSTAR",
"part_id": ""
},
{
"exch": "BCD",
"part_id": ""
}
]
},
{
"acct_id": "CLINV1",
"exch_list": [
{
"exch": "NSE",
"part_id": ""
},
{
"exch": "BSE",
"part_id": ""
}
]
},
{"acct_id": "1T012",
"exch_list": []
},
{
"acct_id": "CH005",
"exch_list": [
{
"exch": "NSE",
"part_id": ""
},
{
"exch": "BSE",
"part_id": ""
}
]
}
]
}

Sample Failure Response :
{
"stat": "Not_Ok",
"emsg": "Session Expired : Invalid Session Key"
}

****
## <a name="md-example-basic"></a> Example - Getting Started
First configure the endpoints in the api_helper constructor. 
Thereon provide your credentials and login as follows.

```python
from api_helper import NorenApiPy
import logging

#enable dbug to see request and responses
logging.basicConfig(level=logging.DEBUG)

#start of our program
api = NorenApiPy()

#credentials
user        = '< user id>'
u_pwd       = '< password >'
factor2     = 'second factor'
vc          = 'vendor code'
app_key     = 'secret key'
imei        = 'uniq identifier'


ret = api.login(userid=user, password=pwd, twoFA=factor2, vendor_code=vc, api_secret=app_key, imei=imei)
print(ret)
```

## <a name="md-example-market"></a> Example Symbol/Contract : Example_market.py
This Example shows API usage for finding scrips and its properties

### Search Scrips
The call can be made to get the exchange provided token for a scrip or alternately can search for a partial string to get a list of matching scrips
Trading Symbol:

SymbolName + ExpDate + 'F' for all data having InstrumentName starting with FUT

SymbolName + ExpDate + 'P' + StrikePrice for all data having InstrumentName starting with OPT and with OptionType PE

SymbolName + ExpDate + 'C' + StrikePrice for all data having InstrumentName starting with OPT and with OptionType C

For MCX, F to be ignored for FUT instruments

```
api.searchscrip(exchange='NSE', searchtext='REL')
```
This will reply as following
```
{
    "stat": "Ok",
    "values": [
        {
            "exch": "NSE",
            "token": "18069",
            "tsym": "REL100NAV-EQ"
        },
        {
            "exch": "NSE",
            "token": "24225",
            "tsym": "RELAXO-EQ"
        },
        {
            "exch": "NSE",
            "token": "4327",
            "tsym": "RELAXOFOOT-EQ"
        },
        {
            "exch": "NSE",
            "token": "18068",
            "tsym": "RELBANKNAV-EQ"
        },
        {
            "exch": "NSE",
            "token": "2882",
            "tsym": "RELCAPITAL-EQ"
        },
        {
            "exch": "NSE",
            "token": "18070",
            "tsym": "RELCONSNAV-EQ"
        },
        {
            "exch": "NSE",
            "token": "18071",
            "tsym": "RELDIVNAV-EQ"
        },
        {
            "exch": "NSE",
            "token": "18072",
            "tsym": "RELGOLDNAV-EQ"
        },
        {
            "exch": "NSE",
            "token": "2885",
            "tsym": "RELIANCE-EQ"
        },
        {
            "exch": "NSE",
            "token": "15068",
            "tsym": "RELIGARE-EQ"
        },
        {
            "exch": "NSE",
            "token": "553",
            "tsym": "RELINFRA-EQ"
        },
        {
            "exch": "NSE",
            "token": "18074",
            "tsym": "RELNV20NAV-EQ"
        }
    ]
}
```
### Security Info
This call is done to get the properties of the scrip such as freeze qty and margins
```
api.get_security_info(exchange='NSE', token='22')
```
The response for the same would be 
```
{
   "request_time": "17:43:38 31-10-2020",
   "stat": "Ok",
   "exch": "NSE",
   "tsym": "ACC-EQ",
   "cname": "ACC LIMITED",
   "symname": "ACC",
   "seg": "EQT",
   "instname": "EQ",
   "isin": "INE012A01025",
   "pp": "2",
   "ls": "1",
   "ti": "0.05",
   "mult": "1",
   "prcftr_d": "(1 / 1 ) * (1 / 1)",
   "trdunt": "ACC.BO",
   "delunt": "ACC",
   "token": "22",
   "varmrg": "40.00"
}

```
### Subscribe to a live feed
Subscribe to a single token as follows

```
api.subscribe('NSE|13')
```

Subscribe to a list of tokens as follows
```
api.subscribe(['NSE|22', 'BSE|522032'])
```

First we need to connect to the WebSocket and then subscribe as follows
```
feed_opened = False

def event_handler_feed_update(tick_data):
    print(f"feed update {tick_data}")

def open_callback():
    global feed_opened
    feed_opened = True


api.start_websocket( order_update_callback=event_handler_order_update,
                     subscribe_callback=event_handler_feed_update, 
                     socket_open_callback=open_callback)

while(feed_opened==False):
    pass

# subscribe to a single token 
api.subscribe('NSE|13')

#subscribe to multiple tokens
api.subscribe(['NSE|22', 'BSE|522032'])
```
## <a name="md-example-orders"></a> Example - Orders and Trades : example_orders.py
### Place Order
    Place a Limit order as follows
```
    api.place_order(buy_or_sell='B', product_type='C',
                        exchange='NSE', tradingsymbol='INFY-EQ', 
                        quantity=1, discloseqty=0,price_type='LMT', price=1500, trigger_price=None,
                        retention='DAY', remarks='my_order_001')
```
    Place a Market Order as follows
```
    api.place_order(buy_or_sell='B', product_type='C',
                        exchange='NSE', tradingsymbol='INFY-EQ', 
                        quantity=1, discloseqty=0,price_type='MKT', price=0, trigger_price=None,
                        retention='DAY', remarks='my_order_001')
```
    Place a StopLoss Order as follows
```
    api.place_order(buy_or_sell='B', product_type='C',
                        exchange='NSE', tradingsymbol='INFY-EQ', 
                        quantity=1, discloseqty=0,price_type='SL-LMT', price=1500, trigger_price=1450,
                        retention='DAY', remarks='my_order_001')
```
    Place a Cover Order as follows
```
    api.place_order(buy_or_sell='B', product_type='H',
                        exchange='NSE', tradingsymbol='INFY-EQ', 
                        quantity=1, discloseqty=0,price_type='LMT', price=1500, trigger_price=None,
                        retention='DAY', remarks='my_order_001', bookloss_price = 1490)
```
    Place a Bracket Order as follows
```
    api.place_order(buy_or_sell='B', product_type='B',
                        exchange='NSE', tradingsymbol='INFY-EQ', 
                        quantity=1, discloseqty=0,price_type='LMT', price=1500, trigger_price=None,
                        retention='DAY', remarks='my_order_001', bookloss_price = 1490, bookprofit_price = 1510)
```
### Modify Order
    Modify a New Order by providing the OrderNumber
```
    api.modify_order(exchange='NSE', tradingsymbol='INFY-EQ', orderno=orderno,
                                   newquantity=2, newprice_type='LMT', newprice=1505)
```
### Cancel Order
    Cancel a New Order by providing the Order Number
```
    api.cancel_order(orderno=orderno)
```
### Subscribe to Order Updates

Connecting to the Websocket will automatically subscribe and provide the order updates in the call back as follows
Note: Feed and Order updates are received from the same websocket and needs to be connected once only.

```
feed_opened = False

def event_handler_order_update(order):
    print(f"order feed {order}")

def open_callback():
    global feed_opened
    feed_opened = True


api.start_websocket( order_update_callback=event_handler_order_update,
                     subscribe_callback=event_handler_feed_update, 
                     socket_open_callback=open_callback)

while(feed_opened==False):
    pass


```

****

## Author

Kumar Anand

****

## License

Copyright (C) 2021 Kambala Solutions Pvt Ltd- All Rights Reserved
Copying of this file, via any medium is strictly prohibited.
Proprietary and confidential.
All file transfers are logged.

****


