"""
EVENTIGRATE API TEST

This file displays the information gathered by restful.py, and should be executed whenever
data has changed AND it is recommended to display the updated information instead of the old.

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
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import sqlite3 as sqlite
from datetime import date
from os import path

db = sqlite.connect('countries.db', isolation_level=None)
db_cursor = db.cursor()

def updateCountries(countries):
	# countries.html
	with open("countriesBegin.template", 'r') as beginFile:
		begin = beginFile.readlines()
	with open("countries.html", 'w') as file:
		file.writelines(begin)
		for country in countries: # [0]: id, [1]: name, [2]: callingCode, [3]: capital, [4]: currency, [5]: flag URL
			file.write('<div class="col-6 col-sm-3 placeholder">\n')
			file.write('<a href="flags.html#%s"><img src="images/%s.svg" width="100" class="img-fluid" alt="Flag of %s"></a>\n' % (country[4], country[4], country[1]))
			file.write('<h4>%s</h4>\n' % country[1])
			file.write('<div class="text-muted">Capital: %s</div>\n' % country[3])
			file.write('</div>\n')
		file.write('</section><h2>Information & statistics</h2><div class="table-responsive"><table class="table table-striped">\n')
		file.write('<thead><tr><th>#</th><th>Name</th><th>Calling code</th><th>Capital</th><th>Currency code</th></tr></thead>\n')
		file.write('<tbody>\n')
		for country in countries: # [0]: id, [1]: name, [2]: callingCode, [3]: capital, [4]: currency, [5]: flag URL
			file.write('<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td><a href="rates.html#%s">%s</a></td></tr>' % (country[0], country[1], "+%s" % country[2], country[3], country[4], country[4]))
		with open("countriesEnd.template", 'r') as endFile:
			end = endFile.readlines()
		file.writelines(end)
		file.close()
	
	# flags.html
	with open("flagsBegin.template", 'r') as beginFile:
		begin = beginFile.readlines()
	with open("flags.html", 'w') as file:
		file.writelines(begin)
		for country in countries:
			file.write('<div class="text-muted text-left">%s</div>\n' % country[1])
			file.write('<section class="row text-center">\n')
			file.write('<img id="%s" src="images/%s.svg" width="500" class="img-fluid" alt="Flag of %s">\n' % (country[4], country[4], country[1]))
			file.write('</section><br />\n')
		with open("flagsEnd.template", 'r') as endFile:
			end = endFile.readlines()
		file.writelines(end)
		file.close()

def updateRates(rates):
	with open("rates.html", 'w') as file:
		file.writelines(begin)
		for country in countries:
			file.write('<div class="text-muted text-left">%s</div>\n' % country[1])
			file.write('<section class="row text-center">\n')
			file.write('<img id="%s" src="images/%s.svg" width="500" class="img-fluid" alt="Flag of %s">\n' % (country[4], country[4], country[1]))
			file.write('</section><br />\n')
		with open("flagsEnd.template", 'r') as endFile:
			end = endFile.readlines()
		file.writelines(end)
		file.close()

def fetchCountries():
	global db_cursor, db
	with db:
		db_cursor.execute("SELECT * FROM Countries ORDER BY id ASC;")
		countries = db_cursor.fetchall()
		updateCountries(countries)
		with open("ratesBegin.template", 'r') as beginFile: # rates.html
			begin = beginFile.readlines()
		with open("rates.html", 'w') as file:
			file.writelines(begin)
			for country in countries:
				file.write('</section><div class="table-responsive"><table class="table table-striped">\n')
				file.write('<thead><tr><th id="%s" colspan="4">%s</th></tr><tr><th>#</th><th>Exchange rate</th><th>Value</th><th>Date</th></tr></thead>\n' % (country[4], country[4]))
				file.write('<tbody>\n')
				db_cursor.execute("SELECT id, symbol FROM Rates WHERE base='%s'" % country[4]) # This will hopefully be multiple BASE/SYMBOL rates
				symbols = db_cursor.fetchall()
				for symbol in symbols:
					db_cursor.execute("SELECT value, date FROM Rate_Has_Value WHERE rate_id='%s';" % symbol[0])
					tmp = db_cursor.fetchall()[0]
					file.write('<tr><td>%s</td><td>%s/%s</td><td>%s</td><td>%s</td></tr>' % (symbol[0], country[4], symbol[1], tmp[0], tmp[1]))
			with open("countriesEnd.template", 'r') as endFile:
				end = endFile.readlines()
			file.writelines(end)
			file.close()

fetchCountries()