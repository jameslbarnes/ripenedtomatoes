import urllib2
import json
import datetime
from lxml import html
import requests
from multiprocessing import Pool 
import numpy as np 
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import sqlite3 
import sys
from collections import Counter
from collections import defaultdict
import time


## Scraping settings (you can add more by visiting the documentation and appending to the URL)

movie_released_after = '2012-12-01' ## 
include_adult = 'false' ## No Porn
with_original_language = 'en' ## English films only
minimum_votes = '10' ## Not quite sure how this is determined, but 10 is enough to cut out weird, obscure movies while most blockbusters have thousands of votes
api_key = 'ffb134d4a18813bcf11b130277649fe3'
url = "https://api.themoviedb.org/3/discover/movie?primary_release_date.gte=" + movie_released_after + "&include_adult=" + include_adult + "&with_original_language=" + with_original_language + "&vote_count.gte=" + minimum_votes + "&api_key=" + api_key 
length = json.load(urllib2.urlopen(url))['total_pages']
moviedict = {'key':[0] * 7}
testdict = {}
parray = []
audienceshatethis = "a"
audienceslovethis = "a"
criticshatethis = "a"
criticslovethis = "a"
corpus = "a"

def kickoff():
	for x in range(1, length): ## Queries the movie DB API to figue out how many pages we need to turn - use "length" for full query
		turnPage(x)

def turnPage(x): ## "turns the page" and iterates the crawler through each item on the newest page

	data = json.load(urllib2.urlopen(url + "&page=" + str(x))) ## creates a JSON object from the movie DB API page's output 
	print "page " + str(x) + " of " +  str(length) + ","
	for index, element in enumerate(data['results']): ## loops through each element in the new JSON object and invokes the web crawler on it
		webCrawl(data, index)


def webCrawl(data, x): ## prepares the URL from the movie DB API and crawls the specific Rotten Tomatoes page

		title = data['results'][x]['title'] ## finds the title 
		title = title.lower() ## prepares the title to be inserted into the Rotten Tomatoes URL
		title = clean_data(title)
		title = title.replace (" ", "_") ##
		vote_count = data['results'][x]['vote_count'] ## finds the vote count for analysis
		date = data['results'][x]['release_date'][:4] ## finds the release date and truncates it to year only
		tomatoesurl = "https://www.rottentomatoes.com/m/" + title ## prepares the base URL
		parsedurl = requests.get(tomatoesurl + "_" + date) ## attempts to access the URL with release date appended at the end
		if parsedurl.status_code == 404:
			parsedurl = requests.get(tomatoesurl) ## if the release date doesn't work, tries without
		else:
			pass
		tree = html.fromstring(parsedurl.content) ## uses the lxml library to parse the site's HTML
		tMeterScore = tree.xpath('string(//span[@class="meter-value superPageFontColor"])') ## uses xpath to extract the tomato meter score, which is held within a random, but unique, span
		audienceScore = str(tree.xpath('//span[@class="superPageFontColor" and @style="vertical-align:top" ]/text()')) ## uses xpath to extract the audience score, which is held within a commonly used span class, but the only one that is vertically aligned
		criticReviews = str(tree.xpath('//div[@id="reviews"]//div[@class="review_quote"]//div[@class="media"]/div[@class="media-body"]/p[1]/text()'))
		audienceReviews = str(tree.xpath('//section[@id="audience_reviews"]//div[@class="review_quote"]//div[@class="media"]/div[@class="media-body"]/p[1]/text()'))
		tMeterScore = tMeterScore.replace("%", "") ## removes artifacts from the scores
		audienceScore = clean_data(audienceScore)
		criticReviews = clean_data(criticReviews)
		audienceReviews = clean_data(audienceReviews)

		if tMeterScore and not tMeterScore.isspace(): ## ensures both scores have values to be stored
			if audienceScore and not audienceScore.isspace():
				if tMeterScore != "0":
					ratio = float(audienceScore) / float(tMeterScore)## calculates ratio of audience to critical reaction
					moviedict[title] = [date, ratio, audienceScore, tMeterScore, criticReviews, audienceReviews, vote_count]
					 ## adds values to dictionary
					parray.append(ratio) ## creates an array of ratios in order to later calculate percentiles
					print "movie " + str(x) + " " + " of " + str(len(data['results']))

					print title + ", " + str(ratio) + " "
		else:
			pass


