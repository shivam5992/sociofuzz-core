import requests
from BeautifulSoup import BeautifulSoup

class BollylifeExtractor:
	def __init__(self, url):
		self.url = url
		return None 

	def extract_summary(self):
		resp = requests.get(self.url)
		soup = BeautifulSoup(resp.text)
		desc = soup.find('p', {'itemprop' : 'description'})
		return desc.text.encode('utf8').replace("Storyline:","")