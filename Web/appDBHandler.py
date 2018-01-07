from pymongo import MongoClient, ASCENDING, DESCENDING
import json, csv
from operator import itemgetter
import math
import gridfs

serveraddress = 'localhost'
serveraddress1 = '130.211.189.17'
client = MongoClient(serveraddress, 27017)
db = client['MovieMasterTweets']

# client1 = MongoClient(serveraddress1, 27017)
# db1 = client1['MovieMasterTweets']

MJCollection = db['MovieJson']
fs = gridfs.GridFS(db)

class GetData:
	def __init__(self):
		return None

	def decide_club(self, value):
		if value >= 500:
			club = "500"
		elif value >= 400 and value < 500:
			club = "400" 
		elif value >= 300 and value < 400:
			club = "300"
		elif value >= 200 and value < 300:
			club = "200" 
		elif value >= 100 and value < 200:
			club = "100"
		elif value >= 90 and value < 100:
			club = "90"
		elif value >= 80 and value < 90:
			club = "80"
		elif value >= 70 and value < 80:
			club = "70"
		elif value >= 60 and value < 70:
			club = "60"
		elif value >= 50 and value < 60:
			club = "50"
		elif value >= 40 and value < 50:
			club = "40"
		elif value >= 30 and value < 40:
			club = "30"
		elif value >= 20 and value < 30:
			club = "20"
		elif value >= 10 and value < 20:
			club = "10"	
		elif value >= 5 and value < 10:
			club = "5"	
		elif value >= 1 and value < 5:
			club = "1"
		else:
			club = None	
		return club

	def getCrore(self, value):
		value = str(value)
		count = len(value) - len(value.rstrip('0'))
		if count == 8:
			return value[:len(value) - count] + "0", "Crore"
		elif count == 7:
			return value[:len(value) - count], "Crore"
		elif count == 6:
			if len(value) == 7:
				return value[:len(value) - count] + "0", "Lakhs"
			elif len(value) == 8:
				return float(int(value[:len(value) - count]))/10, "Crore"
			elif len(value) == 9:
				return float(int(value[:len(value) - count]))/10, "Crore"
		elif count == 5:
			return float(int(value[:len(value) - count]))/100, "Crore"
		elif count == 4:
			if len(value) == 7:
				return float(int(value[:len(value) - count]))/10, "Lakhs"
			elif len(value) == 8:
				return float(int(value[:len(value) - count]))/1000, "Crore"				
			elif len(value) == 6:
				return float(int(value[:len(value) - count]))/10, "Lakh"	
		elif count == 3:
			if len(value) == 7:
				return float(int(value[:len(value) - count]))/100, "Lakhs"	
			elif len(value) == 6:
				return float(int(value[:len(value) - count]))/100, "Lakhs"	

	def getBoxPercent(self, moviename, keyname):	
		box = db['BoxOfficeDetails'].find_one({'_id' : moviename})
		if keyname in box:
			try:
				value_key = int(box[keyname].replace(",","").strip())		
				ahead_movies = 0
				count_movies = 0
				
				allmovies = db['BoxOfficeDetails'].find({}, {'_id' : 0, keyname : 1})
				for each in allmovies:
					if keyname in each:
						try:
							if value_key >= int(each[keyname].replace(",","")):
								ahead_movies += 1 
							count_movies += 1 
						except Exception as E:
							continue 
				return int(round(float(ahead_movies)/count_movies * 100,1))
			except Exception as E:
				return None
		else:
			return None


	def getCroreLakh(self, number):
		z = number
		i = z.split(",")
		result = ""
		num = None
		if len(i) >= 3:
			lack = i[-3]
			if len(i) >= 4:
				a = i[:len(i)-3]
				num = 0
				mult = 1
				for k in a[::-1]:
					num += int(k)*mult
					mult *= 100
			if num is not None:
				result +=  str(num)
				result += ' crores'
			result += " " + str(lack)
			result += ' lakhs'
		return result.strip()

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

	def getTotalCountOfKey(self, keyName, collection_name):
		collection = db[collection_name]
		pipeline = [{"$group": {"_id": "all", "totalCount":{"$sum":"$"+keyName}}}]
		documents = collection.aggregate(pipeline)
		return [x for x in documents['result']]

	def getImagesFromGrid(self, moviename):
		try:
			img = fs.get_last_version(_id = moviename + '_wiki').read().encode('base64')
		except:
			img = None 

		try:	
			img1 = fs.get_last_version(_id = moviename + '_buff').read().encode('base64')
		except:
			img1 = None 

		try:
			anal = self.get_latest_movie_json(moviename)['meta']['wiki']['Starring'].split(",")
			acts = {}
			for x in anal:
				nam = x.strip()
				try:
					nam = nam.replace(" ","_").replace("[1]", "").replace("[2]", "").strip()
					acts[nam] = fs.get_last_version(_id = nam).read().encode('base64')
				except Exception as E:
					print "No Image for", nam
					continue
		except Exception as E:
			print E
			acts = {}


		return img, img1, acts

	def get_next_news(self, moviename):
		collection = db['movie_jsons']
		data = collection.find_one({"_id" : moviename}, {'news_data' : 1})['news_data']
		data = sorted(data, key=itemgetter('count'), reverse = True) 
		return data

	def get_movie_content(self, collection_name, dtype):
		return db[collection_name].find({'dataType' : dtype})

	def get_next_reviews(self, moviename):	
		collection = db['movie_jsons_1']
		data = collection.find_one({"_id" : moviename}, {'reviews_data' : 1})['reviews_data']
		try:
			data = sorted(data, key=itemgetter('rating'), reverse = True) 
		except:
			data = sorted(data, key=itemgetter('count'), reverse = True)
		return data

	def get_social_images(self, moviename):
		data = db[moviename + '_socialImages'].find()	
		return data

	def getBoxOfficeDetails(self, moviename):
		coll = db['BoxOfficeDetail1'].find_one({'_id' : moviename})
		return coll 

	def get_upcoming_movies(self, count):
		collection = db['movie_jsons_1']
		pipeline = [ { '$sort' : { 'MovieId' : -1}}	,
					 { '$limit' : count },
					 {"$group": {"_id": "$movie.name", "projection" : { "$push": 
					 { 'trailer':"$meta.buff.trailer", 
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
		collection = db['movie_jsons_1']
		pipeline = [ { '$sort' : { 'rank' : -1}}	,
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



	def get_allmovies_movies(self, match_query, sort_query):
		collection = db['movie_jsons_1']
		pipeline = [ 
					 {'$match' : match_query },
					 {'$sort' : sort_query },
					 {"$group": {"_id": "$movie.name", "projection" : { "$push": { 'trailer':"$meta.buff.gallery" , 
					 'tweetcount' : '$analyzed.total_tweets' , 'MovieId':'$MovieId', 'rank':'$rank','uname':'$name', 
					 'stars' : '$stars', 'wikiimg' : '$wikiimg', 'buffimg' : '$buffimg' , 'poster' : '$meta.wiki.poster', 
					 'posterAlternate' : '$meta.buff.gallery', 'name' : '$meta.wiki.name', 
					 'date' : '$meta.wiki.Release dates' }}}}
					]
		if match_query == 'all':
			pipeline = pipeline[1:]
		data = collection.aggregate(pipeline)
		data = [x for x in data['result']]
		return data

	def get_movienames(self ,tag):
		if tag.startswith("Keyword:"):
			val = tag.replace("Keyword:", "").strip()
			if val == 'All':
				match_query = 'all'
			else:
				match_query = { 'stars' : val}
			sort_query = { 'MovieId' : -1 }

		elif tag.startswith('Sort:'):
			if "-" in tag:
				prev_filter = tag.split("-")[1]
				val = tag.split("-")[0]
				val = val.replace("Sort:", "").strip()
				if val.startswith('I:'):
					by = 1 
					val = val.replace("I:", "")
				else:	
					by = -1
					val = val.replace("D:", "") 
				sort_query = { val : by } 
				
				if prev_filter == 'All':
					match_query = 'all'
				else:
					match_query = { 'stars' : prev_filter}

		res = self.get_allmovies_movies(match_query, sort_query)
		return res






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

	def check_doc_exist(self, key, value, collection_name):
		status = db[collection_name].find_one({ key : value })
		return status

	def get_value(self, key, collection_name):
		data = db[collection_name].find_one( { 'key' : key })
		if data:
			return data['value']
		else:
			return None

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
			 { '$group' : {'_id': '$negative_words'  ,'tweets1' : {'$first':{'popularity_score':'$popularity_score','_id':'$_id','sentiment':'$sentiment','text':'$text' ,'retweet_count':'$retweet_count','created_at':'$created_at','favorite_count':'$favorite_count','user':'$user','companys':'$companys','dimensions':'$dimensions','retweeted':'$retweeted','negative_words':'$negative_words','positive_words':'$positive_words','clean_text':'$clean_text','retweeted':'$retweeted'}}}},
			 { '$sort' : { 'tweets1.sentiment' : 1}},    
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

	def get_users_api(self, moviename, limit=36):
		limit = 42
		collection = self.get_latest_movie_json(moviename)['analyzed']['user_details']
		line = ""
		count = 0 
		for x in collection:
			line += """
				<span class='images-collage-tag'> \
        			<a href="#">
        				<img src='""" + x['lnk'] + """' onError="this.src = '../static/images/null.jpg'" width="48px"> \
            		</a>
            	</span>"""
			count += 1
			if count == limit:
				break
		return line

	def get_infulencer_api(self, moviename, limit=5):
		collection = self.get_latest_movie_json(moviename)['analyzed']['logscore'][:limit]
		line = ""
		for inf in collection:
			fc = "{:,.2f}".format(inf['fc']).replace(".00","")
			line +=  """<div class='row influencer-row'> 
          					<div class='col-md-12 col-sm-12 col-xs-12 inf-name'> 
	            				<img src=""" + inf['img'] + """ class='influencer-img' onError="this.src = '../static/images/null.jpg'"> 
	            				<div class='img-class'> 
					              <div class='inf-name-text'><a href="https://www.twitter.com/""" + inf['sname'] + """" target="_blank">""" + inf['name'] + """</a></div> 
					              <div class='inf-name-handle'>@""" + inf['sname'] + """</div> 
					              <div class='inf-name-handle'>(""" + str(fc) + """ followers)</div>   
					            </div> 
          					</div> 
        				</div>"""
		return line

	def get_indian_cities(self):
		collection = db['indian_cities_master']
		data = collection.distinct('_id')
		return data
		
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
					'name_id': "/../..",
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
				link = {'source': 0, 'target': i+1 }
				if tag['name_id'] == "FourPillarsOfBasement":
					tag['name'] = "Four Pillars Of Basement"


				
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



class UpdateData:

	def __init__(self):
		return None

	def IsShowable(self, moviename):
		upcoming = get.get_upcoming_movies(5)
		crrnt = [mv['uname'] for mv in upcoming[0]['projection']]
		if moviename in crrnt:
			return "True" 
		else:
			return "False"

	def convert_reviews(self, data):
		html_data = "<div class='review-section row-card'>"
		mobile_data = """<div class="review-section row-card">
					"""
		for each in data:
			
			if any(wrd in each['link'] for wrd in ['music', 'album', 'sound']):
				continue


			if 'rating' not in each:
				rate = str("")
				star = ""
			else:

				star, kw = update.get_stars(each['rating'])
				
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
				desc_text = "The critic reviewer '" + each['name'].strip() +  "' from the website " + each['source'].strip() + \
				 " rated the movie " + str(each['rating']) + " out of 10. The complete review is available on the source. "
			else:
				if any(wrd in each['link'] for wrd in ['music', 'album', 'sound']):
					continue
				desc_text = each['desc_text'][:150] + " ... "
			html_data += """
					
					<div class="row rv">
						<div class="col-md-1 review-image">
                   	 		<img src=""" + each['newSrc'] + """>
                    	</div>
                    	<div class="col-md-8 review-txt">
                    		<p class="rsource-n">""" + each['name'].strip() + " <span style='float:right'> " + star + """ </span></p>
                    		<p class="rsource-s">""" + each['source'].strip() + """</p>  
                    	</div>
                    	<div class="col-md-2">
                    		""" + rate + """
                    	</div>
                    	<div class="col-md-12 rtext">
                    		""" + desc_text + """<a href=""" + each['link'] + """ target='_blank'>Read Complete</a>
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
                    		<p class='rsource-s'>""" + each['source'].strip() + """</p>  
                    	</div>
                    	<div class="col-md-2 col-xs-2 col-sm-2">
                    		""" + rate + """
                    	</div>
                  		</div>
                  	"""
		mobile_data += """ 
                  	</div>"""
		html_data += "</div>"
		return html_data, mobile_data


	# Expensify


	def convert_news(self, data):
		html_data = ""
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
			<p>""" +  desc_text[:300]  + """<a href=""" + each['link'] + """>Read Complete</a></p>
			</div>
			</div>"""

		return html_data


	def convert_new_news(self, news, mname):
		data = ""
		for new in news:
			if 'image' in new:
 				img1 = """<img src='""" + new['image']['url'] + """' width="195.188" height="160" onerror="this.src = '../static/images/sf.jpg'">"""
 			else:
 				img1 = """<img src="../static/images/sf.jpg" width="195.188" height="160">"""

 			if mname.lower().replace(" ","") not in new['titleNoFormatting'].lower().replace(" ", ""):
 				continue

 			if len(new['titleNoFormatting']) < 100:
	 			new['ttle'] = new['titleNoFormatting']
	 		else:
	 			new['ttle'] = new['titleNoFormatting'][:100] + "..."

 			new['src'] = new['publisher'].split(",")[0]
 			if len(new['src']) > 25:
 				new['src'] = new['src'][:25] + "..."

 			dt = new['publishedDate'].split(",")[1].strip().split()[0] +" "+ new['publishedDate'].split(",")[1].strip().split()[1] \
 						 +" "+ new['publishedDate'].split(",")[1].strip().split()[2]
 			data +=	""" <div class="col-md-4" title='""" + new['titleNoFormatting'] + """' data-title="tooltip">
 						<a href='""" + new['unescapedUrl'] + """' target="_blank">
 						<div class="newsCard-parent">
 							<div class="newsCard">
 								<div class="newsImg">""" + img1 + """ </div>
 								<div class="NewsData">
 									<span class="newsTitle">""" +  new['ttle'] + """<br><br>""" + new['src'] +"""<br>"""+ dt +"""</span>
 								</div>
 							</div>
 						</div>
 						</a>
 						</div>
 						
 					"""
 		return data

	def parse_sect_tweet(self, data, flag, sentflag):
		import HTMLParser
		complete = "<div class='row-card'>"
		for tweet in data:
			if 'lang' in tweet:
				if tweet['lang'] == 'und':
					continue
				elif tweet['lang'] == 'hi':
					continue


			if tweet['user']['country'] != "India":
				continue
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
                      	&bull;
                        """ + tweet['created_at'].split()[1] + """ 
                        """ + tweet['created_at'].split()[2] + """,
                        """ + tweet['created_at'].split()[-1] + """
                      </div>
                    </div>
                  </div>
                  <div class="tweet-box-bottom">
                    <div class="tweet-box-text""" + flag  +  """ ">
                      """ + HTMLParser.HTMLParser().unescape(tweet['text']) + """
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


	def get_movie_cards(self, allmovies):
		dat  = ""
		for x in allmovies:
			for movie in x['projection']:
				if 'wikiimg' in movie:
					if  movie['wikiimg'][0] != None:
						img1 = "<img alt='Poster Movie' src='data:image/jpeg;base64," + movie['wikiimg'][0] + "'>"
					else:
						img1 = "<img alt='Poster Movie' src='data:image/jpeg;base64," + movie['buffimg'][0] + "'>"
				else:
					if movie['poster']:
						img1 = "<img src=" + movie['poster'] + ">"
					else:
						img1 = "<img src=" + movie['trailer'][0]['Posters'][0].replace('w=1000','w=200') + ">"
				dat += """<div class="col-sm-3 col-md-2 col-xs-6 wow fadeInLeft animated sortrating" data-search='""" + movie['name'] + """' data-rating='""" + str(movie['rank']) + """' data-wow-duration="1.5s" data-wow-offset="10" data-wow-delay="0.5s" style="visibility: visible; -webkit-animation-duration: 1.5s; -webkit-animation-delay: 0.5s;">
						<div class="movies-update">
						<a href="/movie/""" + str(movie['uname']) + """">""" + img1 + """</a>
						<div class="card-rating">""" + str(movie['rank']) + """</div>
						<div class="movies-update-details">
							<div class="movies-update-discription">
								<div class="desc1">""" + str(movie['stars'][0]) + """</div>
								<div class="desc1">""" + str(movie['stars'][1])  + """</div>
								<div class="desc1"><i class="fa fa-twitter"></i>""" +str(movie['tweetcount']) + """</div>
							</div>
						</div>
						</div>
						</div>"""
		return dat

	def convert_tweets(self, pos, neg):
		pp = self.parse_sect_tweet(pos, "",'p')
		nn = self.parse_sect_tweet(neg, "", 'n')
		return pp, nn    

	def perform_movie(self):
		for movie in db['BoxOfficeDetails'].find():
			budget = movie['Budget']
			if len(budget) > 5:
				value = int(budget.replace(",", ""))
				bget = get.getCrore(value)
				movie['budget_fix'] = bget
			else:
				movie['budget_fix'] = budget
			
			try:
				if 'First Weekend' in movie:
					value = int(movie['First Weekend'].replace(",", ""))
					wkend = get.getCrore(value)
					movie['weekend_fix'] = wkend
				if 'First Day' in movie:
					value = int(movie['First Day'].replace(",", ""))
					dy = get.getCrore(value)
					movie['day_fix'] = dy
				if 'First Week' in movie:
					value = int(movie['First Week'].replace(",", ""))
					wk = get.getCrore(value)
					movie['week_fix'] = wk

			except Exception as E:
				print E 
				continue
			
			collection = movie['Total Nett Gross']
			movie['collection_fix'] = get.getCroreLakh(collection)

			if "crores" in movie['collection_fix']:
				cvalue = int(movie['collection_fix'].split()[0])
				club = get.decide_club(cvalue)
				movie['club'] = club 
			else:
				movie['club'] = None

			db['BoxOfficeDetail1'].insert(movie)

	def convert_social_images(self, data):
		zhtml = ""
		for each in data:
			zhtml += """<a href='""" + each['url'] + """' class="social-image"  data-fancybox-group="gallery"  title = '""" + each['ctext'] + """'><img class="" src='""" + each['url'] + """' data-toggle='tooltip' title='""" + each['ctext'] + """' onError='this.src = "../static/images/null.jpg"'></a>"""
		return zhtml

	def get_stars(self, i):
		a = '<i class="fa fa-star fstar"></i>'
		a1 = '<i class="fa fa-star-half-o fstar"></i>'
		b = '<i class="fa fa-star sstar"></i>'
		b1 = '<i class="fa fa-star-half-o sstar"></i>'
		c = '<i class="fa fa-star tstar"></i>'
		c1 = '<i class="fa fa-star-half-o tstar"></i>'
		d = '<i class="fa fa-star frstar"></i>'
		d1 = '<i class="fa fa-star-half-o frstar"></i>'
		e = '<i class="fa fa-star fvstar"></i>'
		e1 = '<i class="fa fa-star-half-o fvstar"></i>'
		f = '<i class="fa fa-star-o fvstar"></i>'

		stat = ""
		if i >= 0 and i < 1:
			stat = a1 + f + f + f + f
			kw = 'Must Avoide'
		elif i >= 1 and i < 2:
			stat = a + f + f + f + f
			kw = 'Avoidable'
		elif i >= 2 and i < 3:
			stat = a + b1 + f + f + f
			kw = 'Avoidable'
		elif i >= 3 and i < 4:
			stat = a + b + f + f + f
			kw = 'Below Average'
		elif i >= 4 and i < 5:
			stat = a + b + c1 + f + f
			kw = 'Below Average'
		elif i >= 5 and i < 6:
			stat = a + b + c + f + f
			kw = 'Average'
		elif i >= 6 and i < 7:
			stat = a + b + c + d1 + f
			kw = 'Average'
		elif i >= 7 and i < 8:
			stat = a + b + c + d + f
			kw = 'Recommended'
		elif i >= 8 and i < 9:
			stat = a + b + c + d + e1
			kw = 'Must Watch'
		elif i >= 9 and i <= 10:
			stat = a + b + c + d + e
			kw = 'All Time Great'
		return stat, kw

update = UpdateData()
get = GetData()