from dbHandler import db, get
from textblob import TextBlob

def improve_tweets():
	keep_list = open('vocab/keepWords.txt').read().strip().split("\n")
	true = ['JJS', 'JJ',' JJR', 'RB']
	mains = {}
	for x in db['movie_jsons_1'].find({}, {'_id': 1}):
		mname = x['_id']
		p, n = get.get_sentiment_tweets_api(mname + "_ParsedTweets", 30 )
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
						print txt
						cnt += 1 
			except:
				continue
	return valid