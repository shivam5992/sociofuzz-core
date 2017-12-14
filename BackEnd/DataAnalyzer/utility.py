import ast, string, re
from bs4 import UnicodeDammit
from itertools import islice
from nltk.stem.wordnet import WordNetLemmatizer
import nltk
from nltk.corpus import stopwords
# import Levenshtein
import itertools	
import operator


lmtzr = WordNetLemmatizer()
exclude = string.punctuation


class utilities:
	def __init__(self):
		self.lmtzr = WordNetLemmatizer()
		self.exclude = string.punctuation
		self.stopwords = stopwords.words('english')
		self.tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
		return None

	def reform_json(self, line):
		line = line.replace(": true", ": True")
		line = line.replace(": false", ": False")
		line = line.replace(": null", ": None")
		return line

	def make_string_proper(self, line):
		line = ast.literal_eval(line)
		return line

	def punctuation_free(self, text):
		text = "".join([x for x in text if x not in self.exclude])
		return text

	def lemmatize_word(self, word):
		wrd = self.lmtzr.lemmatize(word,'v')
		if wrd == word:
			wrd = self.lmtzr.lemmatize(word,'n')
		return wrd

	def lemmatize_text(self, line):
		words = line.split()
		lemmed = []
		for wrd in words:
			wrd = self.punctuation_free(wrd)
			lem_words = self.lemmatize_word(wrd)
			lemmed.append(lem_words)
		lem_text = " ".join(lemmed)
		return lem_text

	def destrip(self, line):
		return ' ' + line + ' '

	def remove_spaces(self, text):
		text = text.replace("\n"," ")
		text = text.replace("\t"," ")
		text = text.replace("\r"," ")
		text = " ".join(text.split())
		return text

	def remove_encoded(sef, line):
		# line = line.encode('utf-8')
		line = str([line])
		patt = r"\\x[a-z0-9]{2}"
		line = re.sub(patt, "", line)
		line = UnicodeDammit(line)
		line = line.unicode_markup.encode('utf-8')
		line = line.lstrip("[u'").lstrip("['").rstrip("']")
		return line

	def generate_ngrams(self, inp, n=2, islist = False):
		if not islist:
			inp = inp.split()
		output = []
		for i in range(len(inp)-n+1):
			output.append(inp[i:i+n])
		return output

	def generate_chunks_list(self, lst, n):
	    for i in xrange(0, len(lst), n):
	        yield lst[i:i+n]

	def generate_chunks_dict(self, data, n):
	    it = iter(data)
	    for i in xrange(0, len(data), n):
	        yield {k:data[k] for k in islice(it, n)}

	def generate_tokens(self, text):
		tokens = nltk.word_tokenize(text)
		return tokens

	def digit_free(self, text):
		text_list = text.split()
		text_list = [x for x in text_list if not x.isdigit()]
		text = " ".join(text_list)
		return text

	def stopword_free(self, text):
		puncfree = self.punctuation_free(text)
		puncFree_words = puncfree.split()
		stopfree = [x for x in puncFree_words if x.lower() not in self.stopwords]
		stopfree_text = " ".join(stopfree)
		return stopfree_text

	def levenshtein_distance(self, s1, s2):
		return Levenshtein.distance(s1, s2)


	def split_attached_words(self, text):
		if len(text.split()) == 1 and not text.isupper():
			lis = re.findall('[A-Z][^A-Z]*', text)
			if len(lis) == 0:
				line = text
			else:
				line = " ".join(re.findall('[A-Z][^A-Z]*', text))
		else:
			newd = []
			for word in text.split():
				if not word.isupper():
					lis = re.findall('[A-Z][^A-Z]*', word)
					if len(lis) == 0:
						newd.append(word)
					else:
						newd.append(" ".join(lis))
				else:
					newd.append(word)
			line = " ".join(newd)
		return line


	def repeated_chars(self, text, level=2):
		text = ''.join(''.join(s)[:level] for _, s in itertools.groupby(text))
		return text

	def sort_counter(self, adict, freq = False, rvrse = True):
		top = sorted(adict.items(),key=lambda(k,v):(v,k), reverse = rvrse)
		if freq:
			top = top[:freq]
		return top

	def split_into_sentences(self, text):
		sents = tokenizer.tokenize(text)
		return sents

	def sort_dict_value(self, y):
		sx = sorted(y.items(), key = operator.itemgetter(1))
		return sx


utility = utilities()