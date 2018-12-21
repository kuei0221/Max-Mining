
import hmac
import hashlib
import base64
import json
import requests
import time

# Quote data from MAX exchange
def ticker(pair,depth=1):
	#pair use small capital, and only twd no usd ex:"btctwd"
	res = requests.get("https://max-api.maicoin.com/api/v2/depth",{"market":pair,"limit":depth})

 	if res.status_code == requests.codes.ok:
 	
 		d = res.json()
 		bid = d["bids"][0][0]
 		bid=float(bid)
 		d["asks"].reverse()
		ask = d["asks"][0][0]
		ask=float(ask)
		info = {"bid":bid,"ask":ask}
		return info
	else:	
		return "ERROR"
 		pass
		pass
	pass

# Average price data from Binance exchange. Symbol should be Capital.
def price(symbol="BTCUSDT"):
	res=requests.get("https://api.binance.com/api/v3/avgPrice",{"symbol":symbol})
	price=float(res.json()["price"])
	return price
	pass

############### Attribution of self-defined class "account" ###############

## account stand for any information need private api access.
class account(object):
	"""docstring for account"""
	def __init__(self,key,secret,base,ex):
		self.key = key
		self.secret = secret
		self.base = base
		self.ex = ex
		self.pair="{}{}".format(ex,base)
	
	# Pirvate api vertification process
	def verification(self,url):

		nonce =int(round(time.time()*1000))

		payload = {"path":url,"nonce":nonce}
		payload = json.dumps(payload)
		payload = base64.b64encode(payload)
		
		signature = hmac.new(
	    key=self.secret,
	    msg=str(payload),
	    digestmod=hashlib.sha256
		).hexdigest()

		verification={"X-MAX-ACCESSKEY":self.key,"X-MAX-PAYLOAD":payload,"X-MAX-SIGNATURE":signature}
		
		return verification
		pass
	# Check wether the connection to exchange is fine
	def check(self):
		url="https://max-api.maicoin.com/api/v2/members/profile"
		res=requests.get(url,headers=self.verification(url))
		if res.status_code==requests.codes.ok:
			return "Connection Success"
		else:
			return "Connection Fail"
		pass
	# Get particular currency holding info
	def currency(self,symbol):
		url="{}{}".format("https://max-api.maicoin.com/api/v2/members/accounts/",symbol)
		res=requests.get(url,headers=self.verification(url))
		d=res.json()
		d=float(d["balance"])
		if res.status_code==requests.codes.ok:
			return d
		else:
			return "ERROR"
		pass
	# Get current account holding. Only for those coin particpated Max-Mining.
	def balance(self):
		ex=self.currency(self.ex)
		base=self.currency(self.base)
		max_=self.currency("max")
		return dict({self.ex:ex,self.base:base,"max":max_})
		pass
	# Get current open orders of specific currency
	def holding(self,pair):

		url="https://max-api.maicoin.com/api/v2/orders"
		res=requests.get(url,headers=self.verification(url),data={"market":pair})
		if res.status_code==requests.codes.ok:
			return res.json()
			pass
		else:
			return "ERROR"
		pass
	# Post an order
	def order(self,market,side,volume,ord_type,price="",stop_price=""):
		url="https://max-api.maicoin.com/api/v2/orders"
		data=dict({
			"market":market,
			"side":side,
			"volume":volume,
			"price":price,
			"stop_price":stop_price,
			"ord_type":ord_type
			})
		res=requests.post(url,headers=self.verification(url),data=data)
		if res.status_code==requests.codes.ok:
			d=res.json()
			order=dict({"side":d["side"],
						"volume":d["volume"],
						"price":d["price"],
						"ord_type":d["ord_type"],
						"state":d["state"]
						})
			return "Success"
		else:
			return "ERROR",res.status_code
		pass
	# Delete all order in specific side & market
	def delete(self,market,side):
		url="https://max-api.maicoin.com/api/v2/orders/clear"
		data=dict({"market":market,"side":side})
		res=requests.post(url,headers=self.verification(url),data=data)

		if res.status_code==requests.codes.ok:
			return "Success"
		else:
			return "ERROR"
		pass
	# Clear Max holding while remain some of it
	def clearance(self,remain=0.4):

		max_base="{}{}".format("max",self.base)
		
		balance=self.balance()
		amount = balance["max"]*(1-remain)
		
		self.order(market=max_base,side="sell",volume=amount,ord_type="market")
		pass

	pass

############### Attribution of self-defined class "account" ###############


# overview of balance of both account
def overview(a1,a2):
	if a1.pair==a2.pair:

		d1=a1.balance()
		d2=a2.balance()

		ex=d1[a1.ex]+d2[a2.ex]
		base=d1[a1.base]+d2[a2.base]
		max_=d1["max"]+d2["max"]

		pair=a1.pair
		max_base="{}{}".format("max",a1.base)
		max_ex="{}{}".format("max",a1.ex)
		
		e_b=ticker(a1.pair)["bid"]
		m_b=ticker(max_base)["bid"]
		m_e=ticker(max_ex)["bid"]
		m_e_b=m_e*e_b

		total=base+ex*e_b+max(m_b,m_e_b)*max_
		
		return dict({"total":total,a1.base:base,a1.ex:ex,"max":max_})
	else:
		return "Pair ERROR"

# Rebalance both currecny holding so both hold equal value
def rebalance(a1,a2):

	if a1.pair == a2.pair:

		d1 = a1.balance()
		d2 = a2.balance()

		ex1 = d1[a1.ex]
		ex2 = d2[a2.ex]
		base1 = d1[a1.base]
		base2 = d2[a2.base]

		pair = a1.pair
		exr=price(pair.upper())

		ex = ex1 + ex2
		base = (base1 + base2)/exr
		total=ex+base
		dif=(ex-base)/total

		if abs(dif) > 0.2:

			if dif > 0:
				side = "sell"
				p=exr*0.95
				if ex1 > ex2:
					account = a2
					amount = ex2
				elif ex1 < ex2:
					account = a1
					amount = ex1

			elif dif < 0:
				side = "buy"
				p=exr*1.05
				if base1 > base2:
					account = a2
					amount = base2 / exr
				elif base1 < base2:
					account = a1
					amount = base1 / exr

			order = account.order(market = pair,side = side,volume = amount * 0.99,ord_type = "market",stop_price=p)
			return order
	else:
		return "Pair ERROR"
	pass