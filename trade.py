from api import quote, refer_price
import random
import time

# create a dict of both current account status


def overview(account1, account2, ex, base):
    df1 = account1.balancesheet(ex, base)
    df2 = account2.balancesheet(ex, base)
    ex_total = df1[ex] + df2[ex]
    base_total = df1[base] + df2[base]
    max_total = df1["max"] + df2["max"]
    overall = base_total
    + ex_total * quote(f"{ex}{base}")["bid"]
    + max_total * quote(f"max{base}")["bid"]
    return dict({base: base_total, ex: ex_total,
                "max": max_total, "overall": overall})

# create main trade operation function


def trade(account1, account2, ex, base, N):

    pair = f"{ex}{base}"
    max_base = f"max{base}"
    
    # Set Initial account to buy and to sell
    if account1.currency_holding(ex)["balance"] > account2.currency_holding(ex)["balance"]:
        ac_sell = account1
        ac_buy = account2
    else:
        ac_buy = account1
        ac_sell = account2

    # Since the exchange made the max/usdt price hold at 0.081 at this point, the variable is locked by constant
    # The following code might use if the price no longer holds or the product are changed
    # max_order_price = quote(max_base)["bid"] + 1e-3
    max_order_price = 0.081
    
    # Place Initial max order
    [account.create_order(
        market=max_base, side="sell", ord_type="limit",
        volume=float(account.currency_holding("max")["balance"]),
        price=max_order_price)
        for account in [ac_buy, ac_sell]
        if float(account.currency_holding("max")["balance"]) > 10]
    
    # Trade N times with n rolling
    n = 0
    while n < N:

        print(f"Start of {n} trade")
        #Use Refer price as target price, and it should be between the bid and ask price in Max exchange
        try:

            price_from_max = quote(pair)
            price_from_refer = float(refer_price(pair.upper())["price"])

            if price_from_max["bid"] < price_from_refer < price_from_max["ask"]:
                while (1):
                    price = round(price_from_refer * random.uniform(0.997, 0.999), 2)
                    if price_from_max["bid"] < price < price_from_max["ask"]:
                        volume_ex = float(ac_sell.currency_holding(ex)["balance"])
                        volume_base = float(ac_buy.currency_holding(base)["balance"]) / price
                        volume = round(min(volume_ex, volume_base) * 0.995, 6)
                        del price_from_max, price_from_refer
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

        print("Place Sell Orders")
        try:
            order_sell = ac_sell.create_order(
                market=pair, side="sell", ord_type="limit",
                price=price, volume=volume)
            id_sell = order_sell["id"]
        except:
            print("##############################################")
            print("Cannot Place Order. Retry after 3 seconds.")
            print("##############################################")
            time.sleep(3)
            continue

        print("Place Buy Orders")
        try:
            if quote(pair)["ask"] == price:
                order_buy = ac_buy.create_order(
                    market=pair, side="buy", ord_type="market",
                    volume=volume, stop_price=price * 0.98)
                id_buy = order_buy["id"]
        except:
                continue
        del order_sell, order_buy, price, volume_base, volume_ex

        print("Checking orders' status")

        while (1):
            try:
                sell_done = ac_sell.checkorder(id_sell)["state"] == "done"
                buy_done = ac_buy.checkorder(id_buy)["state"] == "done"
            except:
                continue
            if sell_done is True and buy_done is True:
                break
            if sell_done is False and buy_done is False:
                print("Positions in Both Side Remain")
                continue
            if sell_done is True and buy_done is False:
                print("Buy Position Remain")
                ac_buy.delete_order(pair, "buy")
                continue
            if sell_done is False and buy_done is True:
                print("Sell Position Remain")
                ac_sell.delete_order(pair, "sell")
                continue
            del sell_done, buy_done, id_sell, id_buy

        print("Placing New Max orders")

        [account.create_order(
            market=max_base, side="sell", ord_type="limit",
            volume=float(account.currency_holding("max")["balance"]),
            price=max_order_price)
            for account in [ac_buy, ac_sell]
            if float(account.currency_holding("max")["balance"]) > 10]

        print("Place Repurchase Order")
        if n is 0:
            repurchase_price = quote(pair)["bid"] + 0.01
        if repurchase_price != quote(pair)["bid"]:
            ac_buy.delete_order(pair, "buy")
            ac_sell.delete_order(pair, "sell")
            repurchase_price = quote(pair)["bid"] + 0.01
        ac_buy.create_order(
            market=pair, side="buy", ord_type="limit",
            volume=round(volume * 0.001, 6), price=repurchase_price)
        del volume
        print(f"End of {n} trade.")
        print("")

        n += 1
        ac_buy, ac_sell = ac_sell, ac_buy
        pass
