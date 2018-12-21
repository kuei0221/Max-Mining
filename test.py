print "hello world"

import hmac
import hashlib
import base64
import json
import requests
import time


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

def price(symbol="BTCUSDT"):
	res=requests.get("https://api.binance.com/api/v3/avgPrice",{"symbol":symbol})
	price=float(res.json()["price"])
	return price
	pass

############### Attribution of self-defined class "account" ###############

class account(object):
	"""docstring for account"""
	def __init__(self,key,secret,base,ex):
		self.key = key
		self.secret = secret
		self.base = base
		self.ex = ex
		self.pair="{}{}".format(ex,base)
	

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

	def check(self):
		url="https://max-api.maicoin.com/api/v2/members/profile"
		res=requests.get(url,headers=self.verification(url))
		if res.status_code==requests.codes.ok:
			return "Connection Success"
		else:
			return "Connection Fail"
		pass

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
	
	def balance(self):
		ex=self.currency(self.ex)
		base=self.currency(self.base)
		max_=self.currency("max")
		return dict({self.ex:ex,self.base:base,"max":max_})
		pass

	def holding(self,pair):

		url="https://max-api.maicoin.com/api/v2/orders"
		res=requests.get(url,headers=self.verification(url),data={"market":pair})
		if res.status_code==requests.codes.ok:
			return res.json()
			pass
		else:
			return "ERROR"
		pass

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

	def delete(self,market,side):
		url="https://max-api.maicoin.com/api/v2/orders/clear"
		data=dict({"market":market,"side":side})
		res=requests.post(url,headers=self.verification(url),data=data)

		if res.status_code==requests.codes.ok:
			return "Success"
		else:
			return "ERROR"
		pass

	def clearance(self,remain=0.4):

		max_base="{}{}".format("max",self.base)
		
		balance=self.balance()
		amount = balance["max"]*(1-remain)
		
		self.order(market=max_base,side="sell",volume=amount,ord_type="market")
		pass

	pass

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

############### Attribution of self-defined class "account" ###############

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

# michael=account(key="xTMdRafyQcSX1X5G5Zgmewx1JQIVO8USpY9SNcVv",
# 				secret="ENjw20aos4sYiZbcieoibceJEWNqP3QCnEZmKHS8",
# 				base="usdt",
# 				ex="ltc")


# alex=account(key="Ox3ljxZdexOX7nEIzwWWWt64eI61s5iwxzPwDYv9",secret="iaYDgYwx2Udela1YFr2WDL5ZESyEmTAivKvx9lt8",base="usdt",ex="ltc")

# # print overview(michael,alex)
# print michael.balance()
# print alex.balance()
# # # print  rebalance(michael,alex)
# # michael.delete("maxusdt","sell")
# alex.delete("maxusdt","sell")
# # # # print ticker("btcusdt")
# print michael.holding("btcusdt")
# print alex.holding("btcusdt")
# print michael.holding("maxusdt")
# print alex.holding("maxusdt")
# # # # # alex.max_clear()
# # michael.order(market="maxusdt",side="sell",volume=20,ord_type="market",stop_price=0.075)
# alex.order(market="maxusdt",side="sell",volume=44100,ord_type="market")
# print michael.clearance()
# # print alex.clearance()