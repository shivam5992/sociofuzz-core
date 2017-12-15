import requests
from bs4 import BeautifulSoup
import re

class BuffExtractor:
	def __init__(self, url):
		self.url = url
		self.months = ['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec']
		return None
	
	def get_buff_data(self):
		final_info = {}
		new_resp = requests.get(self.url)
		new_soup  =  BeautifulSoup(new_resp.text.encode('utf-8'))
		link_tab  =  new_soup.find("p", { "class" : "info" })
		info = link_tab.text.encode('utf-8')
		basic_info = info.replace('\xc2\xa0','').strip().split('\xe2\x97\x8f')

		primary_info = new_soup.find("div",{"class": "primary"})
		desc = primary_info.find("div",{"itemprop":"description"})
		if desc != None:
			description = desc.text.encode('utf-8').strip()
		else:
			description = ""
		cast_info = primary_info.find("p",{"itemprop":"actor"})
		genre_info = primary_info.find_all("a",{"itemprop":"genre"})
		final_genre = ''
		for info in genre_info:
			new_info = info.text.encode('utf-8').strip()
			final_genre = final_genre+', '+new_info
		final_genre = final_genre.strip().strip(',').strip()
		try:
			cast = cast_info.text.encode('utf-8').strip().strip('Cast:').strip()
		except:
			cast = ""
		secondary_info = new_soup.find_all('div',{"class":"panel panel-default"})
		cast_Details = secondary_info[2].find_all('div',{"class":"col-xs-6 col-sm-4 credit"})
		charact_list = []
		for character in cast_Details:
			char_var = {}
			chrac = character.text.strip().replace('\n',' ')
			chrac_img = character.img['src']
			char_var['character_details'] = chrac
			char_var['character_img'] = chrac_img
			charact_list.append(char_var)
		
		if len(secondary_info) > 4:
			crew_Details = secondary_info[3].find_all('div',{"class":"row crew-group"})
			crew_info = {}
			for crew in crew_Details:
				role = crew.find('div',{"class":"col-xs-4 role"})
				role = role.text
				crew_name = crew.find('div',{"class":"col-xs-8 name"})

				crew_name_det = crew_name.text.replace('\n',', ').strip(',').strip()
				crew_info[role] = crew_name_det
		else:
			crew_info = {}

		if len(secondary_info) >= 5:
			tech_details = secondary_info[4].find_all('div',{"class":"row secondary-info"})
			tech_details_list = []
			for tech in tech_details:
				tech_point = {}
				tit = tech.find('div',{"class":"col-sm-4"}).text.encode('utf-8').strip()
				tit_det = tech.find('div',{"class":"col-sm-8"}).text.encode('utf-8').strip()
				tech_point[tit] = tit_det
				tech_details_list.append(tech_point)
		else:
			tech_details_list = []
		if len(secondary_info) >= 6:
			track_detail_info = []

			track_details = secondary_info[5].find_all('div',{"class": 'row track playable' })
			for track in track_details:
				track_info = {}
				track_duration = track.find('div',{"class":"pull-right"}).text.encode('utf-8').strip()
				track_name = track.find_all('div',{"class":"pull-left"})
				track_info['duration'] = track_duration
				for tracker in track_name:
					track_det = tracker.find('div',{"class":"track-detail"})
					if track_det is not None:
						track_name = track_det.text.encode('utf-8')
						track_info['track_name'] = track_name
				track_other_info = track.find_all('div',{"class":"details"})
				track_det_list = []
				for trac in track_other_info:
					other_info_list = trac.text.split('\n')
					for line in other_info_list:
						key = line[:line.find(':')]
						value = line[line.find(':')+1:].strip()
						track_info[key] = value
				track_detail_info.append(track_info)

			track_details = secondary_info[5].find_all('div',{"class": 'row track ' })
			for track in track_details:
				track_info = {}
				track_duration = track.find('div',{"class":"pull-right"}).text.encode('utf-8').strip()
				track_name = track.find_all('div',{"class":"pull-left"})
				track_info['duration'] = track_duration
				for tracker in track_name:
					track_det = tracker.find('div',{"class":"track-detail"})
					if track_det is not None:
						track_name = track_det.text.encode('utf-8')
						track_info['track_name'] = track_name
				track_other_info = track.find_all('div',{"class":"details"})
				track_det_list = []
				for trac in track_other_info:
					other_info_list = trac.text.split('\n')
					for line in other_info_list:
						key = line[:line.find(':')]
						value = line[line.find(':')+1:].strip()
						track_info[key] = value
				track_detail_info.append(track_info)
		else:
			track_detail_info = []

		if len(secondary_info) >= 7:
			fun_details = secondary_info[6].find_all('div',{"class":"row secondary-info"})
			fun_details_list = []
			for element in fun_details:
				fun_details_list.append(element.text.replace('\n',''))
		else:
			fun_details_list = []

		gallary_info = new_soup.find_all('div',{"data-component":"Gallery"})
		gallary_titles = new_soup.find_all('h5',{"class":"gallery-title"})
		gallery_title_text = []
		for each in gallary_titles:
			gallery_title_text.append(each.text.encode('utf-8').strip())

		if len(gallery_title_text) == 0:
			gallery_stuff = []
		else:
			gallery_stuff = []
			gallery_dict = {}
			trailer_link = []
			poster_link = []
			video_link = []
			audio_link = []
			image_link = []
			for i,line in enumerate(gallery_title_text):
				if line == "Trailers":
					sub = re.compile('trailer*')
					trailer_vedio = gallary_info[i].find_all('a',{"id":sub})
					for video in trailer_vedio:
						video_dict = {}
						video_img_link = video.img['src']
						vid_link = video['href']
						video_dict['video_link'] = vid_link
						video_dict['video_img_link'] = video_img_link
						try:
							video_dict['title'] = video.span.text
							if "trailer" in video.span.text.lower():
								final_info['trailer'] = video_dict
						except Exception as e:
							print e , self.url
							video_dict['title'] = "Trailer"
						trailer_link.append(video_dict)

				elif line == "Posters":
					sub = re.compile('poster*')
					poster = gallary_info[i].find_all('a',{"id":sub})
					for post in poster:
						poster_link.append(post['href'])

				elif line == "Videos":
					sub = re.compile('trailer*')
					vedio_files = gallary_info[i].find_all('a',{"id":sub})

					for video in vedio_files:
						video_dict = {}
						video_img_link = video.img['src']
						vid_link = video['href']
						video_dict['video_link'] = vid_link
						video_dict['video_img_link'] = video_img_link
						video_link.append(video_dict)

				elif line == "Music Clips":
					sub = re.compile('audio*')
					music_video = gallary_info[i].find_all('a',{"id":sub})
					
					for audio in music_video:
						ad = {}
						ad['title'] = audio.img['data-title']
						ad['href'] = audio['href']
						audio_link.append(ad)

				elif line  == "Images":
					sub = re.compile('poster*')
					image_list = gallary_info[i].find_all('a',{"id":sub})
					for image in image_list:
						image_link.append(image['href'])

			gallery_dict['Trailers'] = trailer_link
			gallery_dict['Posters'] = poster_link
			gallery_dict['Videos'] = video_link
			gallery_dict['Music'] = audio_link
			gallery_dict['Images'] = image_link
			gallery_stuff.append(gallery_dict)


		news_data = []
		for each in new_soup.find_all('div', {'class' : 'press-release'}):
			news = {}
			link = each.a['href']
			title = each.a.text.strip()
			txt = each.find('div', {'class' : 'meta'}).text
			source = txt.split("by")[1]
			date = txt.split("by")[0]
			news['link'] = link
			news['title'] = title
			dat, mnth = self.fix_date(date)
			news['date'] = dat, mnth 
			news['source'] = source
			news_data.append(news)
			
		final_info['news_data'] = news_data
		final_info['release_date'] = basic_info[0].strip()
		final_info['lang'] = basic_info[1].strip()
		final_info['running_time'] = basic_info[2].strip()
		final_info['description'] = description
		final_info['main_cast'] = cast
		final_info['genre'] = final_genre
		final_info['cast_details'] = charact_list
		final_info['crew_Details'] = crew_info
		final_info['tech'] = tech_details_list
		final_info['track'] = track_detail_info
		final_info['funstuff'] = fun_details_list
		final_info['gallery'] = gallery_stuff

		# Add Videos to Tracks 
		for each in final_info['track']:
			track1 = each['track_name']
			for song in final_info['gallery'][0]['Music']:
				title = " ".join(song['title'].encode('utf8').split()[1:])
				if track1 == title:
					each['video'] = song['href']



		return final_info

	def reviews(self):
		url = self.url + '/reviews/critics'
		resp = requests.get(url)
		soup = BeautifulSoup(resp.text)
		rest = []
		for each in soup.find_all('div', {'class' : 'pull-left headline'}):
			res = {}
			res['title'] = each.a.text
			res['link'] = each.a['href']
			txt = each.span.text.strip()
			if "," in txt:
				res['name'] = txt.split(",")[0]
				res['source'] = txt.split(",")[1]
			else:
				res['name'] = txt
			# rating 
			rat = each.findPrevious('div', {'class' : 'pull-left rating'})
			if rat:
				rat = rat.img['src']
		
			if rat != None:
				rat = rat.split("ratings/")[1].split('-')[0]
			else:
				rat = 2.5
			try:
				rat = float(rat)*2
			except:
				rat = 2.5
			res['rating'] = rat

			rest.append(res)
		return rest

	def fix_date(self, date):
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


url = 'http://www.moviebuff.com/bajirao-mastani'
bugg = BuffExtractor(url)
bugg.get_buff_data()