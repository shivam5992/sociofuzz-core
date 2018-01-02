from dbHandler import add, get, update, db, db1, fs, serveraddress as serverAddress
from Extractor  import Extract, process as MetaExtractor
from Analyzer import remove_duplicate_media, fix_images, analyze_moviedata as Analyze
from DataAnalyzer.Stars import get_stars
from AddParamaters import AddProcess
from datetime import datetime
import time, ast, json
from TweetEngine import TwitterStreaming, TwitterREST, TwitterTimeline
import HTMLParser
import pymongo
import multiprocessing.pool
import multiprocessing, os
from urllib import urlretrieve
from datetime import datetime
from celery import Celery
from getNews import updateNews, pushNewsToInstance
celery = Celery('MovieController',broker = "redis://")
import os


class NoDaemonProcess(multiprocessing.Process):
    def _get_daemon(self):
        return False
    def _set_daemon(self, value):
        pass
    daemon = property(_get_daemon, _set_daemon)

class MyPool(multiprocessing.pool.Pool):
    Process = NoDaemonProcess

def getRankSocial(rank, negCount):
	n = negCount
	newRank = ""
	if n >=50:
		newRank = rank - rank/5
	elif n >= 30 and n < 50:
		newRank = rank - rank/10
		if rank > 7.5:
			newRank = rank - rank/10 
	elif n >= 25 and n < 30:
		newRank = rank - rank/20 
	elif n >= 20 and n < 25:
		newRank = rank - rank/30 
	elif n >= 10 and n < 20:
		newRank = rank - rank/50
	else:
		newRank = rank + rank/50
	if newRank == "" and  rank > 7.5:
		newRank = rank + rank/20 
		if newRank >= 9.7:
			newRank = 9.7

	if newRank < 0.5:
			newRank = 0.5
	modifiedRank = round(newRank, 1)
	return modifiedRank

def getPreRank(p,n):
	if n >= 50:
		return 3
	elif n >= 40 and n < 50:
		return 4
	elif n >= 30 and n < 40:
		if p > 30:
			return 5 
		else:
			return 4.5
	else:
		if p > 40 and p <= 50:
			return 6.7
		elif p > 50 and p <= 60:
			return 7.5
		elif p > 60:
			return 8
		else:
			return 6

month = {
	'01' : 'Jan',
	'02' : 'Feb',
	'03' : 'Mar',
	'04' : 'Apr',
	'05' : 'May',
	'06' : 'Jun',
	'07' : 'Jul',
	'08' : 'Aug',
	'09' : 'Sep',
	'10' : 'Oct',
	'11' : 'Nov',
	'12' : 'Dec',
}

def reform_date(date):
	if date.count("/") == 2:
		date = month[date.split("/")[1]] + " " + date.split("/")[0] + ", 20" +  date.split("/")[2]
	return date

def reform_time(timed):
	timed = timed.replace("[1]","").replace("[2]","").replace("[3]","")
	timed = timed.replace(",","").lower().strip()
	if "(" in timed:
		timed = timed.split("(")[0]
	timed = timed.replace("minutes","M")
	timed = timed.replace("mins","M").replace("minute","M").replace("min","M")
	timed = timed.replace("hours", "H").replace("hrs", "H").replace("hr", "H")
	if "H" in timed:
		if timed.startswith("1"):
			return timed.replace("H","Hour,").replace("M","Minutes") 
		else:
			return timed.replace("H","Hours,").replace("M","Minutes") 
	else:
		hour = int(float(timed.replace(" M","")) / 60)
		minutes = int(float(timed.replace(" M","")) % 60)
		if hour != 1:
			return str(hour) + " Hours, " + str(minutes) + " Minutes"
		else:
			return str(hour) + " Hour, " + str(minutes) + " Minutes"


def update_movie_seeds(mnames):
	add.add_movie_meta_data(mnames)

