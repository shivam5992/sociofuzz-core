from DataAnalyzer.InfluencerExtractor import calculate_influence_score
from DataAnalyzer.RatingExtractor import rate

from dbHandler import get, add, update, db
from operator import itemgetter
from eventlet.timeout import Timeout

from collections import Counter
import operator, math, urlparse, json, ast
import shutil
import struct
import os
import hashlib
import requests
import urllib


def get_reach(list_of_tweet_jsons):
	users = {}
	reach = 0
	for i, tweet in enumerate(list_of_tweet_jsons):
		uid = str(tweet['user']['id'])
		if uid not in users:
			users[uid] = 1
			foll_count = tweet['user']['followers_count']
			reach += foll_count
	return users, reach


def tweet_day_freq(data, flag):
	dict1 = {}
	for each in data:
		new = each.split(' ')
		if flag == 'day':
			interest = str(new[0])
		else:
			interest = str(new[3].split(":")[0])
		if interest in dict1:
			dict1[interest] += 1
		else:
			dict1[interest] = 1
	tot = sum([y for x,y in dict1.iteritems()])
	
	for x,y in dict1.iteritems():
		dict1[x] = {}
		dict1[x]['rad'] = float(y)/tot * 100
		dict1[x]['val'] = y
	return dict1



### CLEAN HASHTAG

def fix_entities(tags):
	tag_list = {}
	for x in tags:
		for tag in x['entities']['hashtags']:
			tg = tag['text']
			
			if tg not in tag_list:
				tag_list[tg] = 1 
			elif tg.upper() in tag_list:
				tag_list[tg.upper()] += 1
			else:
				tag_list[tg] += 1

	sorted_hashtag = sorted(tag_list.items(), key=operator.itemgetter(1),reverse=True)
	total_tags = 0
	for each in sorted_hashtag[:5]:
		total_tags += each[1]

	tagsq = []
	for i, each in enumerate(sorted_hashtag[:5]):
		if i == 0:
			val = math.floor((float(each[1]) / total_tags)*100)
		else:
			val = math.ceil((float(each[1]) / total_tags)*100)
		tagsq.append((each[0], val, each[1]))
	return tagsq

def fix_mentions(tags):
	tag_list = {}
	for x in tags:
		for tag in x['entities']['user_mentions']:
			if tag:
				tg = tag['screen_name']
				if tg not in tag_list:
					tag_list[tg] = 1 
				else:
					tag_list[tg] += 1

	sorted_hashtag = sorted(tag_list.items(), key=operator.itemgetter(1),reverse=True)[:5]
	total_tags = 0
	for each in sorted_hashtag:
		total_tags += each[1]
	tagsq = []
	for i, each in enumerate(sorted_hashtag):
		if i == 0:
			val = math.floor((float(each[1]) / total_tags)*100)
		else:
			val = math.ceil((float(each[1]) / total_tags)*100)
		tagsq.append((each[0], val, each[1]))
	return tagsq


def parse_urls(urls):
	sites = []
	important = []
	mappurl = {}

	for url in urls:
		rags = url['entities']['urls']
		for x in rags:
			if len(x) == 0:
				continue
			x = x['expanded_url']
			if ".com" in x:
				if "twitter" in x or "youtube" in x or "instagram" in x:
					continue
				else:
					x = x.replace("http://","").replace("https://","")
					if len(x) > 35:
						if x.startswith("www"):
							important.append(x)
							mappurl[x] = url['text']
						else:
							important.append("www." + x)
							mappurl["www." + x] = url['text']
			
			sites.append(urlparse.urlparse(x)[1])
	
	sites = sorted(Counter(sites).items(), key=operator.itemgetter(1), reverse=True)
	true_sites = []
	allext = [".com", ".in", ".net", "co.in"]
	for xx in sites:
		if any(ext in xx[0] for ext in allext):
			true_sites.append(xx)
	important = sorted(Counter(important).items(), key=operator.itemgetter(1), reverse=True)
	nimp = []
	for x1 in important:
		x1 = list(x1) 
		x1.append(mappurl[x1[0]])
		nimp.append(x1)
	return true_sites, nimp, mappurl

def fix_stand(alist):
	blist = []
	for x in alist:
		lab = {}
		lab['label'] = x[0]
		lab['value'] = x[1]
		blist.append(lab)
	return blist

