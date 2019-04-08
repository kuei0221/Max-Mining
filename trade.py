from api import quote,refer_price
import random
import time

#create a dict of current account status
def overview(account1,account2,ex,base):
	df1 = account1.balance(ex, base)
	df2 = account2.balance(ex, base)
	ex_total = df1[ex] + df2[ex]
	base_total = df1[base] + df2[base]
	max_total = df1["max"] + df2["max"]
	overall = base_total + ex_total * quote(f"{ex}{base}")["bid"] + max_total * quote(f"max{base}")["bid"]
	return dict({base:base_total, ex:ex_total, "max":max_total, "overall":overall})
	pass

# main trade operation function
def trade(account1,account2,ex,base,N):

	pair = f"{ex}{base}"
	max_base = f"max{base}"

	if account1.currency(ex)["balance"] > account2.currency(ex)["balance"]:
		ac_sell = account1
		ac_buy = account2
	else:
		ac_buy = account1
		ac_sell = account2

	# max_order_price = quote(max_base)["bid"] + 1e-3
  ## Since the exchange support there max price at 0.081 at this point, the variable is locked by constant
	max_order_price = 0.081
	volume_max_1 = float(ac_buy.currency("max")["balance"])
	if volume_max_1 > 10:
		ac_buy.order(market = max_base, side = "sell", ord_type = "limit",
			volume = volume_max_1, price = max_order_price)	
		pass
	volume_max_2 = float(ac_sell.currency("max")["balance"])
	if volume_max_2 > 10:
		ac_sell.order(market = max_base, side = "sell", ord_type = "limit",
			volume = volume_max_2, price = max_order_price)	
		pass

	n = 0
	while n < N:

		print(f"Start of {n} trade")
		try:

			price_max = quote(pair)
			price_refer = float(refer_price(pair.upper())["price"])

			if price_max["bid"] < price_refer < price_max["ask"]:
				while (1):
					price = round(price_refer * random.uniform(0.997,0.999),2)
					if price_max["bid"] < price < price_max["ask"]:
						volume_ex = float(ac_sell.currency(ex)["balance"])
						volume_base = float(ac_buy.currency(base)["balance"]) / price
						volume = round(min(volume_ex, volume_base) * 0.995,6)
						del price_max, price_refer
						break
					del price
			else:
				print("##############################################")
				print("Refer Price out of Bound. Pause for 30 seconds")
				print("##############################################")
				time.sleep(30)
				continue
		except:
			print("##############################################")
			print("Cannot Get Date from Exchange. Retry after 3 seconds.")
			print("##############################################")
			time.sleep(3)
			continue

		print("Placing Orders")
		try:
			order_sell = ac_sell.order(market = pair, side = "sell", ord_type = "limit",
				price = price, volume = volume)
			id_sell = order_sell["id"]
		except:
			print("##############################################")
			print("Cannot Place Order. Retry after 3 seconds.")
			print("##############################################")
			time.sleep(3)
			continue

		while(1):
			try: 
				 if quote(pair)["ask"] == price:

				    print("Place Main Exchange Order")
				    order_buy = ac_buy.order(market = pair, side = "buy", ord_type = "market", 
					    volume = volume, stop_price = price * 0.98)
				    id_buy = order_buy["id"]

				    if volume_base > volume_ex:
					    print("Place Rebalance Order")
					    print(volume_base)
					    print(volume_ex)
					    remain_base = float(ac_buy.currency(base)["balance"]) / price
					    print(remain_base)
					    # ac_buy.order(market = pair, side = "buy", ord_type = "market", 
					    # volume = round(remain_base * 0.99, 6), stop_price = price * 0.98)
					    del remain_base
				    break
			except:
				continue
		del order_sell, order_buy, price, volume_base, volume_ex

		print("Checking orders' status")

		while (1):
			try:
				condition1 = ac_sell.checkorder(id_sell)["state"] == "done"
				condition2 = ac_buy.checkorder(id_buy)["state"] == "done"
			except:
				continue
			if condition1 is True and condition2 is True:
				break
			if condition1 is False and condition2 is False:
				print("Positions in Both Side Remain")
				continue
			if condition1 is False and condition2 is True:
				print("Buy Position Remain")
				ac_buy.delete(pair,"buy")
				continue
			if condition1 is True and condition2 is False:
				print("Sell Position Remain")
				ac_sell.delete(pair,"sell")
				continue
			del condition1, condition2, id_sell, id_buy

		print("Placing New Max orders")
		volume_max_1 = float(ac_buy.currency("max")["balance"])
		if volume_max_1 > 10:
			ac_buy.order(market = max_base, side = "sell", ord_type = "limit",
				volume = volume_max_1, price = max_order_price)	
		volume_max_2 = float(ac_sell.currency("max")["balance"])
		if volume_max_2 > 10:
			ac_sell.order(market = max_base, side = "sell", ord_type = "limit",
				volume = volume_max_2, price = max_order_price)	
		del volume_max_1, volume_max_2

		print("Place Repurchase Order")
		if n is 0:
			repurchase_price = quote(pair)["bid"] + 0.01
		if repurchase_price != quote(pair)["bid"]:
			ac_buy.delete(pair, "buy")
			ac_sell.delete(pair, "sell")
			repurchase_price = quote(pair)["bid"] + 0.01
		ac_buy.order(market = pair, side = "buy", ord_type = "limit",
			volume = round(volume * 0.001,6), price = repurchase_price)
		del volume
		print(f"End of {n} trade.")
		print("")

		n += 1
		ac_buy, ac_sell = ac_sell, ac_buy
		pass
