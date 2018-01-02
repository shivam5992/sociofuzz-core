from DataAnalyzer.utility import utility
import requests, json, re, ast
from dbHandler import get, add, update, db
from bson.json_util import dumps
from textblob import TextBlob
import time
# from celery import Celery
import multiprocessing.pool
import multiprocessing

# celery = Celery('AddParams20', broker = "redis://")

class NoDaemonProcess(multiprocessing.Process):
    def _get_daemon(self):
        return False
    def _set_daemon(self, value):
        pass
    daemon = property(_get_daemon, _set_daemon)

class MyPool(multiprocessing.pool.Pool):
    Process = NoDaemonProcess


def getTextFileAsDict(pathOfTextFile):
	listData = open(pathOfTextFile).read().split("\r\n")
	dictData = {}
	for each in listData:
		dictData[each] = ''
	return dictData

positiveList = getTextFileAsDict('vocab/positives.txt')
negativeList = getTextFileAsDict('vocab/negatives.txt')

class SentimentExtractor:
	def __init__(self):
		self.url = "http://sentimentanalyzer.appspot.com/api/classify.json"
		self.headers = {"content-type": "application/json"}
		
	def _get_bulk_sentiment(self, data):
		listtext = []
		for tid, text in data.iteritems():
			intjson = {}
			intjson["content"] = text
			intjson["lang"] = "en"
			intjson["tid"] = tid
			listtext.append(intjson)

		payload = {}
		payload["data"] = listtext
		resp = requests.post(self.url, data = json.dumps(payload), headers = self.headers)
		response = resp.text.encode("utf-8").decode("ascii","ignore").strip().replace("\n"," ")
		response = ast.literal_eval(response)
		return response
	

class GenderExtractor:
	def _extract_gender(self, name):
		try:
			if " " in name:
				nameis = str(name).strip().replace(" ","/")
			else:
				nameis = str(name) + "/a"
			url = "http://api.namsor.com/onomastics/api/json/gendre/" + nameis
			response = requests.post(url)
			gender = response.json()["gender"]
		except Exception as e:
			gender = "Unknown"
		return gender


class LocationExtractor:
	def __init__(self):
		self.keyList = open('vocab/LocationAPI.txt').read().split('\n')
		self.default_keyIndex = 1

	def check_for_correct_key(self):
		key_detail_list = self.keyList
		for key in key_detail_list:
			key = str(key).strip()
			res = self._location_call('India', key)
			if res['status'] == 'OK':
				return key

	def _location_call(self, address, key):
		url = 'https://maps.googleapis.com/maps/api/geocode/json?address='
		fullurl = url + address + '&key=' + str(key)
		resp = requests.get(fullurl)
		data = json.loads(resp.text)

		res = {}
		if len(data['results']) != 0:
			add = data['results'][0]['address_components']
			res['status'] = data['status']
			for ele in add:
				if ele['types'] == [u'country', u'political']:
					res['country'] = ele['long_name']
				else:
					res['country'] = "NA"
		else:
			res['status'] = data['status']
			res['country'] = "NA"
		return res

	def _get_country(self, keyword):
		key = str(self.keyList[self.default_keyIndex])
		res = self._location_call(keyword, key)

		if res['status'] == 'OK':
			pass
		elif res['status'] == 'OVER_QUERY_LIMIT':
			key = self.check_for_correct_key()
			res = self._location_call(keyword, key)

		if len(res) != 0:
			country = res['country']
		else:
			country = "NA"
		return country

		
def remove_duplicates(json_list):
	visited = {}
	unique = []
	for each in json_list:
		each = ast.literal_eval(utility.reform_json(each))
		tid = each['_id']
		if tid not in visited:
			visited[tid] = 1
			unique.append(each)
	return unique




