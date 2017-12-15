import requests
from BeautifulSoup import BeautifulSoup

class TimesExtractor:
	def __init__(self, url):
		self.url = url 

	def fetch_text(self):
		texted = []
		url = self.url + "?tabtype=trivia"
		html = requests.get(url)
		source = html.text
		soup = BeautifulSoup(source)
		aaa = soup.findAll('span', {'class':'righttrivia'})
		for i in aaa:
			texted.append(i.text.strip())
		return texted

	def get_boxoffice(self):
		url = self.url + '?tabtype=box'
		html = requests.get(url)
		source = html.text
		soup = BeautifulSoup(source)
		aa = soup.findAll('tr')
		json1 = []
		for x in aa:
			json = []
			twos = x.findAll('td')
			if 'Day' in twos[0].text:
				json.append(twos[0].text)
				json.append(twos[1].text.replace("nett",""))
				json1.append(json)
			elif 'Total' in twos[0].text:
				json.append(twos[0].text)
				json.append(twos[1].text.replace("nett",""))
				json1.append(json)
		return json1

	def getgaana(self):
		html = requests.get(self.url)
		source = html.text
		soup = BeautifulSoup(source)
		alik = soup.find('a', {'class' : 'gaanabtn'})
		# print soup
		# print alik
		if alik:
			link = alik['href'].split("?ref=")[0] + "?ref=sociofuzz"
		else:
			link = None 
		return link

	def get_data(self):
		res = {}
		box = self.get_boxoffice()
		res['box'] = box
		trivias = self.fetch_text()
		res['trivias'] = trivias
		res['gaana'] = self.getgaana()
		return res