def clean_data(x):

	x = x.replace (",", "") ##
	x = x.replace ("!", "") ##
	x = x.replace (".", "") ##
	x = x.replace (":", "") ##
	x = x.replace ("'", "") ##
	x = x.replace ("]", "") ##
	x = x.replace ("[", "") ##
	x = x.replace ("%", "") ##
	x = x.replace ("'", "") ##
	x = x.replace ("-", "") ##

	return x


### executable code below ### 


kickoff()

a = np.array(parray) ## creates numpy array from earlier ratio array

for x, y in moviedict.items(): ## for loop to combine reviews of movies in the 10th and 90th percentiles of ratio

	if y[1] >= np.percentile(a, 90):
		audienceslovethis = audienceslovethis + str(y[5])
		criticshatethis = criticshatethis + str(y[4])
		

	elif y[1] <= np.percentile(a, 10):
		audienceshatethis = audienceshatethis + str(y[5])
		criticslovethis = criticslovethis + str(y[4])

	else:
		continue

for x, y in moviedict.items():
	corpus = corpus + str(y[5]) + str(y[4])

audienceslovethis = audienceslovethis.lower() ## lowercase all characters in reviews
criticshatethis = criticshatethis.lower()
audienceshatethis = audienceshatethis.lower()
criticslovethis = criticslovethis.lower()
corpus = corpus.lower()

audienceslovecount = dict(Counter(audienceslovethis.split()).most_common()) ## use most_common function to create 
criticshatecount = dict(Counter(criticshatethis.split()).most_common())
audienceshatecount = dict(Counter(audienceshatethis.split()).most_common())
criticslovecount = dict(Counter(criticslovethis.split()).most_common())
corpuscount = dict(Counter(corpus.split()).most_common())


db = sqlite3.connect("mydatabase.db") ## create and configure database. replace old tables with new ones


cursor = db.cursor()

cursor.execute('''
    DROP TABLE IF EXISTS audienceslovecount;
''')

cursor.execute('''
    CREATE TABLE audienceslovecount(word TEXT, count INT)
''')
db.commit()

cursor = db.cursor()

cursor.execute('''
    DROP TABLE IF EXISTS audienceshatecount;
''')
cursor.execute('''
    CREATE TABLE audienceshatecount(word TEXT, count INT)
''')
db.commit()

cursor = db.cursor()

cursor.execute('''
    DROP TABLE IF EXISTS criticshatecount;
''')

cursor.execute('''
    CREATE TABLE criticshatecount(word TEXT, count INT)
''')
db.commit()

cursor = db.cursor()

cursor.execute('''
    DROP TABLE IF EXISTS criticslovecount;
''')
cursor.execute('''
    CREATE TABLE criticslovecount(word TEXT, count INT)
''')
db.commit()

cursor = db.cursor()

cursor.execute('''
    DROP TABLE IF EXISTS corpuscount;
''')

cursor.execute('''
    CREATE TABLE corpuscount(word TEXT, count INT)
''')
db.commit()

for key, value in audienceslovecount.items():
	cursor = db.cursor()
	cursor.execute('''INSERT INTO audienceslovecount(word, count)
                  VALUES(?,?)''', (key, value))

db.commit()

for key, value in audienceshatecount.items():
	cursor = db.cursor()
	cursor.execute('''INSERT INTO audienceshatecount(word, count)
                  VALUES(?,?)''', (key, value))

db.commit()



for key, value in criticshatecount.items():
	cursor = db.cursor()
	cursor.execute('''INSERT INTO criticshatecount(word, count)
                  VALUES(?,?)''', (key, value))

db.commit()


for key, value in criticslovecount.items():
	cursor = db.cursor()
	cursor.execute('''INSERT INTO criticslovecount(word, count)
                  VALUES(?,?)''', (key, value))

db.commit()

for key, value in corpuscount.items():
	cursor = db.cursor()
	cursor.execute('''INSERT INTO corpuscount(word, count)
                  VALUES(?,?)''', (key, value))