def add_tweet_parameters(elem):
	moviename = elem[1]
	coll_fix = db[moviename + "_ParsedTweets"] 
	raw_coll = db[moviename + "_RawTweets"]

	loc = LocationExtractor()
	gend = GenderExtractor()
	sent = SentimentExtractor()

	id_text = {}
	main_dict = {}

	visited = {}
	for i,tweet in enumerate(elem[0]):
		
		try:
			tweet = dumps(tweet)
			tweet = json.loads(tweet)
			
			tid = tweet['_id']
			user_location = tweet['user']['location']
			
			''' Location Parser '''
			location = utility.remove_encoded(user_location) 
			

			if location.strip() == "":
				country = "NA"
			else:
				dblocation = get.get_value(location, 'location')
				if dblocation:
					country = dblocation
				else:
					try:
						country = loc._get_country(location)
						doc = { 'key' : str(location), 'value' : str(country) } 
						add.add_json_to_collection(doc, 'location')
					except Exception as E:
						print str(E)
						country = "NA"
		
			tweet['user']['country'] = country
			

			''' Gender Parser '''
			name = tweet['user']['name']
			name = utility.remove_encoded(name)
			name = utility.punctuation_free(name)
			if name.strip() == "":
				gender = "Unknown"
			else:
				dbgender = get.get_value(name, 'genders')
				if dbgender:
					gender = dbgender
				else:
					gender = gend._extract_gender(name)
					doc = { 'key' : str(name), 'value' : str(gender) } 
					add.add_json_to_collection(doc, 'genders')

			tweet['user']['gender'] = gender

			''' Popularity Score '''
			vf = tweet['user']['verified']
			fc = tweet['user']['followers_count']
			rt = tweet['retweet_count']
			vf_w = get_factor(vf, 'verified')
			fc_w = get_factor(fc, 'followers_count')
			rt_w = get_factor(rt, 'retweet')
			popularity_score = vf_w + fc_w + rt_w
			tweet['popularity_score'] = popularity_score

			ts = time.strftime('%Y%m%d', time.strptime(tweet['created_at'],'%a %b %d %H:%M:%S +0000 %Y'))
			tweet['timestamp_ms'] =  ts
			tweet['positive_words'] = getFilteredWords(tweet['text'].split(),positiveList)
			tweet['negative_words'] = getFilteredWords(tweet['text'].split(),negativeList)
			tweetTextBlob = TextBlob(tweet['text'])
			tweet['sentiment'] = tweetTextBlob.sentiment.polarity
		
			print "Locations and Genders Parsed"

			try:
				coll_fix.insert(tweet)
				raw_coll.update({'_id' : tweet['_id']}, {'$set' : { "isNew" : "False" }})
			except Exception as E:
				print str(E)
				continue
		except Exception as E:
			print "Main", str(E)
			continue


def get_factor(value, tag):
		if tag == 'verified':
			if value == False:
				return 1
			else:
				return 5
		elif tag == 'followers_count':
			if value < 50:
				return 1 
			elif value >= 0 and value < 100:
				return 2 
			elif value >= 100 and value < 500:
				return 3 
			elif value >= 500 and value < 1000:
				return 4
			elif value >= 1000 and value < 3000:
				return 6
			elif value >= 3000 and value < 5000:
				return 8
			elif value >= 5000 and value < 10000:
				return 12
			elif value >= 10000 and value < 20000:
				return 15
			else:
				return 18
		else:
			if value < 1:
				return 0
			if value >= 1 and value <= 5:
				return 2 
			elif value >= 5 and value < 10:
				return 3 
			elif value >= 10 and value < 25:
				return 4
			elif value >= 25 and value < 50:
				return 5 
			else:
				return 6


def getFilteredWords(wordlist, filterList):
	filteredWords = []
	for token in wordlist:
		if token.lower() in filterList.keys():
			filteredWords.append(token)
	return filteredWords

def getTextFileAsDict(pathOfTextFile):
	listData = open(pathOfTextFile).read().split("\r\n")
	dictData = {}
	for each in listData:
		dictData[each] = ''
	return dictData

# @celery.task
def processer(mname):
	rawids = db[mname + "_RawTweets"].find({}, {'_id':1})
	parsedids = db[mname + "_ParsedTweets"].find({}, {'_id':1})
	rawidlist = [x['_id'] for x in rawids]
	parsedidlist = [x['_id'] for x in parsedids] 
	
	json_movie_list = []
	for raw in rawidslist:
		if raw not in parsedidlist:
			json_var = db[mname + "_RawTweets"].find_one({'_id' : raw})
			json_movie_list.append(json_var)
	add_tweet_parameters(json_movie_list, mname)



def AddProcess(jlist, moviename):
	master_list = [([x],moviename) for x in jlist]
	p = MyPool(20)
	p.daemon = False
	p.map(add_tweet_parameters, master_list)
	p.close()