from pymongo import MongoClient
import ast

coll = MongoClient('104.197.69.184', 27017)['MovieMasterTweets']['BoxOfficeDetails']

for line in open("data.txt").read().strip().split("\n"):
	line = ast.literal_eval(line)
	line['_id'] = line['name']
	coll.insert(line)
	print line['name']