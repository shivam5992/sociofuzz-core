import urllib2, json
import requests

def updateNews(query, moviename, db):
	merge = []
	for st in range(10):
		st1 = st * 8
		url = 'https://ajax.googleapis.com/ajax/services/search/news?v=1.0&q=' + query + '&start=' + str(st1) + '&rsz=8' 

		try:
			a = urllib2.urlopen(url)
			news = a.read()
			news = json.loads(news)['responseData']['results']
		except:
			try:
				a = requests.get(url)
				news = a.json()['responseData']['results']
			except Exception as E:
				print E 
				continue
		for each in news:
			each['movie'] = moviename
			each['_id'] = each['unescapedUrl']
			try:
				db['NewsMaster'].insert(each)
			except Exception as E:
				print E 
				continue
	return "Updated News"

def pushNewsToInstance(moviename, db, db1):
	db1['NewsMaster'].remove({'movie' : moviename})
	for x in db['NewsMaster'].find({'movie' : moviename}):
		db1['NewsMaster'].insert(x)
	

# qry = 'PremRatanDhanPayo'
# mn = 'Prem Ratan Dhan Payo'
# updateNews(qry,mn, 'db')