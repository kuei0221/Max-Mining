import requests
import json
import time
import hmac, hashlib, base64


url = "https://max-api.maicoin.com"

def __parse_response(res):
    if res is None:
        return None
    if res.status_code is 200:
        data = json.loads(res.text)
        return data
    else:
        print("error",res.status_code)
        print(res.text)

def GET(url,*args,**kwargs):
    try:
        res = requests.get(url,*args,**kwargs)
        return __parse_response(res)
    except requests.exceptions.ConnectionError:
        print("Failed to connect",url)
        return None
    except:
        raise


def POST(url,*args,**kwargs):
    try:
        res = requests.post(url,*args,**kwargs)
        return __parse_response(res)
    except requests.exceptions.ConnectionError:
        print("Failed to connect",url)
        return None
    except:
        raise

def quote(pair,depth=1):
    path = f"{url}/api/v2/depth"
    res = GET(path, data = dict({"market":pair, "limit":depth}))
    if res is not None:
        bid = float(res["bids"][0][0])
        res["asks"].reverse()
        ask = float(res["asks"][0][0])
        return {"bid":bid,"ask":ask}
    else:    
        return res
    pass
def refer_price(symbol):
    return GET("https://api.binance.com/api/v3/avgPrice",{"symbol":symbol})
   
############### Attribution of self-defined class "account" ###############

class account(object):
    """docstring for account"""
    def __init__(self,key,secret):
        self.key = key
        self.secret = secret

    # Pirvate api vertification process
    def verification(self,url):

        nonce =int(round(time.time()*1000))

        payload = {"path":url,"nonce":nonce}
        payload = json.dumps(payload).encode()
        payload = base64.b64encode(payload)
        
        signature = hmac.new(
        key=self.secret.encode(),
        msg=payload,
        digestmod=hashlib.sha256
        ).hexdigest()

        verification={"X-MAX-ACCESSKEY":self.key,"X-MAX-PAYLOAD":payload,"X-MAX-SIGNATURE":signature}
        
        return verification
    # Check wether the connection to exchange is fine
    def check(self):
    	path = f"{url}/api/v2/members/profile"
    	return GET(path,headers = self.verification(path))
    def checkorder(self,order_id):
        path = f"{url}/api/v2/order"
        return GET(path, headers = self.verification(path), data = {"id":order_id})
        pass
    # Get particular currency holding info
    def currency(self,symbol):
        path = f"{url}/api/v2/members/accounts/{symbol}"
        return GET(path,headers = self.verification(path))

    # Get current account holding. Only for those coin particpated Max-Mining.
    def balance(self, ex, base):
        ex_total = float(self.currency(ex)["balance"])
        base_total = float(self.currency(base)["balance"])
        max_total = float(self.currency("max")["balance"])
        return dict({ex:ex_total, base:base_total, "max":max_total})
    
    # Get current open orders of specific currency
    def holding(self, pair):
    	path = f"{url}/api/v2/orders"
    	return GET(path, headers = self.verification(path), data = {"market":pair})
        
    # Post an order
    def order(self, market, side, volume, ord_type, price="", stop_price=""):
        path = f"{url}/api/v2/orders"
        order = dict({
            "market":market,
            "side":side,
            "volume":volume,
            "price":price,
            "stop_price":stop_price,
            "ord_type":ord_type
            })
        return POST(path, headers = self.verification(path), data = order)

    # Delete all order in specific side & market
    def delete(self,market,side):
        path = f"{url}/api/v2/orders/clear"
        data = dict({"market":market,"side":side})
        return POST(path, headers = self.verification(path), data = data)

    # Clear Max holding while remain some of it
    def clearance(self, price, base = "usdt", remain=0.4):        
        amount = self.currency("max")["balance"]*(1-remain)
        return self.order(market = f"max{base}", side = "sell", volume = amount, ord_type = "limit", price = price)

    def address(self,symbol):
        path = f"{url}/api/v2/deposit_addresses"
        POST(path, headers = self.verification(path), data = {"currency":symbol})
        return GET(path, headers = self.verification(path), data = {"currency":symbol})
    pass

############### Attribution of self-defined class "
