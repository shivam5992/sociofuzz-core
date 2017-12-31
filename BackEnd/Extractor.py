from DataExtractor.BuffExtractor import BuffExtractor
from DataExtractor.WikiExtractor import WikiExtractor
from DataExtractor.QuoteExtractor import QuoteExtractor
from DataExtractor.LyricsExtractor import LyricsExtractor, LyricsBogiExtractor
from DataExtractor.NewsExtractor import NewsExtractor
from DataExtractor.ReviewExtractor import ReviewExtractor
from DataExtractor.ImdbExtractor import ImdbExtractor
from DataExtractor.TimesExtractor import TimesExtractor
from DataExtractor.BoxOfficeExtractor import BoxOfficeExtractor
from BeautifulSoup import BeautifulSoup
import multiprocessing.pool
import ast, csv, requests
import multiprocessing
from dbHandler import get, BoxCollection, db, MJCollection as collection
# collection = db['reviews_refresh']

class NoDaemonProcess(multiprocessing.Process):
    def _get_daemon(self):
        return False
    def _set_daemon(self, value):
        pass
    daemon = property(_get_daemon, _set_daemon)

class MyPool(multiprocessing.pool.Pool):
    Process = NoDaemonProcess

class Extract:
	def trivias_mashup(self, times, imdb):
		for each in imdb['trivias']:
			if each not in times:
				times.append(each)
		return times

	def url_fixer(self, url):
		if url == "None":
			return url
		if not url.startswith("http"):
			url = "http://" + url
		return url

	def get_data(self, moviename):
		metadata = get.check_doc_exist('Movie Name', moviename ,'moviemeta')	

		print "buff"
		buff_url =  self.url_fixer(metadata['BuffUrl'].strip())
		buff = BuffExtractor(buff_url)
		buffdata = buff.get_buff_data()
		buffreviews = buff.reviews()

		print "wiki"
		movie_wiki_url = self.url_fixer(metadata['WikiUrl'].strip())
		wiki = WikiExtractor(movie_wiki_url)
		wiki_info = wiki.info_extractor()
		wiki_data = wiki.text_extractor()

		print "imdb"
		imdb_url = self.url_fixer(metadata['ImdbUrl'].strip())
		
		imdb = ImdbExtractor(imdb_url)
		imdb_data = imdb.get_data()

		print "Times"
		times_url = self.url_fixer(metadata['TimesUrl'].strip())
		if times_url.lower() == "none":
			times_data = None
			trivias = self.trivias_mashup([], imdb_data)
			box = {}
			gana = None
		else:
			times = TimesExtractor(times_url)
			times_data = times.get_data()
			trivias = self.trivias_mashup(times_data['trivias'], imdb_data)
		
		print "Lyrics"
		lyrics_url = self.url_fixer(metadata['LyricsUrl'].strip())
		if "lyricsmint" in lyrics_url:
			lyrics = LyricsExtractor(lyrics_url)
			lyrics_data = lyrics.get_lyrics()
		elif 'lyricsbogie' in lyrics_url:
			lyrics = LyricsBogiExtractor(lyrics_url)
			lyrics_data = lyrics.get_lyrics()
		else:
			lyrics_data = None

		print "Quotes"
		quote_url = self.url_fixer(metadata['QuotesUrl'].strip())
		if quote_url.lower() == "none":
			quote_data = None
		else:
			quote = QuoteExtractor(quote_url)
			quote_data = quote.get_quotes()

		
		doc = {   'quote_data' : quote_data, 
				  '_id' : moviename ,
				  'buff' : buffdata ,
				  'MovieId' : metadata['MovieId'] ,
				  'wiki' : wiki_info ,
				  'wiki_data' : wiki_data ,
				  'trivias' : trivias ,
				  'imdb_data' : imdb_data ,
				  'lyrics_data' : lyrics_data ,
				}

		if collection.find_one({  '_id'  : moviename }) == None:
			collection.insert(doc)
			print "Added Quote Data"
		else:
			collection.update({'_id' : moviename},   {'$set': {'crawl_data' : doc }} )
			print "Updated Quote Data"

	
	def news_crawl(self, moviename):
		metadata = get.check_doc_exist('Movie Name', moviename ,'moviemeta')	
		buff_url =  self.url_fixer(metadata['BuffUrl'].strip())
		buff = BuffExtractor(buff_url)
		buffdata = buff.get_buff_data()

		movie_wiki_url = self.url_fixer(metadata['WikiUrl'].strip())
		wiki = WikiExtractor(movie_wiki_url)
		wiki_info = wiki.info_extractor()

		if wiki_info['news_sources'] == None:
			wiki_info['news_sources'] = []

		print "Start Extraction of News"
		collated_news = {}
		for trim in buffdata['news_data']:
			collated_news[trim['link']] = trim 

		
		for i, each in enumerate(wiki_info['news_sources']):
			collated_news[each['link']] = each
			
		nd = collection.find_one({'_id' : moviename})
		if nd == None:
			parsed_links = []
			collection.update({'_id' : moviename}, { 'news_data' : []}, upsert=True)
		else:
			if 'news_data' not in nd:
				parsed_links = []
				collection.update({'_id' : moviename}, { '$set' : {'news_data' : [] }} )
			else:
				parsed_links = [x['link'] for x in nd['news_data']]

		collated_new_news = {}
		for x in collated_news:
			if x == "":
				continue
			if x not in parsed_links:
				collated_new_news[x] = collated_news[x]
		
		if len(collated_new_news) >= 1:
			collated_new_news = [({x:y}, moviename) for x,y in collated_new_news.iteritems()] 
			p = multiprocessing.Pool(len(collated_new_news))
			p.map(worker_news, collated_new_news)
			p.close()

	def reviews_crawl(self, moviename):
		metadata = get.check_doc_exist('Movie Name', moviename ,'moviemeta')	
		buff_url =  self.url_fixer(metadata['BuffUrl'].strip())
		buff = BuffExtractor(buff_url)
		buffreviews = buff.reviews()

		print "Start Extraction of Reviews"
		
		collated_reviews = {}
		for ll in buffreviews:
			collated_reviews[ll['link']] = ll


		reviews_url = self.url_fixer(metadata['ReviewsUrl'].strip())
		if reviews_url != "None":
			resp = requests.get(reviews_url)
			soup = BeautifulSoup(resp.text)
			ptags = soup.findAll('p', attrs = {'class' : 'critic-info-link'})
			name = soup.findAll('p', attrs = {'class': 'critic-info-name'})
			source = soup.findAll('p', attrs = {'class' : 'critic-info-site'})
			rating = soup.findAll('p', attrs = {'class' : 'critic-rating-count'})

			for i, each in enumerate(ptags):
				try:
					res = {}
					res['link'] = each.a['href']
					res['source'] = source[i].text
					res['name'] = name[i].text
					res['rating'] = rating[i].text
					res['rating'] = float(res['rating'])/10 + 0.1
					if each.a['href'] not in collated_reviews:
						collated_reviews[each.a['href']] = res
					else:
						oldrate = collated_reviews[each.a['href']]['rating']
						collated_reviews[each.a['href']]['rating'] = []
						collated_reviews[each.a['href']]['rating'].append(oldrate)
						collated_reviews[each.a['href']]['rating'].append(res['rating'])
						ratinglist = collated_reviews[each.a['href']]['rating']
						collated_reviews[each.a['href']]['rating'] = round(float(sum(ratinglist))/len(ratinglist),1)
				except Exception as E:
					print E 
					continue

		nd = collection.find_one({'_id' : moviename})

		if nd == None:
			parsed_urls = []
			collection.update({'_id' : moviename}, { 'reviews_data' : []}, upsert = True)
		else:
			if 'reviews_data' not in nd:
				parsed_urls = []
				collection.update({'_id' : moviename}, { '$set' : {'reviews_data' : [] }} )
			else:
				parsed_urls = [x['link'] for x in nd['reviews_data']]

		collated_new_urls = {}
		for x in collated_reviews:
			if x not in parsed_urls:
				collated_new_urls[x] = collated_reviews[x]

		if len(collated_new_urls) >= 1:
			collated_new_urls = [({x:y}, moviename) for x,y in collated_new_urls.iteritems()] 
			p = multiprocessing.Pool(len(collated_new_urls))
			p.map(worker_reviews, collated_new_urls)
			p.close()


	def getBoxOffice(self, moviename):
		metadata = get.check_doc_exist('Movie Name', moviename ,'moviemeta')
		times_url = metadata['TimesUrl'].strip()
		try:
			times = TimesExtractor(times_url)
			box = times.get_data()['box']
			return box
		except:
			box = {'No Data Here' : ''}
			return box

	def getBoxOfficeData(self, moviename):
		metadata = get.check_doc_exist('Movie Name', moviename ,'moviemeta')
		box_url = metadata['BoxOffice'].strip()

		if "#" in box_url:
			box_url = box_url.split('#')[0]

		doc = BoxOfficeExtractor.get_data(box_url, moviename)
		if BoxCollection.find_one({  '_id'  : moviename }) != None:
			BoxCollection.remove({'_id' : moviename})
		BoxCollection.insert(doc)
		print "Added Box Office Data"

def worker_news(elem):
	new_news = NewsExtractor(elem[0])
	new_news_data = new_news.get_news()
	collection.update({'_id' : elem[1]}, {'$addToSet' :  { 'news_data' : new_news_data[0] }}, upsert=True)

def worker_reviews(elem):
	new_reviews = ReviewExtractor(elem[0])
	new_reviews_data = new_reviews.get_critic_reviews()
	collection.update({'_id' : elem[1]}, {'$addToSet' :  { 'reviews_data' : new_reviews_data[0] }}, upsert=True)

def masterWorker(funcname):
	master_dict[funcname[0]](funcname[1])
	print "Func Completed", funcname

Extract = Extract()
master_dict = {
	'crawler' : Extract.get_data,
	'news' : Extract.news_crawl,
	'reviews' : Extract.reviews_crawl
}

def process(moviename):
	master_list = [(x,moviename) for x in master_dict]
	p = MyPool(len(master_list))
	p.daemon = False
	p.map(masterWorker, master_list)
	p.close()
	
# Extract.reviews_crawl('PremRatanDhanPayo')
# Extract.news_crawl('CharlieKayChakkarMein')
# Extract.get_data('PremRatanDhanPayo')