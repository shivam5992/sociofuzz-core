import csv, ast, math

def calculate_influence_score(data):
	user_tweets = {}
	for each in data:
		rc = 0
		fc = 0
		for k,v in each.items():
			if k == 'retweet_count':
				rc = v
			if k == "favorite_count":
				fc = v
			if k == 'user':
				for k1,v1 in each[k].items():
					if k1 == 'id':
						userid = str(v1)
						if userid not in user_tweets:
							user_tweets[userid] = {}
							user_tweets[userid]["tweets"] = 1
							user_tweets[userid]["followers"] = 0
							user_tweets[userid]["retweets"] = rc
							user_tweets[userid]["favorite_count"] = fc
						else:
							user_tweets[userid]["tweets"] += 1
							user_tweets[userid]["retweets"] += rc
							user_tweets[userid]["favorite_count"] += fc

					if k1 == "followers_count":
						user_tweets[userid]["followers"] = v1
					if k1 == "screen_name":
						user_tweets[userid]["screen_name"] = v1
					if k1 == "name":
						user_tweets[userid]["name"] = v1
				

	''' Log Score '''
	user_score_log = {}
	for k, v in user_tweets.items():
		f = user_tweets[k]["followers"]
		r = user_tweets[k]["retweets"]
		score = math.log((1+f)*(1+r))
		user_score_log[k] = score

	''' Normal Score '''
	user_score_normal = {}
	for k, v in user_tweets.items():
		f = user_tweets[k]["followers"]
		r = user_tweets[k]["retweets"]
		score = (1+f)*(1+r)
		user_score_normal[k] = score

	log_dictionary = {}
	for k, v in user_score_log.items():
		if k not in log_dictionary:
			log_dictionary[k] = {}
			log_dictionary[k]['log_score'] = user_score_log[k]
			log_dictionary[k]['normal_score'] = user_score_normal[k]
	return log_dictionary


