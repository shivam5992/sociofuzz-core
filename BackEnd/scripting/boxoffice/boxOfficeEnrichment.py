import requests 
from BeautifulSoup import BeautifulSoup

def getBoxOfficeCollection(name, url):
	response = {'movie' : name}
	resp = requests.get(url)
	soup = BeautifulSoup(resp.text)
	dv = soup.find('div' , {'id' : 'box-office'})
	if dv != None:
		prev = dv.findPrevious('div')
		trz = prev.table.tbody.findAll('tr')
		if len(trz) > 1:
			total = trz[1].findAll('th')[1].text
			response['total'] = total
			budget = trz[2].findAll('th')[1].text
			response['budget'] = budget
	days = {}
	table = soup.find('div' , {'id' : 'Weekly'})
	if table != None:
		tab = table.table.tbody
		if len(tab) > 0:
			for tr in tab.findAll('tr')[1:]:
				head = tr.findAll('th')
				if len(head) > 0:
					key = head[0].text
					val = head[1].text
					days[key] = val
	response['days'] = days
	return response


def getSeeds(url):
	resp = requests.get(url)
	soup = BeautifulSoup(resp.text)
	for tr in soup.find('table' , {'class' : 'bordered'}).findAll('a'):
		print tr.text + "," + tr['href']


def parseBoxOffice(url, name, fout):
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
	fout.write(str(doc) + "\n")


fout = open("data2.txt", 'w')
for i, line in enumerate(open("bb.txt").read().split("\n")):
	name = line.split(",")[0].strip() 
	url = line.split(",")[1].strip()
	print name 
	parseBoxOffice(url, name, fout)