db.commit()

cursor = db.cursor()

cursor.execute('''
    DROP TABLE IF EXISTS allcounts;
''')

cursor.execute('''
    CREATE TABLE allcounts(word TEXT, corpusCount INT, audiencesLoveCount INT, audiencesHateCount INT, criticsHateCount INT, criticsLoveCount INT)
''')

db.commit()

cursor.execute('''SELECT a.word, a.count as corpusCount, b.count as audiencesLoveCount, c.count as audiencesHateCount, d.count as criticsHateCount, e.count as criticsLoveCount FROM corpuscount a
	LEFT JOIN audienceslovecount b ON a.word = b.word
	LEFT JOIN audienceshatecount c ON a.word = c.word
	LEFT JOIN criticshatecount d ON a.word = d.word
	LEFT JOIN criticslovecount e ON a.word = e.word
	ORDER BY corpusCount DESC''')
fulldb = cursor.fetchall() #retrieve the first row


cursor.execute('''SELECT word, corpus_ratio, audiencesLoveRatio/corpus_ratio as  audiencesLoveIndex,
audiencesHateRatio/corpus_ratio as  audiencesHateIndex,
criticsHateRatio/corpus_ratio as  criticsHateIndex,
criticsLoveRatio/corpus_ratio as  criticsLoveIndex

  FROM 

(SELECT word, corpusCount*1.0/(SELECT SUM(corpusCount) FROM (SELECT a.word, a.count as corpusCount, b.count as audiencesLoveCount, c.count as audiencesHateCount, d.count as criticsHateCount, e.count as criticsLoveCount FROM corpuscount a
	LEFT JOIN audienceslovecount b ON a.word = b.word
	LEFT JOIN audienceshatecount c ON a.word = c.word
	LEFT JOIN criticshatecount d ON a.word = d.word
	LEFT JOIN criticslovecount e ON a.word = e.word
	ORDER BY corpusCount DESC)) as corpus_ratio,  
	
	audiencesLoveCount*1.0/(SELECT SUM(audiencesLoveCount) FROM (SELECT a.word, a.count as corpusCount, b.count as audiencesLoveCount, c.count as audiencesHateCount, d.count as criticsHateCount, e.count as criticsLoveCount FROM corpuscount a
	LEFT JOIN audienceslovecount b ON a.word = b.word
	LEFT JOIN audienceshatecount c ON a.word = c.word
	LEFT JOIN criticshatecount d ON a.word = d.word
	LEFT JOIN criticslovecount e ON a.word = e.word
	ORDER BY corpusCount DESC)) as audiencesLoveRatio,
	
	audiencesHateCount*1.0/(SELECT SUM(audiencesHateCount) FROM (SELECT a.word, a.count as corpusCount, b.count as audiencesLoveCount, c.count as audiencesHateCount, d.count as criticsHateCount, e.count as criticsLoveCount FROM corpuscount a
	LEFT JOIN audienceslovecount b ON a.word = b.word
	LEFT JOIN audienceshatecount c ON a.word = c.word
	LEFT JOIN criticshatecount d ON a.word = d.word
	LEFT JOIN criticslovecount e ON a.word = e.word
	ORDER BY corpusCount DESC)) as audiencesHateRatio,
	
	criticsHateCount*1.0/(SELECT SUM(criticsHateCount) FROM (SELECT a.word, a.count as corpusCount, b.count as audiencesLoveCount, c.count as audiencesHateCount, d.count as criticsHateCount, e.count as criticsLoveCount FROM corpuscount a
	LEFT JOIN audienceslovecount b ON a.word = b.word
	LEFT JOIN audienceshatecount c ON a.word = c.word
	LEFT JOIN criticshatecount d ON a.word = d.word
	LEFT JOIN criticslovecount e ON a.word = e.word
	ORDER BY corpusCount DESC)) as criticsHateRatio,
	
	criticsLoveCount*1.0/(SELECT SUM(criticsLoveCount) FROM (SELECT a.word, a.count as corpusCount, b.count as audiencesLoveCount, c.count as audiencesHateCount, d.count as criticsHateCount, e.count as criticsLoveCount FROM corpuscount a
	LEFT JOIN audienceslovecount b ON a.word = b.word
	LEFT JOIN audienceshatecount c ON a.word = c.word
	LEFT JOIN criticshatecount d ON a.word = d.word
	LEFT JOIN criticslovecount e ON a.word = e.word
	ORDER BY corpusCount DESC)) as criticsLoveRatio
	
	
	FROM 

(SELECT a.word, a.count as corpusCount, b.count as audiencesLoveCount, c.count as audiencesHateCount, d.count as criticsHateCount, e.count as criticsLoveCount FROM corpuscount a
	LEFT JOIN audienceslovecount b ON a.word = b.word 
	LEFT JOIN audienceshatecount c ON a.word = c.word
	LEFT JOIN criticshatecount d ON a.word = d.word
	LEFT JOIN criticslovecount e ON a.word = e.word
	
	
	
	ORDER BY corpusCount DESC)
	
	)
	WHERE audiencesLoveIndex IS NOT NULL
	AND audiencesHateIndex IS NOT NULL
	AND criticsLoveIndex IS NOT NULL
	AND criticsHateIndex IS NOT NULL
	
	ORDER BY audiencesLoveIndex DESC
''')
ratiodb = cursor.fetchall() #retrieve the first row

