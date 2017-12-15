from bs4 import BeautifulSoup
from wikipedia.wikipedia import Wikipedia
from wikipedia.wiki2plain import Wiki2Plain
import requests, datetime, re

class WikiExtractor:
	def __init__(self, movie_wiki_url):
		self.wiki = Wikipedia('en')
		self.movie_tag = movie_wiki_url.split("/")[-1].strip()
		self.url = movie_wiki_url.strip()
		self.months = ['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec']

		return None

	def text_extractor(self):
		try:
		    raw = self.wiki.article(self.movie_tag)
		    wiki2plain = Wiki2Plain(raw)
		    content = wiki2plain.text
		    short = content.split("==")[0].strip().split(". ")[0] + "."
		    return content, short
		
		except Exception as E:
			print str(E)
			return None

	def fix_date(self, date):
		if date == None:
			return "", ""
		mnth = ""
		for month in self.months:
			if month.title() in date:
				mnth = month.title()
				break
		date = date.lower().replace(mnth.lower(),"")
		for yr in re.findall("[\d]{4}", date):
			date = date.replace(yr,"")
		dat = ""
		for y in date.split():
			if y.isdigit():
				dat = y
				break
		return dat, mnth

	def info_extractor(self):
		res = requests.get(self.url)
		soup = BeautifulSoup(res.text.encode('utf-8'))
		info_tab = soup.find("table", { "class" : "infobox" })
		
		if info_tab == None:
			init = {}
			init['name'] = self.url.replace('https://en.wikipedia.org/wiki/','').replace("_"," ")
				
			poster = soup.find("div", { "class" : "thumbinner" })
			if poster != None:
				poster = poster.a.img['src']
				init['poster'] = "http:" + poster

		else:	
			rows = info_tab.findChildren(['tr'])
			init = {}
			flag = 0
			for row in rows:
				cells = row.findChildren(['th', 'td'])
				if len(cells) == 1 and flag == 0:
					init['name'] = cells[0].text.encode('utf-8').strip()
					flag = 1
				elif len(cells) == 2:
					title = cells[0].text.encode('utf-8')
					key = title.strip().replace("\n"," ")
					data = cells[1].text.encode('utf-8').decode('ascii','ignore')
					data = data.replace('\n',', ')
					
					if key == "Box office":
						data = data.split("(")[0].title() + "INR"
					if key == "Budget":
						data = data.split("(")[0].title() + "INR"
					if key == "Release dates":
						try:
							data = data.split("(")[1].split(")")[0]
						except:
							data = ""

					data = data.strip(",").strip()
					init[key] = data
			

			listed = []
			ol = soup.find("ol", attrs = {'class' : 'references'})
			if ol != None:
				for lix in ol.findAll('li'):
					date = ""
					date = lix.find('span', attrs = {'class' : 'reference-accessdate'})
					if date:
						date = date.text.replace("Retrieved", "").strip().replace(".  ","")
					link1 = lix.find('a', attrs = {'class' : 'external text'})
					title = ""
					link = ""
					if link1:
						link = link1['href']
						title = link1.text
					source = ""
					cn = lix.find('i')
					if cn:
						source = cn.text
					res = {}
					res['link'] = link
					res['title'] = title
					res['source'] = source
					dat, mnth = self.fix_date(date)
					res['date'] = dat, mnth
					listed.append(res)
				init['news_sources'] = listed
			else:
				init['news_sources'] = None

			if info_tab.find('a', {'class' : 'image'}) != None:
				init['poster'] = "http:" + info_tab.find('a', {'class' : 'image'}).img['src']
			else:
				init['poster'] = None

			if "Release dates" in init:
				if not init['Release dates'] == "":
					try:
						newdate = datetime.datetime.strptime(init['Release dates'], '%Y-%m-%d').strftime('%d/%m/%y')
						init['Release dates'] = newdate
					except:
						pass
		return init
