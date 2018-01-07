# from pymongo import MongoClient, ASCENDING, DESCENDING
# serveraddress = 'localhost'
# client = MongoClient(serveraddress, 27017)
# db = client['MovieMasterTweets']
# coll = db['reviews_refresh']

# for x in coll.find():
# 	_id = x['_id']
# 	print _id
# 	rd = x['reviews_data']
# 	print db['movie_jsons'].update( {'_id' : _id } , { '$set' : {  'reviews_data'  : rd  }} )
# 	# break