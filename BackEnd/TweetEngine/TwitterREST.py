import json
import twython
import TwitterUtility
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from datetime import datetime, timedelta


class TwitterREST:

	def __init__(self,searchQuery,authKeyPath,serverAddress,portAddress,dbName,collectionName, update):
		self.storeTweets(searchQuery,authKeyPath,serverAddress,portAddress,dbName,collectionName, update)

	def storeTweets(self,searchQuery,authKeyPath,serverAddress,portAddress,dbName,collectionName, update):
		authKeys = TwitterUtility.getAuthKeysFromCSV(authKeyPath)
		authKeysCycle = TwitterUtility.cycle(authKeys)
		client = MongoClient(serverAddress,portAddress)
		db = client[dbName]
		collection = db[collectionName]

		notInitialized = True
		authKey = authKeysCycle.next()
		print "Using key " + str(authKey[3])
		while True:
			try:
				twitter = twython.Twython(authKey[0], authKey[1], authKey[2], authKey[3])

				if notInitialized:
					if update == False:
						results = twitter.search(q=searchQuery,include_entities='true',count='100',lang='en')
					else:
						today = datetime.now()- timedelta(hours=48)
						twodaysback = str(today).split()[0] 
						results = twitter.search(q=searchQuery, since = twodaysback, include_entities='true',count='100',lang='en')
					notInitialized=False
				else:
					next_results_url_params = results['search_metadata']['next_results']
					next_max_id = next_results_url_params.split('max_id=')[1].split('&')[0]
					results = twitter.search(q=searchQuery,include_entities='true',max_id=next_max_id,count='100',language='en')
			except Exception as e:
				print e
				if 'next_results' in str(e):
					print "123"
					break
				else:
					authKey = authKeysCycle.next()
					print "Moving to next key in Auth Keys"
					continue
				

			for tweet in results['statuses']:
				tweet['_id'] = tweet.pop('id')
				if update == True:
					tweet['isNew'] = "True"
				try:
					collection.insert(tweet)
					print "Processed Tweet" + str(tweet["_id"])
				except DuplicateKeyError:
					print "Tweet already present"