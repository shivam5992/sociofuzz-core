import requests, ast
from BeautifulSoup import BeautifulSoup
from dbHandler import get 

city_lookup = {'Roorkee': 'roorkee-uttarakhand-9pf', 'Thane': 'thane-maharashtra-1jl', 'Rohtak': 'rohtak-haryana-1f0', 'Nanded': 'nanded-maharashtra-1h4', 'Jalandhar': 'jalandhar-punjab-1ht', 'Muzaffarnagar': 'muzaffarnagar-uttar-pradesh-1gm', 'Mangaluru': 'mangaluru-karnataka-1gs', 'Shillong': 'shillong-meghalaya-1e1', 'Bhopal': 'bhopal-madhya-pradesh-19z', 'Kaithal': 'kaithal-haryana-1nv', 'Pathankot': 'pathankot-punjab-1h3', 'Zirakpur': 'zirakpur-punjab-1hc', 'Banswara': 'banswara-rajasthan-1ve', 'Noida': 'noida-uttar-pradesh-1hp', 'Seoni': 'seoni-madhya-pradesh-9pe', 'Lonavla': 'lonavla-maharashtra-27c', 'Samana': 'samana-punjab-8wg', 'Dhamtari': 'dhamtari-chhattisgarh-1a6', 'Mathura': 'mathura-uttar-pradesh-1n0', 'Chandrapur': 'chandrapur-maharashtra-18b', 'Hisar': 'hisar-haryana-26p', 'Khandwa': 'khandwa-madhya-pradesh-1gl', 'Ahmedabad': 'ahmedabad-gujarat-1ab', 'Varanasi': 'varanasi-uttar-pradesh-1an', 'Jalgaon Jamod': 'jalgaon-jamod-maharashtra-1o8', 'Haldia': 'haldia-west-bengal-1u3', 'Nagpur': 'nagpur-maharashtra-1hl', 'Gwalior': 'gwalior-madhya-pradesh-1lu', 'Saharanpur': 'saharanpur-uttar-pradesh-1sj', 'Port Blair': 'port-blair-andaman-and-nicobar-islands-1l2', 'Mohali': 'mohali-punjab-1ya', 'Hubballi': 'hubballi-karnataka-1ch', 'Ahmednagar': 'ahmednagar-maharashtra-1di', 'Bikaner': 'bikaner-rajasthan-1gt', 'Sangli': 'sangli-maharashtra-1al', 'Surat': 'surat-gujarat-1gj', 'Hoshiarpur': 'hoshiarpur-punjab-272', 'Bharuch': 'bharuch-gujarat-1oe', 'Bathinda': 'bathinda-punjab-1lw', 'Alwar': 'alwar-rajasthan-1my', 'Hamirpur': 'hamirpur-himachal-pradesh-1bx', 'Kanpur': 'kanpur-uttar-pradesh-1hj', 'Bhiwadi': 'bhiwadi-rajasthan-1lg', 'Khopoli': 'khopoli-maharashtra-2ui', 'Indapur': 'indapur-maharashtra-9pg', 'Jetpur': 'jetpur-gujarat-8fk', 'Bhilwara': 'bhilwara-rajasthan-1hv', 'Jharsuguda': 'jharsuguda-odisha-22y', 'Ujjain': 'ujjain-madhya-pradesh-1yb', 'Ramnagar': 'ramnagar-uttarakhand-34t', 'Champa': 'champa-chhattisgarh-3q0', 'Bengaluru': 'bengaluru-karnataka-18d', 'Kota': 'kota-rajasthan-1ha', 'Kalyan': 'kalyan-maharashtra-722', 'Sonipat': 'sonipat-haryana-1fg', 'Jind': 'jind-haryana-1zy', 'Durgapur': 'durgapur-west-bengal-1d2', 'Beed': 'beed-maharashtra-1dh', 'Ranchi': 'ranchi-jharkhand-1lo', 'Ganganagar': 'ganganagar-rajasthan-1h6', 'Kichha': 'kichha-uttarakhand-8g7', 'Agartala': 'agartala-tripura-20h', 'Lucknow': 'lucknow-uttar-pradesh-1az', 'Moga': 'moga-punjab-1wo', 'Pen': 'pen-maharashtra-1h9', 'Jamnagar': 'jamnagar-gujarat-1h8', 'Dungarpur': 'dungarpur-rajasthan-9pr', 'Jalpaiguri': 'jalpaiguri-west-bengal-1d1', 'Navsari': 'navsari-gujarat-1ms', 'Gurgaon': 'gurgaon-haryana-1hb', 'Ludhiana': 'ludhiana-punjab-1jr', 'Rajkot': 'rajkot-gujarat-1gw', 'Disa': 'disa-gujarat-8mk', 'Darjiling': 'darjiling-west-bengal-1od', 'Karnal': 'karnal-haryana-1nr', 'Amravati': 'amravati-maharashtra-1j9', 'Kurukshetra': 'kurukshetra-haryana-1mt', 'Meerut': 'meerut-uttar-pradesh-1cd', 'Chiplun': 'chiplun-maharashtra-1xj', 'Moradabad': 'moradabad-uttar-pradesh-1up', 'Banga': 'banga-punjab-26v', 'Barasat': 'barasat-west-bengal-1p3', 'Bijnor': 'bijnor-uttar-pradesh-26i', 'Siliguri': 'siliguri-west-bengal-1hx', 'Gandhinagar': 'gandhinagar-gujarat-8dz', 'Kolhapur': 'kolhapur-maharashtra-1e7', 'New Delhi': 'new-delhi-nct-18h', 'Delhi': 'new-delhi-nct-18h', 'Idar': 'idar-gujarat-1cg', 'Bhilai': 'bhilai-chhattisgarh-1mo', 'Vapi': 'vapi-gujarat-1h2', 'Gorakhpur': 'gorakhpur-uttar-pradesh-1uf', 'Haridwar': 'haridwar-uttarakhand-1ja', 'Ambegaon': 'ambegaon-maharashtra-8od', 'Petlad': 'petlad-gujarat-21r', 'Nashik': 'nashik-maharashtra-1gx', 'Anand': 'anand-gujarat-1hu', 'Kashipur': 'kashipur-uttarakhand-26s', 'Phaltan': 'phaltan-maharashtra-9p0', 'Ratlam': 'ratlam-madhya-pradesh-2ov', 'Asansol': 'asansol-west-bengal-1lp', 'Solapur': 'solapur-maharashtra-1gr', 'Kaushambi': 'kaushambi-uttar-pradesh-1y9', 'Vadodara': 'vadodara-gujarat-19w', 'Raigarh': 'raigarh-chhattisgarh-1zl', 'Ambala': 'ambala-haryana-1lv', 'Junagadh': 'junagadh-gujarat-1pd', 'Patna': 'patna-bihar-19y', 'Bareilly': 'bareilly-uttar-pradesh-1q9', 'Berhampore': 'berhampore-west-bengal-32k', 'Indore': 'indore-madhya-pradesh-189', 'Howrah': 'howrah-west-bengal-1o9', 'Mumbai': 'mumbai-maharashtra-182', 'Bhubaneshwar': 'bhubaneshwar-odisha-1o7', 'Barnala': 'barnala-punjab-4rg', 'Jagdalpur': 'jagdalpur-chhattisgarh-1jq', 'Allahabad': 'allahabad-uttar-pradesh-1hd', 'Aurangabad': 'aurangabad-maharashtra-1a7', 'Haldwani': 'haldwani-uttarakhand-21q', 'Abohar': 'abohar-punjab-9ok', 'Ankleshwar': 'ankleshwar-gujarat-1yo', 'Kolkata': 'kolkata-west-bengal-197', 'Panipat': 'panipat-haryana-1ls', 'Rishikesh': 'rishikesh-uttarakhand-1ze', 'Birbhum': 'birbhum-west-bengal-1j6', 'Betul': 'betul-madhya-pradesh-1pr', 'Ajmer': 'ajmer-rajasthan-1gp', 'Himatnagar': 'himatnagar-gujarat-1c9', 'Patiala': 'patiala-punjab-1ez', 'Lavasa': 'lavasa-maharashtra-9pq', 'Chhindwara': 'chhindwara-madhya-pradesh-1gn', 'Navi Mumbai': 'navi-mumbai-maharashtra-1uc', 'Silchar': 'silchar-assam-1mz', 'Greater Noida': 'greater-noida-uttar-pradesh-1gq', 'Panchkula': 'panchkula-haryana-1ob', 'Ghaziabad': 'ghaziabad-uttar-pradesh-1go', 'Parbhani': 'parbhani-maharashtra-1he', 'Dehradun': 'dehradun-uttarakhand-1hs', 'Beawar': 'beawar-rajasthan-1n1', 'Bhiwani': 'bhiwani-haryana-26r', 'Yavatmal': 'yavatmal-maharashtra-21t', 'Guwahati': 'guwahati-assam-1c2', 'Bidar': 'bidar-karnataka-1ka', 'Jodhpur': 'jodhpur-rajasthan-1ao', 'Bhavnagar': 'bhavnagar-gujarat-1ce', 'Sehore': 'sehore-madhya-pradesh-1sw', 'Goa': 'goa-goa-1jt', 'Pune': 'pune-maharashtra-18w', 'Raipur': 'raipur-chhattisgarh-1h5', 'Wardha': 'wardha-maharashtra-1hg', 'Burdwan': 'burdwan-west-bengal-1gi', 'Dhule': 'dhule-maharashtra-1h7', 'Manipal': 'manipal-karnataka-1oa', 'Jaipur': 'jaipur-rajasthan-1gu', 'Udaipur': 'udaipur-rajasthan-1dn', 'Korba': 'korba-chhattisgarh-1eb', 'Kotkapura': 'kotkapura-punjab-1ly', 'Malegaon': 'malegaon-maharashtra-1jm', 'Sikar': 'sikar-rajasthan-1hw', 'Hajipur': 'hajipur-bihar-8kc', 'Baddi': 'baddi-himachal-pradesh-26q', 'Baloda Bazar': 'baloda-bazar-chhattisgarh-97l', 'Jabalpur': 'jabalpur-madhya-pradesh-1lk', 'Faridabad': 'faridabad-haryana-1i5', 'Buxar': 'buxar-bihar-1la', 'Neemuch': 'neemuch-madhya-pradesh-1ux', 'Margao': 'margao-goa-1wp', 'Amritsar': 'amritsar-punjab-184', 'Baramati': 'baramati-maharashtra-1l8', 'Nawashahr': 'nawashahr-punjab-2zd', 'Bilaspur': 'bilaspur-chhattisgarh-1mu', 'Agra': 'agra-uttar-pradesh-1ho', 'Palanpur': 'palanpur-gujarat-1hm', 'Ranaghat': 'ranaghat-west-bengal-26u', 'Gulbarga': 'gulbarga-karnataka-1vf', 'Vasco Da Gama': 'vasco-da-gama-goa-28x', 'Valsad': 'valsad-gujarat-1jp', 'Akola': 'akola-maharashtra-1hf', 'Latur': 'latur-maharashtra-1hh', 'Balaghat': 'balaghat-madhya-pradesh-1uw', 'Durg': 'durg-chhattisgarh-1hn', 'Belagavi': 'belagavi-karnataka-1es', 'Ghazipur': 'ghazipur-uttar-pradesh-9bg', 'Panaji': 'panaji-goa-28z', 'Aligarh': 'aligarh-uttar-pradesh-1hr', 'Sambalpur': 'sambalpur-odisha-2ou', 'Adipur': 'adipur-gujarat-1uy', 'Boisar': 'boisar-maharashtra-1rp', 'Kawardha': 'kawardha-chhattisgarh-1li'} 