for x, y in moviedict.items():
	print y[0], y[1], y[2], y[3], y[6]


for row in fulldb:
    # row[0] returns the first column in the query (name), row[1] returns email column.
    print('{0} : Corpus: {1} , Audiences Love: {2}, Audiences Hate: {3}, Critics Hate: {4}, Critics Love {5},'.format(row[0], row[1], row[2], row[3], row[4], row[5]))


for row in ratiodb:

	print('{0} : Corpus: {1} , Audiences Love Ratio: {2}, Audiences Hate Ratio: {3}, Critics Hate Ratio: {4}, Critics Love Ratio {5},'.format(row[0], row[1], row[2], row[3], row[4], row[5]))

download_dir = "export_" + str(time.time()) + ".csv"	

csv = open(download_dir, "w") 
#"w" indicates that you're writing strings to the file

columnTitleRow = "word, corpus, audience_love_ratio, audience_hate_ratio, critics_hate_ratio, critics_love_ratio\n"
csv.write(columnTitleRow)

for row in ratiodb:
	word = row[0]
	corpus = row[1]
	audience_love_ratio = row[2]
	audience_hate_ratio	= row[3]
	critics_hate_ratio = row[4]
	critics_love_ratio = row[5]
	row = str(word) + "," + str(corpus) + "," + str(audience_love_ratio) + "," + str(audience_hate_ratio) + "," + str(critics_hate_ratio) + "," + str(critics_love_ratio) + "\n"
	csv.write(row)

cursor = db.cursor()

cursor.execute('''
    DROP TABLE IF EXISTS ratiodb;
''')
cursor.execute('''
    CREATE TABLE ratiodb(word TEXT, corpus REAL, audience_love_ratio REAL, audience_hate_ratio REAL, critics_hate_ratio REAL, critics_love_ratio REAL)
''')
db.commit()

for row in ratiodb:
	cursor = db.cursor()
	cursor.execute('''INSERT INTO ratiodb(word, corpus, audience_love_ratio, audience_hate_ratio, critics_hate_ratio, critics_love_ratio)
                  VALUES(?,?,?,?,?,?)''', (row[0], row[1], row[2], row[3], row[4], row[5]))

db.commit()


cursor = db.cursor()

cursor.execute('''
    DROP TABLE IF EXISTS fulldb;
''')
cursor.execute('''
    CREATE TABLE fulldb(title TEXT, date INT, ratio REAL, audienceScore REAL, tMeterScore REAL, audienceReviews TEXT, criticReviews TEXT, vote_count INT)
''')
db.commit()

for key, value in moviedict.items():
	cursor = db.cursor()
	cursor.execute('''INSERT INTO fulldb(title, date, ratio, audienceScore, tMeterScore, audienceReviews, criticReviews, vote_count)
                  VALUES(?,?,?,?,?,?,?,?)''', (key, value[0], value[1], value[2], value[3], value[4], value[5], value[6]))

db.commit()

db.close()

