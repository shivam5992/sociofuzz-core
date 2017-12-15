import requests
from BeautifulSoup import BeautifulSoup
import requests
import subprocess


class LyricsBogiExtractor:
	def __init__(self, url):
		self.url = url     

	def get_lyrics(self):
		proc = subprocess.Popen(["curl", "-s", self.url], stdout=subprocess.PIPE)
		(out, err) = proc.communicate()
		soup1 = BeautifulSoup(out)
		link1 = soup1.find('ul' , {'class' : 'song_list'})
		links = link1.findAll('li')
		allsongs = []
		for each in links:
			hh = each.find('h3', {'class' : 'entry-title'})
			link = hh.a

			if link != -1:
				song_json = {}
				try:
					new_url = link['href']
					song_json['link'] = new_url

					proc = subprocess.Popen(["curl", "-s", new_url], stdout=subprocess.PIPE)
					(out, err) = proc.communicate()
					soup = BeautifulSoup(out)
					
					title = soup.title.text.split("|")[0].split("Lyrics")[0]
					song_json['title'] = title.split("-")[0].title().strip()
					lyrics = soup.find('div' , {'id' : 'lyricsDiv'})
					compl = ""
					for pp in lyrics.findAll('p'):
						dd = str(pp).replace("<br />","\n") 
						dd = dd.replace("<p>", " ").replace("\n ","\n")
						dd = dd.replace("</p>", "\n")
						compl +=  dd.strip()
						compl += "\n\n"
					lyrics_final = compl.split("<script")[0].strip()
					song_json['lyrics'] = lyrics_final
					allsongs.append(song_json)

				except Exception as E:
					print E 
					continue
		return allsongs

class LyricsExtractor:
	def __init__(self, url):
		self.url = url 

	def get_lyrics(self):
		html = requests.get(self.url)
		source = html.text
		soup1 = BeautifulSoup(source)
		link1 = soup1.find('ol')
		allsongs = []

		if link1 == None:
			song_json = {}
			detail = requests.get(self.url)
			detail_txt = detail.text
			soup = BeautifulSoup(detail_txt)

			
			title = soup.title.text.split("|")[0].split("Lyrics")[0]
			song_json['title'] = title.split("-")[0].title().strip()
			try:			
				lyric1 = str(soup.find('div',{'id':'lyric'}).find('p'))
				lyric1 = lyric1.replace("<p>","").replace("</p>","").replace("<br />","")
				song_json['lyrics'] = lyric1.strip()
				
				songinfo = soup.find('div',{'class':'songinfo'})
				content = str(songinfo).split("\n")

				if "Singers:" in content[0]:
					singers = content[0].split("Singers:")[1].replace("<br />","").strip()
					song_json['singer'] = singers
				elif "Singer:" in content[0]:
					singers = content[0].split("Singer:")[1].replace("<br />","").strip()
					song_json['singer'] = singers
				else:
					song_json['singer'] = ""

				for each in content[1:]:
					if ":" in each:
						each = each.split(":")
						song_json[each[0].replace(".","").replace(":","").replace("-","")] = ":".join(each[1:]).replace("<br />","").replace("-"," ").strip()
				allsongs.append(song_json)
			except:
				allsongs.append({})

		else:
			for each in link1:
				link = each.find('a')
				if link != -1:
					song_json = {}
					try:
						new_url = link['href']
						song_json['link'] = link['href']
						
						detail = requests.get(new_url)
						detail_txt = detail.text
						soup = BeautifulSoup(detail_txt)

						# songvid = soup.find('div', {'id' : 'lyrics-aside'}).iframe
						# if s['src']
						# song_json['video'] = songvid
						
						title = soup.title.text.split("|")[0].split("Lyrics")[0]
						song_json['title'] = title.split("-")[0].title().strip()
						
						lyric1 = str(soup.find('div',{'id':'lyric'}).find('p'))
						lyric1 = lyric1.replace("<p>","").replace("</p>","").replace("<br />","")
						song_json['lyrics'] = lyric1.strip()
						
						songinfo = soup.find('div',{'class':'songinfo'})
						content = str(songinfo).split("\n")

						if "Singers:" in content[0]:
							singers = content[0].split("Singers:")[1].replace("<br />","").strip()
							song_json['singer'] = singers
						elif "Singer:" in content[0]:
							singers = content[0].split("Singer:")[1].replace("<br />","").strip()
							song_json['singer'] = singers
						else:
							song_json['singer'] = ""

						for each in content[1:]:
							if ":" in each:
								each = each.split(":")
								song_json[each[0].replace(".","").replace(":","").replace("-","")] = ":".join(each[1:]).replace("<br />","").replace("-"," ").strip()
						allsongs.append(song_json)
					except:
						continue
		return allsongs




