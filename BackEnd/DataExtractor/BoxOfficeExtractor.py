import requests 
from BeautifulSoup import BeautifulSoup

class BoxOfficeExtractor:
	def __init__(self):
		a = None 

	def get_data(self, url, name):
		resp = requests.get(url)
		soup = BeautifulSoup(resp.text)
		doc = {}
		doc['name'] = name
		for table in soup.find('span', {'class' : 'text'}).findAll('table'):
			tab = table.tr.findAll('td')
			key = tab[0]
			val = tab[1]
			key = key.text
			val = val.text.replace("&#8377;","").replace("&nbsp;"," ")
			doc[key] = val 

		for tr in soup.find('table' , {'class' : 'rhtCol'}).findAll('tr'):
			tdz = tr.findAll('td')
			a = tdz[0].text.replace('&#8377;'," ").replace("&nbsp;", " ")
			val = a.split()[-1] 
			key = " ".join(a.split()[:-1])
			doc[key] = val
			key = a.split()[-1] 
			if len(tdz) > 1:
				b = tdz[1].text.replace('&#8377;'," ").replace("&nbsp;", " ")
				val = b.split()[-1] 
				key = " ".join(b.split()[:-1])
				doc[key] = val
			if "Overseas" in a:
				break
		return doc