def update_movie_final(moviename, update_meta = False, update_box = False, update_analyze = False, TrimFlag = False, pre = False):
	if update_meta == True:
		MetaExtractor(moviename)

	meta = db['MovieJson'].find_one({  '_id'  : moviename })
	movie_rank = meta['crawl_data']['imdb_data']['rating']

	if update_analyze == True:
		analyzed = Analyze(moviename)
		movie_rank = getRankSocial(movie_rank, analyzed['sentiment']['negative'])
		val = int(str(analyzed['total_tweets']).replace(",",""))

		if pre == True:
			movie_rank = getPreRank(analyzed['sentiment']['positive'], analyzed['sentiment']['negative'])
			stars = get_stars(movie_rank)

		get.ParseSocialImages(moviename)

	else:
		analyzed = []
		val  = 0
	stars = get_stars(movie_rank)
	mid = meta['crawl_data']['MovieId']

	if update_box == True:
		print "Extracting Box"
		boxoffice = Extract.getBoxOffice(moviename)
	else:
		if 'box' in meta['crawl_data']:
			mbox = meta['crawl_data']['box']
			boxoffice = mbox
		else:
			boxoffice = None

	ignoreNews = ['iBooks', 'review', 'trailer', 'boxoffice']
	news_data_list = []
	for news in meta['news_data']:
		if type(news['title']) == list:
			ntitle = news['title'][0].encode("utf8").lower()
		else:
			ntitle = news['title'].encode("utf8").lower()
		dsc = news['desc_text'].encode("utf8")

		if any(wrd in ntitle for wrd in ignoreNews):
			pass
		else:
			if str(dsc).strip() == "":
				txt = news['text'].encode("utf8").split(". ")
				md = news['meta_description'].encode("utf8").split(". ")
				
				if len(txt) >= 2:
					news['desc_text'] = ". ".join(txt[:3]) 
				elif len(md) >= 2:
					news['desc_text'] = ". ".join(txt[:3])
			if news['desc_text'] != "":
				news_data_list.append(news) 

		if TrimFlag == True:
			del news['text']


	for rvw in meta['reviews_data']:
		if rvw['name'] == "Source":
			rvw['name'] = rvw['source']

	ndate, ntimed = "None" , "None"
	if 'Running time' in meta['crawl_data']['wiki']:
	 	tm = meta['crawl_data']['wiki']['Running time']
		ntimed = reform_time(tm)

	if 'Release dates' in meta['crawl_data']['wiki']:
		date = meta['crawl_data']['wiki']['Release dates']
		ndate = reform_date(date)

	movie_json = {}
	movie_json['new_date'] = ndate
	movie_json['new_time'] = ntimed
	movie_json['name'] = moviename
	movie_json['meta'] = meta['crawl_data']
	movie_json['reviews_data'] = meta['reviews_data']
	movie_json['news_data'] = news_data_list
	movie_json['MovieId'] = int(mid)
	movie_json['analyzed'] = analyzed
	movie_json['rank'] = movie_rank
	movie_json['stars'] = stars
	movie_json['box'] = boxoffice
	movie_json['_id'] = moviename
	movie_json['meta']['trivias'] = [HTMLParser.HTMLParser().unescape(x) for x in meta['crawl_data']['trivias']]
	movie_json['sfreview'] = ""
	movie_json['news_count'] = int(len(news_data_list))/10 + 1
	movie_json['reviews_count'] = int(len(meta['reviews_data']))/10 + 1
	movie_json['total_tweets_int'] = val
	movie_json['reviews_count_int'] = len(meta['reviews_data'])

	if movie_json['_id'] == "FourPillarsOfBasement":
		movie_json['meta']['wiki']['name'] = "Four Pillars Of Basement"

	update.update_movie_json(moviename, movie_json)
	print "Inserted Updated Movie Json"


def update_trend_final(trendname, imagelink):
	analyzed = Analyze(trendname, isTrend = True)
	# print analyzed
	val = int(str(analyzed['total_tweets']).replace(",",""))	

	movie_json = {}
	movie_json['name'] = trendname
	movie_json['_id'] = trendname.replace(' ',"")
	movie_json['analyzed'] = analyzed
	movie_json['image'] = imagelink
	movie_json['total_tweets_int'] = val

	update.update_movie_json(trendname.replace(' ',""), movie_json, isTrend = True)
	print "Inserted Updated Movie Json"
	