class ShowTimeExtractor:
	def __init__(self, city, buff_url):
		self.city = city
		self.buff_url = buff_url
		return None

	def get_times(self):
		if self.city in city_lookup:
			url_tag = city_lookup[self.city]
			url = self.buff_url + '/tickets/' + url_tag
			
			resp = requests.get(url) 
			soup = BeautifulSoup(resp.text)
			complete = []
			for theater in soup.findAll('div', {'class' : 'theater'}):
				row = {}
				name = theater.find('h3', {'class' : 'name'}).text

				looked = get.check_doc_exist('name', name, 'theaters')
				row['theater_data'] = looked

				times = []
				for time in theater.findAll('div', {'class' : 'day row'}):
					timed = {}
					day = time.find('h5', {'class' : 'col-md-4'}).text
					timings = [x.text for x in time.findAll('a')]
					timed[day] = timings
					times.append(timed)
				row['name'] = name
				row['times'] = times
				complete.append(row)
			return complete
		else:
			return None

	def json_to_html(self, theaters):
		html = []
		latlongs = []
		if theaters == None:
			return "No Data Found"
		for each in theaters:
			if 'phone' not in each['theater_data']:
				each['theater_data']['phone'] = "NA"

			ctime = ""
			for xx, yy in each['times'][0].iteritems():
				for tt in yy:
					ctime += """<span class="show-time">""" + tt + """</span>"""
			
			row = """<div class="row-card">
			<div class="stack-show ">
				<div class="theater-id col-md-5">
					<div class="theater-name">""" + each['name'] +  """ </div>
					<div class="theater-Info">
						<div class="row">
							<div class="col-md-1 col-sm-1 col-xs-1"><i class="fa fa-map-marker"></i></div> 
							<div class="col-md-10 col-sm-10 col-xs-10">""" + each['theater_data']['address']  + """</div>
						</div>
					</div>
					<div class="theater-Info">
						<div class="row">
							<div class="col-md-1 col-sm-1 col-xs-1"><i class="fa fa-phone"></i></div>
							<div class="col-md-10 col-sm-10 col-xs-10"><p>""" + each['theater_data']['phone'].replace("Phone:","").replace(",", "</p><p>") + """</p></div>
						</div>
					</div>
				</div>
				<div class="theater-times col-md-7">""" + ctime + """</div>
			</div>
		</div>
		"""
			# print row
			html.append(row)

			ll = each['theater_data']['ll']
			term = []
			term.append( ll.split(",")[0])
			term.append( ll.split(",")[1] )
			term.append(each['name'])
			latlongs.append(term)
			
		return "".join(html), latlongs



# a = ShowTimeExtractor('delhi', 'http://www.moviebuff.com/titli')
# t = a.get_times()
# print a.json_to_html(t)