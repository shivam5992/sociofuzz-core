import requests
from BeautifulSoup import BeautifulSoup

class ImdbExtractor:
	def __init__(self, url):
		self.url = url 

	def fetch_text(self, url):
		html = requests.get(url)
		source = html.text
		soup = BeautifulSoup(source)
		relt = soup.findAll('div', {'class':'sodatext'})
		texts = [x.text.strip() for x in relt]
		return texts

	def get_trivias(self):
		possibles = ['trivia', 'goofs']
		texted = []
		for each in possibles:
			if self.url.endswith("/"):
				url = self.url + each
			else:
				url = self.url + "/" + each
			texted.extend(self.fetch_text(url))
		return texted
	
	def get_external_reviews(self):
		url = self.url + "/externalreviews"
		html = requests.get(url)
		source = html.text
		soup = BeautifulSoup(source)

		result = []
		for each in soup.find('ul', {'class' : 'simpleList'}).findAll('a'):
			if each:
				res = {}
				res['link'] = "http://www.imdb.com/" + each['href']
				if "[" in each.text:
					source = each.text.split("[")[0]
					name = each.text.split("[")[1]
				elif "(" in each.text:
					source = each.text.split("(")[0]
					name = each.text.split("(")[1]
				else:
					source = each.text 
					name = ""
				res['source'] = source
				res['name'] = name
				result.append(res)
		return result

	def get_rating(self):
		soup = BeautifulSoup(requests.get(self.url).text)
		try:
			return float(soup.find("div",{ 'class' : "titlePageSprite star-box-giga-star"}).text.strip())
		except Exception as E:
			try:
				return float(soup.find("span",{ 'class' : "rating"}).text.strip().replace('"','').replace("/10",""))
			except Exception as E1:
				print E1
				return 0


	def get_data(self):
		res = {}
		res['rating'] = self.get_rating()
		res['trivias'] = self.get_trivias()
		# can also get reviews
		return res