def start_tweet_Extraction(moviename, streaming = False, update = False, trend = False, trendQueries = False):
	authKeyPath = 'vocab/TwitterAPI.csv'
	portAddress = 27017
	dbName = 'MovieMasterTweets'
	collectionName = moviename + "_RawTweets"

	if trend == False:
		query = get.check_doc_exist('Movie Name', moviename ,'moviemeta')['TwitterHandles']
		query = query.strip()
		if query != "None":
			TwitterTimeline.TwitterTimeline(handle=query,authKeyPath=authKeyPath,dbName=dbName,\
				collectionName=collectionName, serverAddress = serverAddress, portAddress = portAddress,
				update = update)
			print "Extraction Completed for Twitter TimeLine"

		keywords = get.check_doc_exist('Movie Name', moviename ,'moviemeta')['Keywords']
		query = keywords.replace(";", " OR ").replace("  "," ")
		query = moviename
	else:
		query = trendQueries.replace(";", " OR ").replace("  "," ")
	

	rest = TwitterREST.TwitterREST(searchQuery=query,authKeyPath=authKeyPath,dbName=dbName,\
		collectionName=collectionName, serverAddress = serverAddress, portAddress = portAddress,\
		update = update)
	print "Extraction Completed REST"

	if streaming == True:
		print "Starting Streaming"
		query = keywords.replace(";", ",")
		TwitterStreaming.TwitterStream(searchQuery = query, authKeyPath = authKeyPath, dbName = dbName, collectionName = collectionName, serverAddress=serverAddress, portAddress=portAddress)


def AddParamProcess(moviename, update = False):
	collection_name = moviename + "_RawTweets"
	if update == False:
		json_list = db[collection_name].find()
	else:
		json_list = db[collection_name].find({'isNew' : 'True'})
	json_movie_list = []
	for i, x in enumerate(json_list):
		json_movie_list.append(x)
	AddProcess(json_movie_list, moviename)

def ImageToDB(moviename):
	coll = db['movie_jsons'].find_one({'_id' : moviename})

	try:
		poster1 = coll['meta']['wiki']['poster']
		wikipath = 'vocab/Hash/' + moviename + "_wikiposter.jpg"
		urlretrieve(poster1, wikipath)
		fs.put(open(wikipath,'rb'), _id = moviename + "_wiki")
	except Exception as E:
		print ">>>", E
		print "Already There Wiki"
	
	try:
		poster2 = "http:"+coll['meta']['buff']['gallery'][0]['Posters'][0].replace('w=1000','w=200')	
		buffpath = 'vocab/Hash/' + moviename + "_buffposter.jpg"
		urlretrieve(poster2, buffpath)
		fs.put(open(buffpath,'rb'), _id = moviename + "_buff")
	except Exception as E:
		print E
		print "Already There Buff"
		
def FirstTime(moviename, pre = False):
	update_movie_seeds()
	print "Updated Seeds"
	
	start_tweet_Extraction(moviename)
	print "Extracted Tweets Data"
	
	update_movie_final(moviename, update_meta = True,  update_box = False , update_analyze = False, pre = pre)
	print "Extracted Meta Data"
	
	AddParamProcess(moviename)
	print "Added Parameters"

	db[moviename + "_ParsedTweets"].ensure_index([('text', pymongo.TEXT)])

	update_movie_final(moviename, update_meta = False,  update_box = False , update_analyze = True, pre = pre)
	print "Updated Movie Analyzed"
	
	ImageToDB(moviename)
	a, b, c = get.getImagesFromGrid(moviename)
	db.movie_jsons.update({ '_id' : moviename }, 
		{'$set': {'wikiimg': [a], 'buffimg' : [b] }})
	
	# p , n = get.get_sentiment_tweets_api(moviename + '_ParsedTweets', 15)
	p, n = update.valid_tweets(moviename)
	pop = get.get_popular_tweets(moviename + "_ParsedTweets", 20)
	doc = {'pos' : p, 'neg' : n, 'pop' : pop, 'dataType' : 'tweet'}
	db[moviename + '_ParsedPopTweets'].insert(doc)
	db.movie_jsons.update({'_id' : moviename}, {'$set' : { 'actsimg' : c }})

	update.map_lyrics(moviename)
	update.trim_movie_json(moviename)
	


	