def fix_hour(alist):
	mapped = {
	'01': '6 AM','02': '7 AM','03': '8 AM','04': '9 AM','05': '10 AM','06': '11 AM',
	'07': '12 AM','08': '1 PM','09': '2 PM','10': '3 PM','11': '4 PM','12': '5 PM',
	'13': '6 PM','14': '7 PM','15': '8 PM','16': '9 PM','17': '10 PM','18': '11 PM',
	'19': '12 PM','20': '1 AM','21': '2 AM','22': '3 AM','23': '4 AM','00': '5 AM',
	}
	blist = []
	for x in alist:
		lab = {}
		lab['frequency'] = x['frequency']
		lab['letter'] = mapped[x['letter']]
		blist.append(lab)
	return blist

def fix_city(alist):
	sm = 0 
	for x in alist[:5]:
		sm += x[1]

	nl = []
	for x in alist[:5]:
		x = list(x)
		x.append(round(float(x[1])/sm,2))
		nl.append(x)
	return nl

def analyze_moviedata(moviename, isTrend = False):
	if isTrend == False:
		metadata = get.check_doc_exist('Movie Name', moviename ,'moviemeta')
	
	movieDB = moviename + "_ParsedTweets" 
	data = get.get_jsons_collection(movieDB)
	analyzed = {}
	tot_tweet = data.count()
	unique_users = get.getUniqueDetailsFromDoc('user.id', 'user', movieDB)
	reluser = []
	for xx in unique_users['result']:
		nm = xx['projection']['name']
		lnk = xx['projection']['profile_image_url_https']
		this = {}
		this['name'] = nm 
		this['lnk'] = lnk
		reluser.append(this)
	analyzed['user_details'] = reluser[:42]
	 
	totuser_var = len(unique_users['result'])

	reachvar = get.getTotalCountOfKey('user.followers_count', movieDB)
	reachvar = reachvar[0]['totalCount']
	analyzed['reach'] = format(reachvar, ',d')
	analyzed['total_users'] = format(totuser_var, ',d')
	analyzed['total_tweets'] = format(tot_tweet, ',d')

	standardise_cities = []
	locations = get.get_location_count(movieDB)
	for loc in locations:
		loc = loc['user']['location'].lower()
		words = loc.split()
		[standardise_cities.append(wrd.title()) for wrd in words if get.check_doc_exist('_id', wrd, 'indian_cities')]
	standardise_cities1 = []	
	standardise_cities1.append(['City','Count'])
	standardise_cities1 = sorted(Counter(standardise_cities).items(), key=operator.itemgetter(1), reverse=True)	
	analyzed['cities'] = fix_stand(standardise_cities1[:5])
	analyzed['cities_count'] = len(standardise_cities1)
	analyzed['city_per'] = fix_city(standardise_cities1)


	

	analyzed['sentiment'] = get.get_sentiment_count(movieDB)
	#print "Sentiment"

	hashtaged = get.get_hashtag_count(movieDB)
	tags = fix_entities(hashtaged)
	analyzed['hashtags'] = tags
	#print "Hashtags"
	
	mentions = get.get_mention_count(movieDB)
	mentions = fix_mentions(mentions)
	analyzed['mentions'] = mentions
	#print "Mentions"

	urls = get.get_url_count(movieDB)	
	urls = parse_urls(urls)
	analyzed['links'] = urls[0][:8]
	analyzed['links_length'] = len(urls[0])
	analyzed['websites'] = urls[1][:6]
	#print "Websites"
	
	gend = get.get_gender_count(movieDB)
	gender = [x['user']['gender'] for x in gend]
	
	gender = dict(Counter(gender))
	if 'male' not in gender:
		gender['male'] = 10
	if 'female' not in gender:
		gender['female'] = 10
	tot = gender['male'] + gender['female']

	gendr = {'male' : int(math.floor((float(gender['male'])/tot)*100)) , 'female' : int(math.ceil((float(gender['female'])/tot)*100)) }
	analyzed['genders'] = gendr	
	#print "Genders"

	
	loggs = get.getInfluencerData(movieDB)
	loggs = sorted(loggs, key=lambda k: k['log'], reverse = True)[:6]
	analyzed['logscore'] = loggs

	#print "Influencers"
	
	
	times = get.get_timestamp_count(movieDB)
	days = tweet_day_freq(times, 'day')
	daylist = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

	nl = []
	for eachday in daylist:
		if eachday not in days:
			days[eachday] = {}
			days[eachday]['rad'] = 10
			days[eachday]['val'] = "100+"
			nl.append(days[eachday]['rad'])
		else:
			nl.append(days[eachday]['rad'])

	minFreq = min(nl)
	maxFreq = max(nl)

	for tag in days:
		freqTag = days[tag]['rad']
		fontMax = 45
		fontMin = 10
		K = (freqTag - minFreq)/(maxFreq - minFreq)
		frange = fontMax - fontMin
		C = 4
		
		K = float(freqTag - minFreq)/(maxFreq - minFreq)
		size = fontMin + (C*float(K*frange/C))
		days[tag]['rad'] = size

	


	hours = tweet_day_freq(times, 'hour')
	listedhours = []
	for x,y in hours.iteritems():
		a = {}
		a['letter'] = x
		a['frequency'] = y['val']
		listedhours.append(a)
	hours = sorted(listedhours, key=lambda k: k['letter']) 
	analyzed['days'] = days
	analyzed['hours'] = fix_hour(hours)
	#print "TimeSeries"


	ratingdata = open("vocab/ratingvocab.csv").read().strip().split("\n")
	themes_rating = get.get_theme_rating(moviename, ratingdata)
	analyzed['themes_rating'] = themes_rating
	#print "ratings"

	if isTrend == False:
		actordata = []
		for actor in metadata['actors'].split(";"):
			actor = actor.strip()
			if actor == "[1]":
				continue
			try:
				actorvocab = get.check_doc_exist('_id', actor ,'actorvocab')
				string = actor + "," + actorvocab['vocab'].encode('utf-8').replace(";",",")	
			except:
				# print "vocab", actor
				string = actor 	
			actordata.append(string)
			
		actor_rating = get.get_theme_rating(moviename, actordata)
		rated_list = []
		for x,y in actor_rating.iteritems():
			rated = {}
			x = x.replace("Asin","Asin Thottumkal")
			act = get.check_doc_exist('_id', x, 'actorMaster1')
			if act == None:
				pass
				# print "!!! Update", x
			else:
				rated['name'] = x
				rated['rating'] = y['val']
				rated['tweets'] = y['tweets']
				rated['url'] = act['url']
				if 'poster' in act:
					rated['poster'] = act['poster']
				else:
					rated['poster'] = ""
				rated_list.append(rated)
		rated_list = sorted(rated_list, key=lambda k: k['tweets'], reverse = True) 
		analyzed['actor_rating'] = rated_list
	
	return analyzed

