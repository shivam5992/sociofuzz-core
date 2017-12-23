from pymongo import MongoClient, ASCENDING, DESCENDING
import json, csv
from operator import itemgetter
import math
import gridfs
from textblob import TextBlob
from Levenshtein import ratio

serveraddress = 'localhost'
serveraddress1 = '130.211.189.17'
client = MongoClient(serveraddress, 27017)
db = client['MovieMasterTweets']
client1 = MongoClient(serveraddress1, 27017)
db1 = client1['MovieMasterTweets']
fs = gridfs.GridFS(db)

MJCollection = db['MovieJson']
BoxCollection = db['BoxOfficeDetails']

# for x in db1.collection_names():
# 	if "Pop" in x:
# 		print db[x].find_one().keys()
# 		print db1[x].update({'_id' : x['_id']},{ '$set' : {'dataType': 'tweet' }} ) 

# exit(0)

class AddData:
	def __init__(self):
		return None

	def add_json_to_collection(self, json, collection_name):
		collection = db[collection_name]
		collection.insert(json)
		print "Inserted"

	def add_movie_meta_data(self, mnames):
		collection = db.moviemeta
		collection1 = db1.moviemeta

		metadata_list = []
		with open('vocab/MetaData.csv', 'rU') as metadata:
			reader = csv.reader(metadata)
			for i, row in enumerate(reader):
				meta = {}
				if i == 0:
					header = row
				else:
					metadata_list.append(row)

		for each in metadata_list:
			# print each
			for movie_id in mnames:
				if each[1] == movie_id:
					meta = {}
					for j, data in enumerate(each):
						meta[header[j]] = each[j]
						meta['_id'] = each[1]
					print each[1]
					collection.remove({'_id' : movie_id})
					collection1.remove({'_id' : movie_id})
					collection.insert(meta)
					collection1.insert(meta)

	def add_image(self, elem, moviename):
		collection = db['movie_jsons']
		collection.update({'_id' : moviename}, {'$addToSet': {'imgelem': elem }})
		print "updated"	

	def InsertBlog(self, blog):
		db['MovieBlog'].insert(blog)
		print "Inserted"

	def PushToInstance(self, moviename, get , isTrend = False):
		client1 = MongoClient(serveraddress1, 27017)
		db1 = client1['MovieMasterTweets']

		if isTrend == True:
			doc = get.get_latest_movie_json(moviename, getNews = False, isTrend = True)
			db1['trend_jsons'].update({'_id':moviename}, doc, True)

			# IMP Every Time
			p , n = get.get_sentiment_tweets_api(moviename + '_ParsedTweets', 9)
			pop = get.get_popular_tweets(moviename + "_ParsedTweets", 18)
			doc = {'pos' : p + n , 'neg' : n,  'pop' : pop}
			print doc 
			db1[moviename + '_ParsedPopTweets'].drop()  
			db1[moviename + '_ParsedPopTweets'].insert(doc)

		else:
			doc = db['movie_jsons_1'].find_one({'_id' : moviename})
			db1['movie_jsons_1'].update({'_id':moviename}, doc, True)
		
			# IMP Every Time
			doc = db[moviename + "_ParsedPopTweets"].find({'dataType' : 'tweet'})
			db1[moviename + '_ParsedPopTweets'].remove({'dataType' : 'tweet'})
			db1[moviename + '_ParsedPopTweets'].insert(doc)
			
			db1[moviename + '_ParsedPopTweets'].remove({'dataType' : 'socialImage'})  
			for doc in db[moviename + "_ParsedPopTweets"].find({'dataType' : 'socialImage'}):
				db1[moviename + '_ParsedPopTweets'].insert(doc)
			
			# Not Required as you are already sending movie json to the instance
			# a, b, c = get.getImagesFromGrid(moviename)
			# db1.movie_jsons.update({ '_id' : moviename }, 
				# {'$set': {'wikiimg': [a], 'buffimg' : [b] }})
			# db1.movie_jsons.update({'_id' : moviename}, 
			# {'$set' : { 'actsimg' : c }}
			# )

	def AddTrailer(self, name, link, date):
		doc = {
			'type' : 'trailer',
			'url' : link, 
			'date' : date ,
			'name' : name
		}
		db['HomeContent'].insert(doc)
		db1['HomeContent'].insert(doc)
	





