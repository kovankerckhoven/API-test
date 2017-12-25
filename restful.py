"""
EVENTIGRATE API TEST

This file has two tasks, and should be executed on an automatic basis whenever changes
to the described data are to be expected; it could for example be run as a cronjob once
at the end of every day.

1) Retrieve the following data from restful web services:
https://restcountries.eu/ (free, without registration)
    Name
    Calling code
    Capital
    Population
    Currency
    Flag --------------> If we don't have it yet in images/<country.svg>
http://fixer.io/ (free, without registration)
    Exchange rate (EUR vs. AUS, BRA, CHN, GBR, USA)

2) Store the data in a database (SQLite)
Table Countries
	id				INTEGER PRIMARY KEY (AUTOINCREMENT)
	name			TEXT
	callingCode		TEXT
	capital			TEXT
	currency		TEXT
	flag			TEXT
Table Country_Has_Population
	country_id		INTEGER (FOREIGN KEY)
	date			DATE
	population		INTEGER
Table Rates
	id				INTEGER PRIMARY KEY (AUTOINCREMENT)
	base			TEXT
	symbol			TEXT
Table Rate_Has_Value
	rate_id			INTEGER (FOREIGN KEY)
	date			DATE
	value			INTEGER
"""

# Imports
import sys
import json
import requests
import shutil
import sqlite3 as sqlite
from datetime import date
from os import path

currencyCodes = []
codeCollection = ""
db = sqlite.connect('countries.db', isolation_level=None)
db_cursor = None

def db_setup():
	global db_cursor, db
	with db:
		db_cursor = db.cursor()
		db_cursor.execute("CREATE TABLE IF NOT EXISTS Countries(id INTEGER PRIMARY KEY, name TEXT, callingCode TEXT, capital TEXT, currency TEXT, flag TEXT)")
		db_cursor.execute("CREATE TABLE IF NOT EXISTS Country_Has_Population(country_id INTEGER, date DATE, population INTEGER)")
		db_cursor.execute("CREATE TABLE IF NOT EXISTS Rates(id INTEGER PRIMARY KEY, base TEXT, symbol TEXT)")
		db_cursor.execute("CREATE TABLE IF NOT EXISTS Rate_Has_Value(rate_id INTEGER, date DATE, value INTEGER)")

def db_print():
	global db_cursor, db
	with db:
		db_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
		print("TABLES IN DB:")
		tables = db_cursor.fetchall()
		print(tables)
		for table in tables:
			db_cursor.execute("SELECT * FROM %s;" % table)
			print("Table %s" % table)
			print(db_cursor.fetchall())
			print("")

def downloadFlag(url, filename):
	if not path.isfile("images/%s" % filename): # If the flag has never been downloaded yet
		req = requests.get(url, stream=True)
		with open("images/%s" % filename, 'wb') as file:
			shutil.copyfileobj(req.raw, file)

# What we will use to temporarily store objects before updating the DB
class Country(object):
	def printCountry(self):
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
	
	def __str__(self):
		return u'{}'.format(self.name)
		
	def __init__(self, json):
		self.name = json.get('name', None)
		self.currencies = json.get('currencies', None)
		self.capital = json.get('capital', None)
		self.callingCodes = json.get('callingCodes', None)
		self.population = json.get('population', None)
		self.flag = json.get('flag', None)
			