def calculate_hash(url):
	resp = urllib.urlretrieve(url, "static/Hash/img1.jpg")
	return jpeg(file('static/Hash/img1.jpg'))

def jpeg(fh):
    hash = hashlib.md5()
    assert fh.read(2) == "\xff\xd8"
    while True:
        marker,length = struct.unpack(">2H", fh.read(4))
        assert marker & 0xff00 == 0xff00
        if marker == 0xFFDA:
            hash.update(fh.read())
            break
        else:
            fh.seek(length-2, os.SEEK_CUR)
    return "%r" % hash.digest()

def remove_duplicate_media(moviename):
	movieDB = moviename + '_ParsedTweets'
	data = get.get_medias(movieDB)
	try:
		mains = get.get_medias_hashed(moviename)
		hashedimgs = [x[0] for x in mains]
	except:
		hashedimgs = []


	for x in data:
		try:
			with Timeout(5, False):
				if x not in hashedimgs:
					hashed = calculate_hash(x)
					element = (x, hashed)
					add.add_image(element, moviename) 
		except Exception as E:
			continue

def exists(path):
    r = requests.head(path)
    return r.status_code == requests.codes.ok

def fix_images(moviename):
	coll = get.get_latest_movie_json(moviename)
	coll_ud = coll['analyzed']['user_details']
	newlist = []
	for each in coll_ud:
		imgpath = each['projection']['profile_image_url_https']
		if 'default' in imgpath:
			continue
		elif exists(imgpath) == True:
			newlist.append(each)
		else:
			print imgpath
	coll['analyzed']['user_details'] = newlist
	update.update_movie_json(moviename, coll)	