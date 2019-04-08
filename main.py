import sys
import api
from trade import trade, overview
from launch import read_account_data

operation_start = input("Hello Trader, Going to start the Operation? y/n   ")

if operation_start is not "y":
	sys.exit()
	pass


df = read_account_data()
while (1) :
	user = input("Please Enter Name of Account: ")
	if user not in df.keys():
	    print("Such User does not Exist. Please Re Enter.")
	    continue
	account1 = api.account(key = df[user]["key1"], secret = df[user]["secret1"])
	account2 = api.account(key = df[user]["key2"], secret = df[user]["secret2"])
	base = df[user]["base"]
	ex = df[user]["ex"]
	pair = f"{ex}{base}"
	break

if account1.check() is None or account2.check() is None:
	print("Irregular Account")
	sys.exit()
	pass


view = overview(account1, account2, ex, base)
keys = view.keys()
print(f"Current Account Balance:")
for key in keys:
	print(f"{key.upper()} : {round(view[key],4)}")
	pass
del view, keys


go = input("Trade start?  y/n    ")
if go is "y":
	n = input("How much trades you would like to do?")
	if n > 0:
		trade(account1, account2, ex, base, N = int(n))
	else:
		print("Error: Irregular Number Entered")
else:
	print("Trade has been canceled. Press any key to end the system.")
input()