"""
restcountries.eu API Calls
https://restcountries.eu/rest/v2/name/australia
https://restcountries.eu/rest/v2/name/brazil
https://restcountries.eu/rest/v2/name/china -> [0] = China, [1] = Macao, [2] = Taiwan
https://restcountries.eu/rest/v2/name/britain
https://restcountries.eu/rest/v2/name/usa

Stores country fields in DB and updates population if necessary
TODO: Insert ALL callingCodes and currencies and be able to retrieve them as a list
"""
def getCountries():
	global currencyCodes, codeCollection, db, db_cursor
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
			
			# Map the data to Python
			countryObj = Country(data)
			downloadFlag(data['flag'], "%s.svg" % countryObj.currencies[0]['code'])
			currencyCodes.append(countryObj.currencies[0]['code'])
			codeCollection = "%s,%s" % (codeCollection, countryObj.currencies[0]['code'])
			
			# Insert data into DB where necessary
			with db:
				db_cursor.execute("SELECT id FROM Countries WHERE name='%s';" % countryObj.name)
				rows = db_cursor.fetchall()
				if not rows: # Country not in DB yet; insert it completely
					db_cursor.execute("INSERT INTO Countries(name, callingCode, capital, currency, flag) VALUES ('%s', '%s', '%s', '%s', '%s');" % (countryObj.name, countryObj.callingCodes[0], countryObj.capital, countryObj.currencies[0]['code'], countryObj.flag))
					db_cursor.execute("SELECT id FROM Countries WHERE name='%s';" % countryObj.name)
					country_id = db_cursor.fetchall()[0][0]
					db_cursor.execute("INSERT INTO Country_Has_Population(country_id, date, population) VALUES ('%s', '%s', '%s');" % (country_id, date.today(), countryObj.population))
				else: # Country already in DB; check if today's population is in DB
					country_id = rows[0][0]
					db_cursor.execute("SELECT population, date FROM Country_Has_Population WHERE country_id='%s' ORDER BY date DESC" % country_id)
					rows = db_cursor.fetchall()
					if not rows: # No population for this country in DB yet; insert it
						db_cursor.execute("INSERT INTO Country_Has_Population(country_id, date, population) VALUES ('%s', '%s', '%s');" % (country_id, date.today(), countryObj.population))
					elif "%s" % rows[0][1] != "%s" % date.today(): # Population for this date not in DB yet; insert it
						db_cursor.execute("INSERT INTO Country_Has_Population(country_id, date, population) VALUES ('%s', '%s', '%s');" % (country_id, date.today(), countryObj.population))
					# If there is already a population for today, compare the values and take the mean?
		elif response.status_code == 404:
			print("HTTP 404: InvalidURL")
			raise requests.exceptions.InvalidURL
		else:
			print("RequestException")
			raise requests.exceptions.RequestException

""" 
fixer.io API calls
https://api.fixer.io/latest?symbols=USD,GBP&base=EUR (will ask for today's EUR/USD and EUR/GBP rates)
"""
def getExchangeRates():
	global currencyCodes, codeCollection, db, db_cursor
	fixerBase = "https://api.fixer.io/latest?symbols="
	for baseField in currencyCodes:
		url = ("%s%s&base=%s" % (fixerBase, codeCollection, baseField)) # format URL
		response = requests.get(url)
		if response.status_code == 200: # HTTP 200 OK
			data = json.loads(response.text)
			for rate in data['rates']: # data['base'] is the BASE, rate is the SYMBOL (BASE/SYMBOL notation)
				db_cursor.execute("SELECT id FROM Rates WHERE base='%s' AND symbol='%s';" % (baseField, rate))
				rows = db_cursor.fetchall()
				if not rows: # This rate (BASE/SYMBOL combination) not in DB yet; insert it completely
					db_cursor.execute("INSERT INTO Rates(base, symbol) VALUES ('%s', '%s');" % (data['base'], rate))
					db_cursor.execute("SELECT id FROM Rates WHERE base='%s' AND symbol='%s';" % (data['base'], rate))
					rate_id = db_cursor.fetchall()[0][0]
					db_cursor.execute("INSERT INTO Rate_Has_Value(rate_id, date, value) VALUES ('%s', '%s', '%s');" % (rate_id, date.today(), data['rates'][rate]))
				else: # Rate already in DB; check today's values instead
					rate_id = rows[0][0]
					db_cursor.execute("SELECT value, date FROM Rate_Has_Value WHERE rate_id='%s' ORDER BY date DESC" % rate_id)
					rows = db_cursor.fetchall()
					if not rows: # No value for this rate in DB yet; insert it
						db_cursor.execute("INSERT INTO Rate_Has_Value(rate_id, date, value) VALUES ('%s', '%s', '%s');" % (rate_id, date.today(), data['rates'][rate]))
					elif "%s" % rows[0][1] != "%s" % date.today(): # Population for this date not in DB yet; insert it
						db_cursor.execute("INSERT INTO Rate_Has_Value(rate_id, date, value) VALUES ('%s', '%s', '%s');" % (rate_id, date.today(), data['rates'][rate]))
					# If there is already a rate for today, compare the values and take the mean?
		elif response.status_code == 404:
			print("HTTP 404: InvalidURL")
			raise requests.exceptions.InvalidURL
		else:
			print("RequestException")
			raise requests.exceptions.RequestException
			
def callAPIs():
	getCountries()
	getExchangeRates()

db_setup()
callAPIs()
# Call db_print() to easily print contents of the entire DB