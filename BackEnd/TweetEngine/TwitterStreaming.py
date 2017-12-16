from twython import TwythonStreamer
import TwitterUtility
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import time
import json
from datetime import datetime
import time

class TwitterStreamAccumulator(TwythonStreamer):

    def __init__(self, app_key=None, app_secret=None, oauth_token=None, oauth_token_secret=None,serverAddress='localhost',portAddress=27017,dbName='dbTest',collectionName='collTest',filePath='tweetsBackup.txt'):
        TwythonStreamer.__init__(self,app_key,app_secret,oauth_token,oauth_token_secret)
        self.dbName = dbName
        self.collectionName = collectionName
        self.serverAddress = serverAddress
        self.portAddress = portAddress
        client = MongoClient(self.serverAddress,self.portAddress)
        self.db = client[self.dbName]
        self.collection = self.db[self.collectionName]

    def on_success(self, tweet):
        if 'text' in tweet:
            tweet['_id'] = tweet.pop('id')
            try:
                self.collection.insert(tweet)
                print str(tweet['_id'])
            except DuplicateKeyError:
                print "Presente" + str(tweet['_id'])
    def on_error(self, status_code, data):
        print "Error : " + str(status_code)
        raise Exception


class TwitterStream(object):
    """Used for Streaming the Twitter and Storing it in Text File and MongoDB"""
    def __init__(self, searchQuery, authKeyPath='twitterKeys.csv',serverAddress='localhost',portAddress=27017,dbName='dbTest',collectionName='collTest'):
        authKeys = TwitterUtility.getAuthKeysFromCSV(authKeyPath)
        authKeysCycle = TwitterUtility.cycle(authKeys)
        authKey = authKeysCycle.next()
        while True:
            try:
                print authKey[0]
                tw = TwitterStreamAccumulator(app_key=authKey[0],app_secret=authKey[1],oauth_token=authKey[2],oauth_token_secret=authKey[3],serverAddress=serverAddress,portAddress=portAddress,dbName=dbName,collectionName=collectionName)
                tw.statuses.filter(track=searchQuery)
            except Exception,e:
                time.sleep(3)
                authKey = authKeysCycle.next()
                exceptionData = "Exception :" + str(e)
                print "Got an exception over here -- " + exceptionData + " -- Changing the key"          
            