import urllib2, json
import requests

def getNews(queries):
	merge = []
	for query in queries:
		url = 'https://ajax.googleapis.com/ajax/services/search/news?v=1.0&q=' + query + '&rsz=4'
		a = urllib2.urlopen(url)
		news = a.read()
		news = json.loads(news)['responseData']['results']
		merge.extend(news)
	return merge


def getMovieVideos(name, service):
	query = name.strip()
	data = []
	# for i in range(5):
	i = -1
	j = (i+1)*8
	url = 'https://ajax.googleapis.com/ajax/services/search/'+service+'?v=1.0&q=' + query + '&rsz=8&start=' + str(j)
	try:
		a = urllib2.urlopen(url)
		video = a.read()
		video = json.loads(video)['responseData']['results']
	except:
		resp = requests.get(url)
		video = resp.json()['responseData']['results']
	data.extend(video)
	return data