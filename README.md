# API-test
EVENTIGRATE API TEST

Dependencies: Python 2.7, sqlite3, requests (pip install requests)

1) Retrieves data from the following restful web services:
https://restcountries.eu/ (free, without registration)
    Name
    Calling code
    Capital
    Population
    Currency
    Flag --------------> in images/<country.svg>
http://fixer.io/ (free, without registration)
    Exchange rate (EUR vs. AUS, BRA, CHN, GBR, USA)

2) Stores this data in a database (SQLite)
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
	
3) Reports this information as static HTML pages
countries.html		-->		Contains general information for the countries
flags.html			-->		Contains large-scale versions of the flags
rates.html			-->		Displays all currency exchange rates in a clean overview

Examples:
![Countries](https://i.imgur.com/WNbUrAO.png)
![Exchange Rates](https://i.imgur.com/cYhOFgK.png)