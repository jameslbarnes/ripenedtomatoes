from uszipcode import ZipcodeSearchEngine
search = ZipcodeSearchEngine()
import random
import numpy as np 
import scipy
densitymap = {}
incomemap = {}
densities = []
incomes = []
ziplisting = {}
cities = {}
cityDensity = []
cityWealth = []

zips = random.sample(xrange(10000,99999), 500)

for x in zips:
	zipcode = search.by_zipcode(x)
	if zipcode.City > 0:
		if zipcode.Wealthy > 0:
			if zipcode.Density > 0:
				cityDensity[x] = zipcode.Density
				cityWealth[x] = zipcode.Wealthy
				densities.append(zipcode.Density)
				incomes.append(zipcode.Wealthy)


for x in densities:
	stats.percentileofscore(densities, x, 'mean')
			
