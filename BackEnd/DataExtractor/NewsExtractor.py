from goose import Goose
from operator import itemgetter
from eventlet.timeout import Timeout
g = Goose()

class NewsExtractor:
	def __init__(self, collated):
		self.collated_news = collated

	def get_news(self):
		news_data = []
		count_total = 0
		for each,res in self.collated_news.iteritems():
			count_total += 1
			if each == '':
				continue
			try:
				with Timeout(5, False):
					article = g.extract(url = each)
					res['text'] = article.cleaned_text
					stext = res['text'].encode("utf8").replace("\n"," ")
					if len(stext) >= 300:
						stext = stext[:300]
						stext = ". ".join(stext.split(". ")[:-1])
					else:
						stext = ""
					res['desc_text'] = stext
					res['meta_description'] = article.meta_description
					res['title'] = article.title.split("|")
					
					count = 0
					if res['title'] != "":
						count += 1
					if res['desc_text'] != "":
						count += 1
					if res['date'] != "":
						count += 1
					if res['source'] != "":
						count += 1
					res['count'] = count
					news_data.append(res)
					print "News", count_total
			except Exception as E:
				print "Inside News Exception", str(E)
				continue
		return news_data