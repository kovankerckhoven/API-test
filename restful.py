"""
EVENTIGRATE API TEST

1) Retrieve the following data from restful web services:
https://restcountries.eu/ (free, without registration)
    Name
    Calling code
    Capital
    Population
    Currency
    Flag
http://fixer.io/ (free, without registration)
    Exchange rate (EUR vs. AUS, BRA, CHN, GBR, USA)

2) Store the data in a database (SQLite)
3) Report the results for each country (Australia, Brazil, China, Great Britain, USA) back to the end user

The end-user report should contain (the average of) all above properties for the past month in
a nice and clean summary of the following countries: AUS, BRA, CHN, GBR, USA.. The type of
report can be decided completely by you (.xls, .html, .pdf, .txt, .csv, ...). You can choose the
language, technologies, frameworks, tools, etc. Please create your own database and push your
code to a git repository together with an example of the output report and a sketch off your
architecture/design (a photo of a simple paper-sketch suffices) and share the repository with
thomas_demoor@msn.com or the user thomasdemoor on Bitbucket. If something is unclear,
you can always send a mail to thomas@eventigrate.com or give a call at +32497486215.
"""

# Imports
import json
import requests
from datetime import date

currencyCodes = []
codeCollection = ""

# What we will use to temporarily store objects before updating the DB
class Country(object):
    def __str__(self):
        return u'{}'.format(self.name)

    def __init__(self, json):
		self.name = json.get('name', None)
		self.currencies = json.get('currencies', None)
		self.capital = json.get('capital', None)
		self.callingCodes = json.get('callingCodes', None)
		self.population = json.get('population', None)
		self.flag = json.get('flag', None)
		print("%s:" % self.name)
		print("\tCapital: %s" % self.capital)
		print("\tPopulation: %s" % self.population)
		print("\tCalling code: +%s" % self.callingCodes[0])
		print("\tCurrencies:")
		print("AMOUNT OF CURRENCIES: %s" % len(self.currencies))
		for currency in self.currencies:
			print("\t\t%s (%s, %s)" % (currency['code'], currency['name'], currency['symbol']))
		print("\tFlag: %s" % self.flag)
		print("")

"""
restcountries.eu API Calls
https://restcountries.eu/rest/v2/name/australia
https://restcountries.eu/rest/v2/name/brazil
https://restcountries.eu/rest/v2/name/china -> [0] = China, [1] = Macao, [2] = Taiwan
https://restcountries.eu/rest/v2/name/britain
https://restcountries.eu/rest/v2/name/usa

TODO: Store each Country object in the DB after fetching its data
"""
def getCountries():
	global currencyCodes, codeCollection
	restBase = "https://restcountries.eu/rest/v2/name"
	countries = ["australia", "brazil", "china", "britain", "usa"]
	restFields = "?fields=name;callingCodes;capital;population;currencies;flag"
	for country in countries:
		url = ("%s/%s%s" % (restBase, country, restFields)) # format URL
		response = requests.get(url)
		if response.status_code == 200: # HTTP 200 OK
			data = json.loads(response.text)
			if type(data) == list:
				data = data[0] # We're only interested in the first country
			country = Country(data)
			currencyCodes.append(country.currencies[0]['code'])
			codeCollection = "%s,%s" % (codeCollection, country.currencies[0]['code'])
		elif response.status_code == 404:
			print("HTTP 404: InvalidURL")
			raise requests.exceptions.InvalidURL
		else:
			print("RequestException")
			raise requests.exceptions.RequestException

""" 
fixer.io API calls
https://api.fixer.io/latest?symbols=USD,GBP&base=EUR (will ask for today's EUR/USD and EUR/GBP rates)

TODO: Don't check today's date, but the last date updated in the DB for that base currency
"""
def getExchangeRates():
	global currencyCodes, codeCollection
	url = "https://api.fixer.io/latest?symbols=USD&base=USD" # NOT NECESSARY WHEN USING DB
	response = requests.get(url) # NOT NECESSARY WHEN USING DB
	if response.status_code == 200: # HTTP 200 OK; NOT NECESSARY WHEN USING DB
		data = json.loads(response.text) # NOT NECESSARY WHEN USING DB
		if (("%s" % data['date']) == ("%s" % date.today())): # Start for-loop here, check DB for each one.
			fixerBase = "https://api.fixer.io/latest?symbols="
			for fixerField in currencyCodes:
				url = ("%s%s&base=%s" % (fixerBase, codeCollection, fixerField)) # format URL
				response = requests.get(url)
				if response.status_code == 200: # HTTP 200 OK
					data = json.loads(response.text)
					print("")
					print("Exchange rate date: %s" % data['date'])
					for rate in data['rates']:
						print("%s/%s: %s" % (data['base'], rate, data['rates'][rate]))
				elif response.status_code == 404:
					print("HTTP 404: InvalidURL")
					raise requests.exceptions.InvalidURL
				else:
					print("RequestException")
					raise requests.exceptions.RequestException

def callAPIs():
	getCountries()
	getExchangeRates()
					
callAPIs()

"""
def writeToFile():
    displayFile = open("index.html", 'w')
    displayFile.write("<HTML>")
	displayFile.write("</HTML>")
	displayFile.close()

# Working with floating point:	
# btc = Decimal(i*0.00000001).quantize(Decimal('.00000001'), rounding=ROUND_DOWN)
"""