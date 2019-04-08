import configparser
def read_account_data():
	conf = configparser.ConfigParser()
	try:
		conf.read("account.ini")	
	except:
		print("Error: Account Data Not Exist")
		return None
	else:
		df =dict()
		for section in conf.sections():
			d = dict(conf.items(section))
			df.update({section: d})
		return df
	pass
