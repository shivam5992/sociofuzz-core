import json
import twython
import TwitterUtility
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from datetime import datetime, timedelta

class TwitterTimeline:
	def __init__(self, handle,authKeyPath='twitterKeys.csv',dbName = 'testDB',
		collectionName='collTest', serverAddress='localhost', portAddress = 27017, update = False):
		self.extract_timline(handle,authKeyPath,serverAddress,portAddress,dbName,collectionName, update)

	def extract_timline(self, handle,authKeyPath,serverAddress,portAddress,dbName,collectionName, update):
		authKeys = TwitterUtility.getAuthKeysFromCSV(authKeyPath)
		authKeysCycle = TwitterUtility.cycle(authKeys)
		client = MongoClient(serverAddress,portAddress)
		db = client[dbName]
		collection = db[collectionName]

		notInitialized = True
		authKey = authKeysCycle.next()
		keycount = 0
		max_id = None
		breakFlag = False
		while True:
			try:
				twitter = twython.Twython(authKey[0], authKey[1], authKey[2], authKey[3])
				for count in range(1, 20):
					count = count * 200
					if update == False:
						user_timeline = twitter.get_user_timeline(screen_name = handle, count = count, include_rts=1, 
							exclude_replies = False, max_id = max_id)
					else:
						today = datetime.now()- timedelta(hours=48)
						twodaysback = str(today).split()[0]
						user_timeline = twitter.get_user_timeline(screen_name = handle, count = count,since = twodaysback , include_rts=1, 
							exclude_replies = False, max_id = max_id)
					jsoned = json.loads(json.dumps(user_timeline))
					for i, each in enumerate(jsoned):
						each['_id'] = each.pop('id')
						each['isNew'] = "True"
						try:
							collection.insert(each)
							print "Adding tweet with Id : " + str(each['_id'])
						except DuplicateKeyError:
							print "Tweet already present"
							breakFlag = True
							break 
					max_id = each['id_str']
					if breakFlag == True:
						break
				if breakFlag == True:
					break
			except:
				print "Changing Key"
				authKey = authKeysCycle.next()
				keycount += 1
				if keycount == 3:
					break