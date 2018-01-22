import urllib2
import json
import datetime
from lxml import html
import requests
from multiprocessing import Pool 
import numpy as np 
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

## Scraping settings (you can add more by visiting the documentation and appending to the URL)

movie_released_after = '2015-01-01' ## 
include_adult = 'false' ## No Porn
with_original_language = 'en' ## English films only
minimum_votes = '10' ## Not quite sure how this is determined, but 10 is enough to cut out weird, obscure movies while most blockbusters have thousands of votes
api_key = 'ffb134d4a18813bcf11b130277649fe3'
url = "https://api.themoviedb.org/3/discover/movie?primary_release_date.gte=" + movie_released_after + "&include_adult=" + include_adult + "&with_original_language=" + with_original_language + "&vote_count.gte=" + minimum_votes + "&api_key=" + api_key 
length = json.load(urllib2.urlopen(url))['total_pages']
dictionary = {'key':[None] * 6}
parray = []
bigstring = "a"
smallstring = "a"

def kickoff():
	for x in range(1, 2): ## Queries the movie DB API to figue out how many pages we need to turn
		turnPage(x)

def turnPage(x): ## "turns the page" and iterates the crawler through each item on the newest page

	data = json.load(urllib2.urlopen(url + "&page=" + str(x))) ## creates a JSON object from the movie DB API page's output 
	print "page " + str(x) + " of " +  str(length) + ","
	for index, element in enumerate(data['results']): ## loops through each element in the new JSON object and invokes the web crawler on it
		webCrawl(data, index)

def clean_data(x):
	x = x.replace(",", " ") ##
	x = x.replace("!", " ") ##
	x = x.replace(".", " ") ##
	x = x.replace(":", " ") ##
	x = x.replace("'", " ") ##
	x = x.replace("]", " ") ##
	x = x.replace("[", " ") ##
	x = x.replace("%", " ") ##
	x = x.replace("  ", " ")
	return x

def webCrawl(data, x): ## prepares the URL from the movie DB API and crawls the specific Rotten Tomatoes page

		title = data['results'][x]['title'] ## finds the title 
		title = title.lower() ## prepares the title to be inserted into the Rotten Tomatoes URL
		title = title.replace (" ", "_") ##
		title = title.replace (",", "") ##
		title = title.replace ("!", "") ##
		title = title.replace (".", "") ##
		title = title.replace (":", "") ##
		title = title.replace ("'", "") ##
		title = title.replace ("-", "") ##
		title = title.replace ("'", "") ##
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
		criticsConsensus = str(tree.xpath('//p[@class="critic_consensus superPageFontColor"]/text()')) ## uses xpath to extract the critical consensus
		tMeterScore = tMeterScore.replace("%", "") ## removes artifacts from the scores
		audienceScore = audienceScore.replace("[", "") ##
		audienceScore = audienceScore.replace("]", "") ##
		audienceScore = audienceScore.replace("%", "") ##
		audienceScore = audienceScore.replace("'", "") ##
		clean_data(criticsConsensus)

		if tMeterScore and not tMeterScore.isspace(): ## ensures both scores have values to be stored
			if audienceScore and not audienceScore.isspace():
				if tMeterScore != "0":
					if "No consensus yet" not in criticsConsensus:
						ratio = float(audienceScore) / float(tMeterScore)## calculates ratio of audience to critical reaction
						dictionary[title] = [date, audienceScore, tMeterScore, criticsConsensus, vote_count, ratio] ## adds values to dictionary
						parray.append(ratio) ## creates an array of ratios in order to later calculate percentiles
						print "movie " + str(x) + " " + " of " + str(len(data['results']))
						print criticsConsensus
		else:
			pass


### executable code below ### 

kickoff()

a = np.array(parray) ## creates numpy array from earlier ratio array

for x, y in dictionary.items(): ## for loop to combine reviews of movies in the 10th and 90th percentiles of ratio

	if y[5] >= np.percentile(a, 90):
		bigstring= bigstring + str(y[3])

	elif y[5] <= np.percentile(a, 10):
		smallstring = smallstring + str(y[3])



criticshate = WordCloud(    stopwords=STOPWORDS, 
                          background_color='blue',
                          width=1200,
                          height=1000
                         ).generate(bigstring)


criticslove = WordCloud(    stopwords=STOPWORDS, 
                          background_color='blue',
                          width=1200,
                          height=1000
                         ).generate(smallstring)


hatefile = "criticshate" + str(datetime.datetime.now()) + ".png"
lovefile = "criticslove" + str(datetime.datetime.now()) + ".png"

plt.imshow(criticshate)
plt.axis('off')
plt.savefig(hatefile)
print "saving criticshate.png"


plt.imshow(criticslove)
plt.axis('off')
plt.savefig(lovefile)
print "saving criticslove.png" 







