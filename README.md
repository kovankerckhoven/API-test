# API-test
EVENTIGRATE API TEST

Dependencies: Python 2.7, sqlite3, requests (pip install requests)

1. Retrieves data from the https://restcountries.eu/ and http://fixer.io/
  * Name
  * Calling code
  * Capital
  * Population
  * Currency
  * Flag --------------> in images/<country.svg>
  * Exchange rate (EUR vs. AUS, BRA, CHN, GBR, USA)

2. Stores this data in a database (SQLite)
  * Table Countries (id, name, callingCode, capital, currency, flag)
  * Table Country_Has_Population (country_id, date, population)
  * Table Rates (id, base, symbol)
  * Table Rate_Has_Value (rate_id, date, value)
  
3. Reports this information as static HTML pages
  * countries.html (Contains general information for the countries)
  * flags.html (Contains large-scale versions of the flags)
  * rates.html (Displays all currency exchange rates in a clean overview)

Examples:
![Countries](https://i.imgur.com/WNbUrAO.png)
![Exchange Rates](https://i.imgur.com/cYhOFgK.png)