@celery.task
def CronTime(moviename, trend = False, pre = False):
	if trend == True:
		update_movie_final(moviename, update_meta = False,  update_box = False , update_analyze = True, TrimFlag = True)

	else:	
		start_tweet_Extraction(moviename, update = True)
		AddParamProcess(moviename, update = True)
		db[moviename + "_ParsedTweets"].ensure_index([('text', pymongo.TEXT)])

		update_movie_final(moviename, update_meta = True,  update_box = False , update_analyze = False, pre = pre)
		update_movie_final(moviename, update_meta = False,  update_box = True , update_analyze = True, TrimFlag = True, pre = pre)
		
		#IMP Every Time
		p, n, pop = update.valid_tweets(moviename)
		doc = {'pos' : p, 'neg' : n, 'pop' : pop, 'dataType' : 'tweet'}
		db[moviename + '_ParsedPopTweets'].remove({'dataType' : 'tweet'})  
		db[moviename + '_ParsedPopTweets'].insert(doc)
		
		# IMP Every Time
		a, b, c = get.getImagesFromGrid(moviename)
		db['movie_jsons'].update({'_id' : moviename}, {'$set': {'wikiimg': [a], 'buffimg' : [b] }})
		db['movie_jsons'].update({'_id' : moviename}, {'$set': {'actsimg': c }})

	if pre == True:
		db.movie_jsons.update({ '_id' : moviename }, {'$set': {'pre': True }})

	update.map_lyrics(moviename)
	update.trim_movie_json(moviename)
	

def AddActor(url, name):
	actpath = 'vocab/Hash/' + name.replace(" ","_") + ".jpg"
	urlretrieve(url, actpath)
	fs.put(open(actpath,'rb'), _id = name.replace(" ","_"))
	os.remove(actpath)




def update_trend():
	trend = 'SalmanVerdict'
	trendqueries = 'Salman Verdict'
	imagelink = "http://www.indicine.com/images/gallery/bollywood/actors/salman-khan/15-salman-khan-medium.jpg"

	start_tweet_Extraction(trend, trend=True, trendQueries = trendqueries)
	AddParamProcess(trend)
	db[trend + "_ParsedTweets"].ensure_index([('text', pymongo.TEXT)])
	update_trend_final(trend, imagelink)

	p , n = get.get_sentiment_tweets_api(trend + '_ParsedTweets', 9)
	pop = get.get_popular_tweets(trend + "_ParsedTweets", 18)
	doc = {'pos' : p + n , 'neg' : n, 'pop' : pop, 'dataType' : 'tweet'}
	db[trend.replace(" ","") + '_ParsedPopTweets'].drop()  
	db[trend.replace(" ","") + '_ParsedPopTweets'].insert(doc)

	updateNews(trend, trend.replace(" ",""), db)

	add.PushToInstance(trend, get, isTrend = True)
	pushNewsToInstance(trend.replace(" ",""), db, db1)

# AddActor('http://www.indicine.com/images/gallery/bollywood/actress/kriti-sanon/23977-Kriti-Sanon-medium.jpg', 'Kriti Sanon')
# mnames = ['Wazir']
# update_movie_seeds(mnames)
# add.AddTrailer('Fitoor', 'https://www.youtube.com/watch?v=FZLDoF7VfaQ', '20160212')

movienames = ['Wazir']
for moviename in movienames:
	print moviename
	# CronTime(moviename, pre = False)
	# add.PushToInstance(moviename, get)
	
	# print "updating news"
	# mname = db['movie_jsons'].find_one({'_id' : moviename} , {'_id' : 0, 'meta.wiki.name' : 1})['meta']['wiki']['name']
	# updateNews(mname, moviename, db)
	# pushNewsToInstance(moviename, db, db1)