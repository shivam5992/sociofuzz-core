from DataAnalyzer.utility import utility

class MatchingArchitecture:

	def __init__(self):
		return None

	def exact_match(self, keyword, text):
		text = utility.punctuation_free(text)
		text = utility.remove_spaces(text)
		text = utility.destrip(text)
		text = text.lower()
		keyword = utility.destrip(keyword)	
		keyword = keyword.lower()
		if keyword in text:
			return True
		else:
			return False
			
	def lemmatize_match(self, keyword, text):
		text = utility.remove_spaces(text)
		text = utility.punctuation_free(text)
		text = text.lower()
		text = utility.lemmatize_text(text)
		keyword = keyword.lower()
		keyword = utility.lemmatize_word(keyword)
		matched_status = self.exact_match(keyword, text)
		return matched_status
		

	def order_match(self, keyword, text, lemmatizeCheck = True):
		text = utility.punctuation_free(text)
		text = text.lower().strip()
		
		if lemmatizeCheck:
			text = utility.lemmatize_text(text)
			keyword = utility.lemmatize_word(keyword)

		text = utility.destrip(text)
		text_list = text.split()

		keyword = keyword.lower().strip()
		keyword = utility.destrip(keyword)
		keyword_list = keyword.split()

		count = 0
		for kwrd in keyword_list:
			if len(kwrd) < 1:
				continue
			if kwrd in text:
				count += 1

		order = float(count)/len(keyword_list)*100
		return order

match = MatchingArchitecture()