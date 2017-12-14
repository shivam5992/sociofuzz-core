from MatchingArchitecture import match
from DataAnalyzer.utility import utility
import json, math, ast

class RatingExtractor:
	def __init__(self):
		return None

	def _isverified(self, tweet_json):
		return tweet_json['verified']
			
	def _ispresent(self, keyword, text):
		exact_match_status = match.exact_match(keyword, text)
		lemmatized_match_status = match.lemmatize_match(keyword, text)
		
		if exact_match_status:
			return True
		elif lemmatized_match_status:
			return True
		else:
			return False 

	def _theme_extractor(self, list_of_tweets, rating_vocab_data):
		rating_vocab = {}
		theme_count = {}
		for row in rating_vocab_data:
			keyed = row.split(",")
			key = keyed[0]
			keys = keyed[1:]
			rating_vocab[key] = keyed
			theme_count[key] = 0

		for i, tweet in enumerate(list_of_tweets):
			text = tweet['text']
			
			for rating_key, keys in rating_vocab.iteritems():
				for each_key in keys:
					if self._ispresent(each_key, text):
						theme_count[rating_key] += 1


		total_captured = 0
		for key, value in theme_count.iteritems():
			total_captured += value

		theme_num = {}
		for key, value in theme_count.iteritems():
			val = round((float(value)/total_captured )*100,2)
			decimal = int("".join(str(val).split(".")[1:]))
			if decimal < 50:
				theme_num[key] = int(math.floor(val)) 
			else:
				theme_num[key] = int(math.ceil(val)) 
		return theme_num

rate = RatingExtractor()
