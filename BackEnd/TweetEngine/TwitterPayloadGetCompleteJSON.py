import twython
import json
import TwitterUtility
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

class TwitterPayloadGetCompleteJSON:

	def __init__(self, authKeyPath, serverAddress, portAddress, dbNameSource, collectionNameSource, initialStart, dbNameDestination, collectionNameDestination):
		self.getTweetsJSONAndStore(authKeyPath, serverAddress, portAddress, dbNameSource, collectionNameSource, initialStart, dbNameDestination, collectionNameDestination)

	def getTweetsJSONAndStore(self, authKeyPath, serverAddress, portAddress, dbNameSource, collectionNameSource, initialStart, dbNameDestination, collectionNameDestination):
		authKeys = TwitterUtility.getAuthKeysFromCSV(authKeyPath)
		authKeysCycle = TwitterUtility.cycle(authKeys)

		client = MongoClient(serverAddress,portAddress)

		sourceDB = client[dbNameSource]
		sourceCollection = sourceDB[collectionNameSource]

		destDB = client[dbNameDestination]
		destCollection = destDB[collectionNameDestination]

		counterCollection = sourceDB['counterCollection']

		counterCollection.find_one_and_update({'_id':'JSONTweetCounter'},{'$set': {'value': initialStart}},upsert=True)

		authKey = authKeysCycle.next()
		print "Using key " + str(authKey)

		tweetIDs = [x['_id'] for x in sourceCollection.find(projection={'_id':1},skip=initialStart)]
		print tweetIDs
		for tweetIDChunks in (list(self.chunks(tweetIDs, 100))):
			tweetCountChunks = len(tweetIDChunks)

			while True:
				try:
					twitter = twython.Twython(authKey[0], authKey[1], authKey[2], authKey[3])
					tweets = twitter.lookup_status(id = tweetIDChunks)
				except Exception as e:
					print "In Exception"
					authKey = authKeysCycle.next()
					print "Moving to next key in Auth Keys"
					continue

				

				for tweet in tweets:
					tweet['_id'] = tweet.pop('id')
					try:
						print "Inserting into it"
						destCollection.insert_one(tweet)
						print "Adding tweet with Id : " + str(tweet['_id'])
					except DuplicateKeyError:
						print "Tweet already present" + str(tweet['_id'])

				counterCollection.find_one_and_update({'_id': 'JSONTweetCounter'}, {'$inc': {'value': tweetCountChunks}})
				break

	def chunks(self,l, n):
	    for i in xrange(0, len(l), n):
	        yield l[i:i+n]
