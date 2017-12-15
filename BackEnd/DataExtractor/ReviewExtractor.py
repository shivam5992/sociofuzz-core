import requests
from BeautifulSoup import BeautifulSoup
from goose import Goose
from random import shuffle
import string 
import ast
from operator import itemgetter
from eventlet.timeout import Timeout
g = Goose()

class ReviewExtractor:
	def __init__(self, data):
		self.data = data
		self.punclist = string.punctuation
		self.pos = ast.literal_eval(open("DataExtractor/../vocab/poslist.txt").read())
		self.neg = ast.literal_eval(open("DataExtractor/../vocab/neglist.txt").read())
		return None

	def remove_punctuations(self, text):
		for punc in self.punclist:
			text = text.replace(punc, " ")
		return text

	def get_word_count(self, text):
		text = self.remove_punctuations(text)
		words = text.split()
		p = []
		n = []
		for wrd in words:
			wrd = wrd.lower()
			wrd = wrd.encode('utf8')
			if len(wrd) < 3:
				continue
			if wrd in self.pos:
				p.append(wrd)
			elif wrd in self.neg:
				n.append(wrd)
		t = len(words)
		return p, n, t

	def get_critic_reviews(self):
		result = []
		total_count = 0
		for each,res in self.data.iteritems():
			try:
				with Timeout(5, False):
					article = g.extract(url=each)
					res['link'] = each
					res['text'] = article.cleaned_text

					wrds = self.get_word_count(res['text'])
					res['pos'] = list(set(wrds[0]))
					res['neg'] = list(set(wrds[1]))
					res['tot'] = wrds[2]

					stext = res['text'].encode("utf8").replace("\n"," ")[:300]
					stext = ". ".join(stext.split(". ")[:-1])
					res['desc_text'] = stext			
					res['meta_description'] = article.meta_description
					res['title'] = article.title.split("|")[0]

					count = 0
					if res['title'] != "":
						count += 1
					if res['desc_text'] != "":
						count += 1
					if res['source'] != "":
						count += 1
					res['count'] = count
					result.append(res)
					
					total_count += 1
					print "Rv", total_count
			except Exception as E:
				print "Inside Reviews Exceptions", E
				continue
		return result