class GetData:
	def __init__(self):
		return None

	### NEW
	def getPercent(self, rank):	
		srtd = sorted([x['rank'] for x in db['movie_jsons'].find({}, {'rank'})])
		percent = srtd.index(rank)
		percent = int(float(percent)/len(srtd) * 100)
		return percent


	def getBlogPost(self, postlink):
		post = db['MovieBlog'].find_one({'link' : postlink})
		return post

	def getAllBlogs(self):
		pipeline = [{'$sort' : {'blogid': -1}},
					{'$group' : {'_id' : 'blogid', 'data'  : 
					{ '$push' : { 'title'  : '$title' ,'PostedOn' : '$PostedOn' ,
					'Desc' : '$Desc' , 'link' : '$link' }}  }}]
		posts = db['MovieBlog'].aggregate(pipeline)
		postsAll = posts['result'][0]['data']
		return postsAll

	def get_latest_movie_json(self, moviename, getNews = False, isTrend = False):
		if isTrend == True:
			collection = db['trend_jsons']
			data = collection.find( { '_id' : moviename } )
			return data[0] 
		else:
			collection = db['movie_jsons']
			if getNews == False:
				data = collection.find({ "_id" : moviename }, {'news_data' : 0})
			else:
				data = collection.find({ "_id" : moviename })
			return data[0]

	def get_movie_names(self):
		collection = db['moviemeta']
		data = collection.find({}, {'Movie Name' : 1, '_id' : 0})
		return data

	def get_next_news(self, moviename):
		collection = db['movie_jsons']
		data = collection.find_one({"_id" : moviename}, {'news_data' : 1})['news_data']
		data = sorted(data, key=itemgetter('count'), reverse = True) 
		return data

	def get_next_reviews(self, moviename):
		collection = db['movie_jsons_1']
		data = collection.find_one({"_id" : moviename}, {'reviews_data' : 1})['reviews_data']
		try:
			data = sorted(data, key=itemgetter('rating'), reverse = True) 
		except:
			data = sorted(data, key=itemgetter('count'), reverse = True)
		return data

	def get_upcoming_movies(self, count):
		collection = db['movie_jsons']
		pipeline = [ { '$sort' : { 'MovieId' : -1}}	,
					 { '$limit' : count },
					 {"$group": {"_id": "$movie.name", "projection" : { "$push": 
					 { 'trailer':"$meta.buff.gallery", 
					   'tweetcount' : '$analyzed.total_tweets' , 
					   'MovieId':'$MovieId', 
					   'rank':'$rank',
					   'uname':'$name', 
					   'wikiimg' : '$wikiimg',
					   'buffimg' : '$buffimg',
					   'stars' : '$stars', 
					   'poster' : '$meta.wiki.poster', 
					   'name' : '$meta.wiki.name', 
					   'date' : '$meta.wiki.Release dates' }}}}
					]
		data = collection.aggregate(pipeline)
		return data['result']

	def get_top_movies(self, count):
		collection = db['movie_jsons']
		pipeline = [ { '$sort' : { 'rank' : -1}}	,
					 { '$limit' : count },
					 {"$group": {"_id": "$movie.name", "projection" : { "$push": { 
					 'trailer':"$meta.buff.gallery" ,'tweetcount' : '$analyzed.total_tweets' , 
					 'MovieId':'$MovieId', 'rank':'$rank','uname':'$name', 'stars' : '$stars',
					  'poster' : '$meta.wiki.poster', 'name' : '$meta.wiki.name',
					  'wikiimg' : '$wikiimg',
					  'buffimg' : '$buffimg', 
					  'date' : '$meta.wiki.Release dates' }}}}
					]
		data = collection.aggregate(pipeline)
		return data['result']

	def get_allmovies_movies(self):
		collection = db['movie_jsons']
		pipeline = [ { '$sort' : { 'MovieId' : -1}}	,
					 {"$group": {"_id": "$movie.name", "projection" : { "$push": { 'trailer':"$meta.buff.gallery" , 
					 'tweetcount' : '$analyzed.total_tweets' , 'MovieId':'$MovieId', 'rank':'$rank','uname':'$name', 
					 'stars' : '$stars', 'wikiimg' : '$wikiimg', 'buffimg' : '$buffimg' , 'poster' : '$meta.wiki.poster', 'posterAlternate' : '$meta.buff.gallery', 'name' : '$meta.wiki.name', 
					 'date' : '$meta.wiki.Release dates' }}}}
					]
		data = collection.aggregate(pipeline)
		data = [x for x in data['result']]
		return data

	def get_allmovies_mobile_movies(self):
		collection = db['movie_jsons']
		pipeline = [ { '$sort' : { 'MovieId' : -1}}	,
					 {"$group": {"_id": "$movie.name", "projection" : { "$push": {  
					 'tweetcount' : '$analyzed.total_tweets' , 'MovieId':'$MovieId', 'rank':'$rank','uname':'$name', 
					  'name' : '$meta.wiki.name', 
					  }}}}
					]
		data = collection.aggregate(pipeline)['result'][0]['projection']
		return data

	def get_jsons_collection(self, collection_name):
		collection = db[collection_name].find()
		return collection

	def check_doc_exist(self, key, value, collection_name):
		status = db[collection_name].find_one({ key : value })
		return status

	def get_value(self, key, collection_name):
		data = db[collection_name].find_one( { 'key' : key })
		if data:
			return data['value']
		else:
			return None

	def get_all_collections(self):
		coll_names = db.collection_names()
		return coll_names

	def get_sentiment_tweets_api(self, collectionname, limit):
		pipeline = [{"$group": {"_id": "all", "mincount":{"$min":"$sentiment"},"maxcount":{"$max":"$sentiment"}}}]
		avgs = db[collectionname].aggregate(pipeline)
		ac = 0
		for x in avgs['result']:
			if x['mincount'] == -1:
				ac = 0 
			else:
				ac = 0.5

		pipelinePos = [ 
			 {'$match':{"sentiment" : { '$gt': ac }}  },
			 { '$match' : { 'user.country' : 'India' }}, 
			 {'$match':{'negative_words' : {'$size' : 0} }},
			 { '$group' : {'_id': '$positive_words'  ,'tweets1' : {'$first':{'popularity_score':'$popularity_score','_id':'$_id','sentiment':'$sentiment','text':'$text' ,'retweet_count':'$retweet_count','created_at':'$created_at','favorite_count':'$favorite_count','user':'$user','companys':'$companys','dimensions':'$dimensions','retweeted':'$retweeted','negative_words':'$negative_words','positive_words':'$positive_words','clean_text':'$clean_text','retweeted':'$retweeted'}}}},
			 { '$sort' : { 'tweets1.sentiment' : -1}},    
			{ '$limit' : limit }			 
		]
		documentsPos = db[collectionname].aggregate(pipelinePos)
		pos = []
		for pp in documentsPos['result']:
			pos.append(pp['tweets1'])

		pipelineNeg = [ 
			 {'$match': {"sentiment" : { '$lt': ac }}  },
			 { '$match' : { 'user.country' : 'India' }},
			 {'$match':{'positive_words' : {'$size' : 0} }},
			 { '$group' : {'_id': '$negative_words'  ,'tweets1' : {'$first':{'popularity_score':'$popularity_score','_id':'$_id','sentiment':'$sentiment', 'eurl' : '$entities.urls.expanded_url', 'text':'$text' ,'retweet_count':'$retweet_count','created_at':'$created_at','favorite_count':'$favorite_count','user':'$user','companys':'$companys','dimensions':'$dimensions','retweeted':'$retweeted','negative_words':'$negative_words','positive_words':'$positive_words','clean_text':'$clean_text','retweeted':'$retweeted'}}}},
			 { '$sort' : { 'tweets1.sentiment' : 1}},    
			 # { '$sort' : { 'tweets1.popularity_score' : -1}},    
			 { '$limit' : limit }			 
		]
		documentsNeg = db[collectionname].aggregate(pipelineNeg)

		neg = []
		for pp in documentsNeg['result']:
			neg.append(pp['tweets1'])
		return pos, neg

	def get_popular_tweets(self, collectionname, limit):
		pipeline = [ { '$sort' : { 'popularity_score' : 1}},
					 { '$match' : { 'user.country' : 'India' }},
					 { '$group' : {'_id': { 'userid':'$user.id' },\
					 'tweets1' : {'$first':{'popularity_score':'$popularity_score',\
					 '_id':'$_id','lang' : '$lang', 'sentiment':'$sentiment','text':'$text'\
					  ,'retweet_count':'$retweet_count','created_at':'$created_at',\
					  'favorite_count':'$favorite_count','user':'$user','companys':'$companys',\
					  'dimensions':'$dimensions','retweeted':'$retweeted','negative_words':'$negative_words',\
					  'positive_words':'$positive_words','clean_text':'$clean_text','retweeted':'$retweeted'}}}}
					 ]

		documents = db[collectionname].aggregate(pipeline, allowDiskUse=True)
		pop = []
		count = 0

		for x in documents['result']:
			pop.append(x['tweets1'])
			count += 1
			if count == limit:
				break
		return pop

	def get_collection_count(self, collection_name):
		collection = db[collection_name]
		return collection.count()

	def get_new_tweets(self, collection_name):
		return db[collection_name].find_one({'dataType' : 'tweet'})


	def get_sentiment_count(self, collection_name):
		collection = db[collection_name]

		pipeline = [{"$group": {"_id": "all", "mincount":{"$min":"$sentiment"},"maxcount":{"$max":"$sentiment"}}}]
		avgs = collection.aggregate(pipeline)
		ac = 0
		Flag = False
		for x in avgs['result']:
			if x['mincount'] == -1:
				ac = 0 
			else:
				ac = 0.5
		try:
			pipelineNeg = [ 
				 {'$match': {"sentiment" : { '$lt': ac+0.2 }}  },
				 {'$match': { 'user.country' : 'India' }},
				 {'$match': {'positive_words' : {'$size' : 0} }},
			]
			documentsNeg = collection.aggregate(pipelineNeg)
			negative = len(documentsNeg['result'])
		except:
			Flag = True

		
		try:
			pipelinePos = [ 
				 {'$match': {"sentiment" : { '$gt': ac+0.2 }}  },
				 {'$match': { 'user.country' : 'India' }},
				 {'$match': {'negative_words' : {'$size' : 0} }},
	 		]
			documentsPos = collection.aggregate(pipelinePos)
			positive = len(documentsPos['result'])
		except:
			Flag = True

		try:
			pipelineNeut = [ 
				 {'$match': { 'user.country' : 'India' }},
				 {'$match': {'negative_words' : {'$size' : 0} }},
				 {'$match': {'positive_words' : {'$size' : 0} }},
			]
			documentsNeu = collection.aggregate(pipelineNeut)
			neutral = len(documentsNeu['result'])
		except:
			Flag = True

		if Flag == True:
			pipelineNeg = {'sentiment' : {'$lt' : 0.2 + ac}, 'user.country' : 'India'} 
			negative = collection.find(pipelineNeg).count()
			
			pipelinePos = {'sentiment' : {'$gt' : 0.2 + ac}, 'user.country' : 'India'} 
			positive = collection.find(pipelinePos).count()

			pipelineNeut = {'sentiment' : {'$lt' : ac + 0.2, '$gt'  : ac - 0.2 }, 'user.country' : 'India'} 
			neutral = collection.find(pipelineNeut).count()			


		total = neutral + positive + negative


		try:
			ppercent = int(math.floor((float(positive)/total)*100))
			npercent = int(math.ceil((float(negative)/total)*100))
			nupercent = int(math.ceil((float(neutral)/total)*100))
		except:
			ppercent = 25
			npercent = 25
			nupercent = 20

		total_sent = {
			"positive_count" : positive,
			"negative_count" : negative,
			"neutral_count" : neutral,
			"total_count" : total,
			"positive" : ppercent,
			"negative" : npercent,
			"neutral" : nupercent
		}
		return total_sent

	def get_gender_count(self, collection_name):
		collection = db[collection_name]
		gender = collection.find({}, { "user.gender" :1,"_id":0})
		return gender

	def get_theme_rating(self, moviename, searchValues):
		mains = {}
		allt = 0
		for val in searchValues:
			terms = val.split(",")
			trmcount = 0
			for term in terms:
				documents = db[moviename + '_ParsedTweets'].find({"$text":{"$search":term}})
				trmcount += documents.count()
			mains[terms[0]] = 1 + trmcount
			allt += trmcount + 5
		tains = {}
		for x in mains:
			tains[x] = {}
			tains[x]['val'] = int(math.ceil(round(float(mains[x])/allt * 100, 1))) 
			tains[x]['tweets'] = mains[x] + 5
		return tains

	def get_user_details(self, collection_name, limit):
		collection = db[collection_name]
		data = collection.find({}, { "user.name" :1, 
			"user.id_str" : 1, 
			"user.followers_count":1, 
			"user.screen_name":1,  
			"user.profile_image_url":1, 
			"_id":0}).limit(limit)
		return data

	def get_timestamp_count(self, collection_name):
		collection = db[collection_name]
		timestamp = collection.find({}, { "created_at" :1,"_id":0})
		timestamp = [x['created_at'] for x in timestamp]
		return timestamp

	def get_country_count(self, collection_name):
		collection = db[collection_name]
		country = collection.find({}, { "user.country" :1,"_id":0})
		country = [x['user']['country'] for x in country]
		return country

	def get_influence_data(self, collection_name):
		collection = db[collection_name]
		data = collection.find({}, { 'retweet_count':1,
			'favorite_count':1, 
			"user.id" : 1, "user.followers_count":1, 
			"user.screen_name":1, "user.name" : 1, 
			"user.profile_image_url":1, "_id":0})
		return data

	def get_location_count(self, collection_name):
		collection = db[collection_name]
		country = collection.find({}, { "user.location" :1,"_id":0})
		return country

	def get_tweet_texts(self, collection_name, limit):
		collection = db[collection_name]
		texts = collection.find({}, { "text" :1,"_id":0}).limit(limit)
		return texts

	def get_user_reach(self, collection_name):
		collection = db[collection_name]
		texts = collection.find({}, { "user.id" :1,"user.followers_count" :1,"_id":0})
		return texts

	def get_medias(self, collection_name):
		collection = db[collection_name]
		media = collection.find({}, { "entities.media" :1,"_id":0})
		return collection.distinct('entities.media.media_url')
	
	def get_media_api(self, moviename):
		coll = self.get_latest_movie_json(moviename)
		media_data = coll['imgelem']
		return media_data

	def get_hashtag_count(self, collection_name):
		collection = db[collection_name]
		hashtag = collection.find({}, {"entities.hashtags.text" :1,"_id":0})
		return hashtag

	def get_mention_count(self, collection_name):
		collection = db[collection_name]
		ment = collection.find({}, {"entities.user_mentions.screen_name" :1,"entities.user_mentions.name" :1,"_id":0})
		return ment 

	def get_url_count(self, collection_name):
		collection = db[collection_name]
		hashtag = collection.find({}, {"entities.urls.expanded_url" :1, 'text':1, "_id":0})
		return hashtag

	def get_users_api(self, moviename, limit=39):
		collection = self.get_latest_movie_json(moviename)['analyzed']['user_details']
		line = ""
		count = 1 
		for x in collection:
			line += """
			<span class='images-collage-tag'> \
        		<object data=""" + x['lnk'] + """ type='image/jpg'>
        		<img src="" > \
            	</object></span>"""
			count += 1
			if count == limit:
				break
		return line

	def get_infulencer_api(self, moviename, limit=5):
		collection = self.get_latest_movie_json(moviename)['analyzed']['logscore'][:limit]
		line = ""
		for inf in collection:
			line += "<div class='row influencer-row'> \
          <div class='col-md-6 col-sm-6 col-xs-6 inf-name'> \
            <img src=" + inf['img'] + " class='influencer-img'> \
            <div class='img-class'> \
              <div class='inf-name-text'>" + inf['name'] + "</div> \
              <div class='inf-name-handle'>@"+ inf['sname'] + "</div> \
            </div> \
          </div> \
          <div class='col-md-3 col-sm-3 col-xs-3 inf-follower'>" + str(inf['fc']) + "</div> \
          <div class='col-md-3 col-sm-3 col-xs-3 inf-follower'>" + str(round(inf['log'], 2)) +"</div> \
        </div>"
		return line

    #Get sentiment information of tweets which are retweeted more than 30
	def getReTweetedCount(self, collection_name):
		collection = db[collection_name]
		retweet_count = collection.find({ "retweet_count" : { '$gte': 5 }}).count()
		return retweet_count

    # Get number of tweets which are posted by verified users
	def getVerifiedCount(self,collection_name):
		collection = db[collection_name]
		verified_count = collection.find({'user.verified_status' : True}).count()
		return verified_count


	def getFavouriteCount(self, collection_name):
		collection = db[collection_name]
		favourite_count = collection.find({"favourite_count" : {'$gte' : 1}}).count()
		return favourite_count

	def get_indian_cities(self):
		collection = db['indian_cities']
		data = collection.distinct('_id')
		return data
	

	def getUniqueDetailsFromDoc(self, groupKey, projectionFields, collectionName):
		collection = db[collectionName]
		pipeline = [ {'$match' : {'user.country' : 'India'}}, { "$group"     : { "_id": "$" + groupKey, 
						"projection" : { "$first" : "$"+projectionFields },  
						}  }, { '$sort' : { 'projection.followers_count' : -1}}]
		documents = collection.aggregate(pipeline)
		return documents

	def getTotalCountOfKey(self, keyName, collection_name):
		collection = db[collection_name]
		pipeline = [{"$group": {"_id": "all", "totalCount":{"$sum":"$"+keyName}}}]
		documents = collection.aggregate(pipeline)
		return [x for x in documents['result']]

	def getInfluencerData(self, collection_name):
		collection = db[collection_name]
		pipeline = [{'$group':{"_id":"$user.id",
					'rc': {"$sum":"$retweet_count"},
					'fc': {"$first":"$user.followers_count"},
					'img': {"$first":"$user.profile_image_url_https"},
					'name': {"$first":"$user.name"},
					'sname': {"$first":"$user.screen_name"},
					}}]
		documents = collection.aggregate(pipeline)
		documents1 = []
		for x in documents['result']:
			x['log'] = math.log((1+x['fc'])*(1+x['rc'])) 
			documents1.append(x)
		return documents1

	def get_medias_hashed(self, moviename):
		col = self.get_latest_movie_json(moviename)
		return col['imgelem']

	def getImagesFromGrid(self, moviename):
		try:
			img = fs.get_last_version(_id = moviename + '_wiki').read().encode('base64')
		except:
			img = None 

		try:	
			img1 = fs.get_last_version(_id = moviename + '_buff').read().encode('base64')
		except:
			img1 = None 

		traffic = False
		try:
			anal = self.get_latest_movie_json(moviename)['meta']['wiki']['Starring'].split(",")
			acts = {}
			for x in anal:
				if len(x.strip()) < 2:
					continue
				nam = x.strip().replace(".","").replace("_(actor)", "").strip()
				try:
					nam = nam.replace(" ","_").replace("[1]", "").replace("[2]", "").strip()
					acts[nam] = fs.get_last_version(_id = nam).read().encode('base64')
				except Exception as E:
					traffic = True
				
				if traffic == True:
					try:
						nam = nam.replace(" ","_").replace("[1]", "").replace("[2]", "").replace("_(actor)", "").strip()
						acts[nam] = db['actorSupport'].find_one( {'_id' : nam } )['url']
					except Exception as E:
						print "No Image for", nam
						acts[nam] = "../static/images/null.jpg"

		except Exception as E:
			print E
			acts = {}	
		return img, img1, acts
	

	def get_insights(self, limit):
		complete = []
		upcoming = self.get_upcoming_movies(limit)
		each = upcoming[0]

		for x in each['projection']:
			name = x['uname']
			insights = {}
			
			try:
				mv = self.get_latest_movie_json(name)
				anal = mv['analyzed']
				meta = mv['meta']
				insights['rank'] = mv['rank']
			except Exception as E:
				continue 

			handle = {}
			handle['name'] = anal['mentions'][0][0]
			handle['value'] = anal['mentions'][0][2]
			insights['name'] = x['name']
			insights['handle'] = handle

			for hr in anal['days']:
				if anal['days'][hr]['rad'] == 45:
					thisday = hr
			insights['day'] = (thisday, anal['days'][thisday])


			maxhr = 0
			for hr in anal['hours']:
				if hr['frequency'] > maxhr:
					maxhr = hr['frequency']
					thishr = hr
			insights['hour'] = thishr

			insights['tot_tweets'] = anal['total_tweets']
			insights['hashtag'] = anal['hashtags'][0]
			insights['websites'] = anal['websites'][0]
			if anal['genders']['male'] > anal['genders']['female']:
				insights['genders'] = ('Males', 'Females')
			else:
				insights['genders'] = ('Females', 'Males')

			insights['link'] = anal['links'][0]
			insights['inf'] = (anal['user_details'][0]['projection']['screen_name'], 
							anal['user_details'][0]['projection']['followers_count'])
			complete.append(insights)
		return complete, upcoming
		
	def get_total_insights(self):
		totcol = db['movie_jsons'].find()
		tot_movies = totcol.count()
		rv_cnt = get.getTotalCountOfKey('reviews_count_int', 'movie_jsons')[0]['totalCount']
		cnt1 = get.getTotalCountOfKey('total_tweets_int', 'movie_jsons')[0]['totalCount']
		
		total = {}
		total['parsed'] = format(int(cnt1), ',d')
		total['movies'] = format(int(tot_movies), ',d')
		total['reviews'] = format(int(rv_cnt), ',d')

		return total

	def getSearchElements(self):
		lst = []
		pipeline = [ { '$group' : {'_id': { 'mid':'$_id' }, 'name' : {'$first': {'name':'$meta.wiki.name'}}}}]
		docs = db['movie_jsons'].aggregate(pipeline)
		for x in docs['result']:
			label = x['_id']['mid']
			value = x['name']['name']
			elem = {}
			elem['value'] = label
			elem['label'] = value
			lst.append(elem)
		return lst



	def getAboutGraphData(self):
		pipeline = [{'$group' : {'_id' : '$_id' , 'projection' : {'$push' : 
											{ 'name_id' : '$_id' , 
											  'rank' : '$rank',
											  'stars' : '$stars',
											  'wikiimg' : '$meta.wiki.poster',
											  'name' : '$meta.wiki.name'}}}}]

		x = db['movie_jsons'].aggregate(pipeline)
		links = []
		nodes = []
		doc = { 
					'color': "red",
					'poster': "/static/teaser/logo.png",
					'name': "Sociofuzz",
					'name_id': "/",
					'rank': 6,
					'score': 6,
					'star_keyword': "",
					'stars': ""
					}
		nodes.append(doc)
		colors = ['red', 'green', 'blue', 'orange', 'pink', 'gray']
		j = 0
		for i, mv in enumerate(x['result']):
			try:



				tag = mv['projection'][0]
				if tag['name_id'] == "FourPillarsOfBasement":
					tag['name'] = "Four Pillars Of Basement"


				link = {'source': 0, 'target': i+1 }
				doc = { 
						'color': colors[j],
						'poster': tag['wikiimg'],
						'name': tag['name'],
						'name_id': tag['name_id'],
						'rank': tag['rank'],
						'score': tag['rank'],
						'star_keyword': tag['stars'][1],
						'stars': tag['stars'][0]
						}
				j += 1
				j = j % len(colors)
				links.append(link)
				nodes.append(doc)

			except Exception as E:
				print E, tag['name_id']
				continue
		toJson =  { 'links' : links,
					'nodes' : nodes}
		return toJson


	def ParseSocialImages(self, moviename):
		txts = {}
		cnt = 1

		urls = {}
		for each in db[moviename + "_ParsedTweets"].find({}, {'entities.media' : 1 , 'text' : 1, 'user.name' : 1, 'user.screen_name' : 1}):
			if each['entities']:
				murl = each['entities']['media'][0]['media_url_https']
				if murl not in urls:
					urls[murl] = 1 

					txt = " ".join(each['text'].split())
					txt = " ".join([x for x in txt.split() if not x.startswith("http")]).replace("RT","").strip()
					txt = " ".join([x for x in txt.split() if not x.startswith("[")])
					wrds = txt.split()
					if wrds and wrds[0].endswith(":"):
						wrds = wrds[1:]

					txt = " ".join(wrds).replace('"',"'")
					if txt.startswith("."):
						txt = txt[1:]

					if txt not in txts:
						txts[txt] = 1
						each['ctext'] = txt

						doc = {
							'ctext' : txt, 
							'url' : murl,
							'user' : each['user']['name'],
							'screen_name' : each['user']['screen_name'],
							'text' : each['text'],
							'dataType' : 'socialImage',
							'_id' : murl	
						}
						try:
							db[moviename + "_ParsedPopTweets"].insert(doc)
						except Exception as E:
							pass

