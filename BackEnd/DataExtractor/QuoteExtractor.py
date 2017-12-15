from BeautifulSoup import BeautifulSoup
import requests
import string
punc = string.punctuation

class QuoteExtractor:
	def __init__(self,url):
		self.url = url

	def get_quotes(self):
		dialogs = []
		html = requests.get(self.url)
		source = html.text
		soup = BeautifulSoup(source)
		dialog_html = soup.findAll('div', {'class':'dialogueBoxHindiRight'})
		for each in dialog_html:
			text = each.text
			text = text.strip()
			if text[-1] in punc:
				text = "".join(text[:-1])
			text = text.replace(" ... "," ...... ") + " !!!"
			dialogs.append(text)
		return dialogs