class UpdateData:

	def __init__(self):
		return None

	def update_json_to_collection(self, doc, collection):
		db[collection].update({'_id': doc['name']}, doc, True)
		return None

	def IsShowable(self, moviename):
		upcoming = get.get_upcoming_movies(5)
		crrnt = [mv['uname'] for mv in upcoming[0]['projection']]
		if moviename in crrnt:
			return "True" 
		else:
			return "False"

	def update_movie_json(self, moviename, json, isTrend = False):
		if isTrend == True:
			# print moviename
			db['trend_jsons'].update({'_id':moviename}, json, True)
		else:
			db['movie_jsons'].update({'_id':moviename}, json, True)
		print "Inserted"

	def remove_document(self, json, collection_name):
		db[collection_name].remove(json)
		print "removed"	

	def convert_reviews(self, data):
		html_data = ""
		mobile_data = """<div class="review-section row-card">
					"""
		for each in data:
			if 'rating' not in each:
				rate = str("")
			else:
				if each['rating'] < 3:
					col = "#DD0000"
				elif each['rating'] >= 3 and each['rating'] < 5:
					col = "#EEAB00"
				elif each['rating'] >= 5 and each['rating'] < 6:
					col = "#00DD00"
				else:
					col = "#499914"
				rate = """<p data-toggle="tooltip" 
							title=' """ + str(each['tot']) + """ words, """ + str(len(each['pos'])) + """ positive and """ +  str(len(each['neg'])) + """ negative.'
							class="review-rate" 
							style="background-color:""" + col + """; color:white">
						""" + str(each['rating']) + """</p>""" 
			if each['desc_text'] == "":
				desc_text = ""
			else:
				if any(wrd in each['link'] for wrd in ['music', 'album', 'sound']):
					continue

				desc_text = each['desc_text'] + " ... "
			html_data += """
					<div class="review-section row-card">
					<div class="row">
						<div class="col-md-1 review-image">
                   	 		<img src=""" + each['newSrc'] + """>
                    	</div>
                    	<div class="col-md-8 review-txt">
                    		<p class="rsource-n">""" + each['name'].strip() + """</p>
                    		<p class="rsource"-s>""" + each['source'].strip() + """</p>  
                    	</div>
                    	<div class="col-md-2">
                    		""" + rate + """
                    	</div>
                    	<div class="col-md-12 rtext">
                    		""" + desc_text + """<a href=""" + each['link'] + """>Read Complete</a>
                    	</div>
                  	</div>
                  	</div>
                  	"""
			mobile_data += """
						<div class="row">
						<div class="col-md-1 col-xs-2 col-sm-2 review-image">
                   	 		<img src=""" + each['newSrc'] + """>
                    	</div>
                    	<div class="col-md-8 col-xs-6 col-sm-6 review-txt">
                    		<a href=""" + each['link'] + """><p class="rsource-n">""" + each['name'].strip() + """</p></a>
                    		<p class="rsource"-s>""" + each['source'].strip() + """</p>  
                    	</div>
                    	<div class="col-md-2 col-xs-2 col-sm-2">
                    		""" + rate + """
                    	</div>
                  		</div>
                  	"""
		mobile_data += """ 
                  	</div>"""
		return html_data, mobile_data

	def convert_news(self, data):
		html_data = ""
		mobile_data = "<div class='news-section-one'>"
		for each in data:
			
			if len(each['source']) < 3:
				each['source'] = ""
			
			if each['date'][0] == "":
				each['date'][0] = ""
			if each['date'][1] == "":
				each['date'][1] = ""

			if type(each['title']) == list:
				ttle = each['title'][0]
			else:
				ttle = each['title']

			if each['desc_text'] == "":
				desc_text = ""
			else:
				desc_text = each['desc_text'] + " ... "

			html_data += """<div class='news-section-one'> 
			<div class="news-heading">
			<span class='rsource-n'>""" + ttle + """</span>
			</div>
			<div class="news-summary">
			<p>""" +  desc_text  + """<a href=""" + each['link'] + """>Read Complete</a></p>
			</div>
			
			</div>"""

			mobile_data += """ 
			<div class="news-heading">
			<span class='rsource-n'><a href=""" + each['link'] + """>""" + ttle + """</a></span>
			</div>
			"""
		mobile_data += "</div>"

		return html_data, mobile_data

	def parse_sect_tweet(self, data, flag, sentflag):
		complete = "<div class='row-card'>"
		for tweet in data:
			if sentflag == 'p':
				sent = """<span class="senti-tweet"><i class="fa fa-smile-o"></i>""" + str(round(tweet['sentiment'],2)) +"""</span>"""
			elif sentflag == 'n':
				sent = """<span class="senti-tweet-n"><i class="fa fa-frown-o"></i>""" + str(round(tweet['sentiment'],2)) +"""</span>"""
			else:
				sent = ""

			complete += """
                  <div class="tweet-box-content">
                   <div class="tweet-box-top">
                    <div class="tweet-box-detail">
                      <div class="tweet-box-name">""" + tweet['user']['name'] + """</div>
                      <div class="tweet-box-handle">@""" + tweet['user']['screen_name'] + """</div>
                      <div class="tweet-box-date">
                        """ + tweet['created_at'].split()[1] + """ 
                        """ + tweet['created_at'].split()[2] + """,
                        """ + tweet['created_at'].split()[-1] + """
                      </div>
                    </div>
                  </div>
                  <div class="tweet-box-bottom">
                    <div class="tweet-box-text""" + flag  +  """ ">
                      """ + tweet['text'] + """
                    </div>
                    <div class="tweet-box-icons">
                      <span><i class="fa fa-retweet"></i>""" + str(tweet['retweet_count']) +"""</span>
                      <span><i class="fa fa-star"></i>""" + str(tweet['favorite_count']) +"""</span>""" + sent + """
                    </div>
                  </div>
                </div>
              """
		complete += "</div>"
		return complete

	def convert_tweets(self, pos, neg):
		pp = self.parse_sect_tweet(pos, "",'p')
		nn = self.parse_sect_tweet(neg, "", 'n')
		return pp, nn    

	def get_latlong(self, address, add, get):
		address = address.replace(" ","-")
		latlong_json = get.check_doc_exist('key', address, 'latlongs')
		if latlong_json == None:
			url ='https://www.google.co.in/maps/search/' + address
			r = requests.get(url)
			a = [x for x in r.text.encode('utf8').split("\n")[:20] if x.strip().startswith('cacheResponse')][0]
			b = map(lambda x : x.replace("]",""), a.split(",")[:3][-2:])
			loc = { 'lat' : b[1], 'lng' : b[0] }
			jsoned = { 'key' : address, 'value' : loc }
			add.add_json_to_collection( jsoned, 'latlongs')
			return jsoned
		else:
			return latlong_json

	def ensureIndex(self, moviename):
		db[moviename + "_ParsedTweets"].ensure_index("text")
		return "Ensured Index"

	def generatenames(self, name):
		name1 = name.replace(" ","")
		name2 = name
		nam = ";" + name1 + ";" + name2
		return nam


	def trim_movie_json(self, mid):
		trim = [
			'sfreview', 
			'news_data' ,
			'meta.wiki.Music by',
			'meta.wiki.Distributed by',
			'meta.wiki.Edited by',
			'meta.wiki.Country',
			'meta.wiki.Release dates',
			'meta.wiki.Written by',
			'meta.wiki.Production companies',
			'meta.wiki.Cinematography',
			'meta.wiki.news_sources',
			'meta.wiki.Running time',
			'meta.wiki.box',
			'meta.imdb_data'	,
			'meta.wiki_data',
			'meta.summary_data',
			'meta.gaana',
			'meta.lyrics_data',
			'meta.buff.funstuff',
			'meta.buff.track',
			'meta.buff.news_data',
			'meta.buff.release_date',
			'meta.buff.crew_Details',
			'meta.buff.main_cast',
			'meta.buff.tech',
			'meta.buff.gallery',
			'meta.buff.cast_details',
			'meta.buff.running_time',
			'reviews',
			'buff']
		copy_doc = get.get_latest_movie_json(mid)
		db['movie_jsons_1'].update({'_id': mid}, copy_doc, True)
		for each in trim:
			if each == 'reviews':
				mmid = db['movie_jsons_1'].find_one({'_id' : mid} , {'reviews_data' : 1})
				for rv in mmid['reviews_data']:
					del rv['meta_description']
					del rv['text']
				db['movie_jsons_1'].update({ '_id' : mid } , { '$set'   : { 'reviews_data' : mmid['reviews_data']  }})
			else:
				db['movie_jsons_1'].update({ '_id' : mid } , { '$unset' : { each : 1 }}); 




	def map_lyrics(self, moviename):
		custom = {
			'Super Man' : 'Main Toh Superman',
			'Micromax Singh is Bliing Rap' : 'The Singh Is Bliing Rap',
			'Tere Naina Maar' : 'Tera Naina Maar Hi Daalenge',
			"I'm Sorry Par Tumse Pyaar Ho Gaya" : "Tumse Pyar Ho Gaya",
			"Yeh Ishq" : "Ishq Da Maara",
			"Bihari Valentine" : "Bihari Valentine",
			"Guddu Ki Gun" : "Guddu Ki Gun (Title)",
			"Kolkata Qutub Minar" : "Kolkata Qutub Minar",
			"Surroor" : "Tera Suroor",
			"Icecream" : "Ice Cream Khaungi"
			}


		x = db['movie_jsons'].find_one({'_id' : moviename})
		
		if x['meta']['lyrics_data'] == None:
			return None

		for each in x['meta']['buff']['track']:
			if 'Juke Box' in each['track_name']:
				continue
			try:
				tnam = str(each['track_name'].split("-")[0].strip().split("(")[0].strip().replace('Title Song', '')
					.replace("Lyrics","").strip()).encode('utf8') \
					.replace(" Mashup", "")

				got = False
				for lyr in x['meta']['lyrics_data']:
					if 'title' not in lyr:
						continue
					
					lyr['title'] = str(lyr['title'].split("(")[0].strip().replace('Title Song', '').replace("Lyrics","").strip()).encode('utf8')
					
					if lyr['title'] == tnam:
						got = True
						break
					elif ratio(lyr['title'], tnam) > 0.85:
						got = True 
						break

					elif lyr['title'][:15].startswith(tnam[:15]):
						got = True 
						break

					elif lyr['title'][:7].startswith(tnam[:7]):
						got = True 
						break

					elif lyr['title'].lower() in tnam.lower():
						got = True
						break

					elif tnam.lower() in lyr['title'].lower():
						got = True 
						break

				if got == True:
					lyrics = lyr['lyrics']
					each['lyrics'] = lyrics

				elif tnam in custom:
					for xx in x['meta']['lyrics_data']:
						xx['title'] = str(xx['title'].split("(")[0].strip().replace('Title Song', '').replace("Lyrics","").strip()).encode('utf8')
						if custom[tnam] == xx['title']:
							each['lyrics'] = xx['lyrics']

			except Exception as E:
				print E 
				continue
		_id = x['_id']
		trk = x['meta']['buff']['track']
		print db['movie_jsons'].update( {'_id' : _id } , { '$set' :   {  'meta.buff.tracks'  : trk  }})
		return 


	def colorTweets(self, this):
		ignore = ['starring', 'critic', 'phantom', 'talking', 'bumper', 'torrent']
		thus = []
		for x in this:	
			txt = []
			try:
				for wrd in x['text'].split():
					if wrd.lower() not in ignore:
						if wrd in x['positive_words']:
							wrd = "<font color='#7CB02E'>"+wrd+"</font>"
						if wrd in x['negative_words']:
							wrd = "<font color='#DE4343'>"+wrd+"</font>"
					wrd = wrd.replace(".@"," @")
					wrd = wrd.replace(".http"," http")
					if wrd.startswith('RT'):
						continue
					# if wrd.startswith("http"):
					# 	wrd = "<a href='"+wrd+"' target='_blank'>"+wrd+"</a>"
					# 	continue
					elif wrd.startswith("@"):
						wrd = "<font color='#65BEDB'><a href='http://www.twitter.com/" + wrd.replace("@","") + "' target='_blank'>"+wrd+"</a></font>"
					elif wrd.startswith("#"):
						wrd = "<font color='#65BEDB' style='font-weight:600'><a href='#'>"+wrd+"</a></font>"
					txt.append(wrd)
			except:
				continue
			x['text'] = " ".join(txt)
			thus.append(x)
		return thus


	def valid_tweets(self, moviename):
		keep_list = open('vocab/keepWords.txt').read().strip().split("\n")
		true = ['JJS', 'JJ',' JJR', 'RB']
		mains = {}
		p, n = get.get_sentiment_tweets_api(moviename + "_ParsedTweets", 50 )
		valid_n = []
		cnt = 0
		for each in n:
			try:
				txt = " ".join(each['text'].split()).encode('utf8')
				isValid = False
				if "http" in txt:
					isValid = False
				else:
					valid_pos = 0
					for wrd_pos in TextBlob(txt).tags:
						wrd = wrd_pos[0].lower()
						pos = wrd_pos[1]
						if wrd in [_.lower() for _ in each['negative_words']]:
							if pos in true:
								valid_pos += 1 
							elif wrd in keep_list:
								valid_pos += 1
					if valid_pos > 0:
						valid_n.append(each)
						cnt += 1 
			except:
				continue

		valid_p = []
		for each in p:
			try:
				txt = " ".join(each['text'].split()).encode('utf8')
				if "http" not in txt:
					valid_p.append(each)
			except:
				continue


		pop = get.get_popular_tweets(moviename + "_ParsedTweets", 50)
		valid_pop = []
		for each in pop:
			try:
				txt = " ".join(each['text'].split()).encode('utf8')
				if "http" not in txt:
					valid_pop.append(each)  
			except:
				continue
		
		valid_p = update.colorTweets(valid_p)
		valid_n = update.colorTweets(valid_n)
		valid_pop = update.colorTweets(valid_pop)

		return valid_p, valid_n, valid_pop 

	def updatestar(self):
		from DataAnalyzer.Stars import get_stars
		for x in db['movie_jsons_1'].find({}, {'stars' : 1, 'rank' : 1 }):
			rnk = x['rank'] 
			print rnk
			stars = get_stars(rnk)
			db1['movie_jsons_1'].update({'_id' : x['_id']}, {'$set'  : {'stars' : stars}  }   )

update = UpdateData()
add = AddData()
get = GetData()