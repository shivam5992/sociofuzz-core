from dbHandler import db, db1

for each in db.collection_names():
	if "Pop" in each and 'ABCD2' not in each: 
		print each
		curd = db[each].find({'dataType' : 'socialImage'})

		i = 0
		for val in curd:
			try:
				print i, curd.count()
				i += 1
				del val['url']
				db1[each].insert(val)
			except:
				continue
		# break
exit(0)

# from Levenshtein import ratio 


# for x in db['movie_jsons'].find():
# 	if 'tracks' in x['meta']['buff']:
# 		for a in x['meta']['buff']['tracks']:
# 			if 'lyrics' in a:
# 				ly = a['lyrics'].encode('utf8')
# 				print ly
			# else:
			# 	print a['track_name']


exit(0)

# for x in db['movie_jsons'].find():
	## CHANGE 1
	# if 'buff' in x:
	# 	for y in x['meta']['buff']['track']:
	# 		for dat in y['track_sec']:
	# 			for k,v in dat.iteritems():
	# 				y[k] = v
	# 		del y['track_sec']
	# 	print x['_id']	
	# 	db['movie_jsons'].update( {'_id' : x['_id'] } , { '$set' : {'meta.buff'  : x['meta']['buff']  }} ) 

	## CHANGE 2
	# if 'buff' in x:
	# 	if 'Uvaa' != x['_id']:

			# for each in x['meta']['buff']['track']:
			# 	track = each['track_name']
			# 	got = True
			# 	for song in x['meta']['buff']['gallery'][0]['Music']:
			# 		title = " ".join(song['title'].encode('utf8').split()[1:])
			# 		if track == title:
			# 			each['video'] = song['href'] 
			# 			got = True
			# 			break
			# 	if got == False:
			# 		print "!", track, x['_id']
			# print db['movie_jsons'].update( {'_id' : x['_id'] } , { '$set' :   {  'meta.buff'  : x['meta']['buff']  }   }   )


# Change 3 


custom = {
	'Super Man' : 'Main Toh Superman',
	'Micromax Singh is Bliing Rap' : 'The Singh Is Bliing Rap',
	'Tere Naina Maar' : 'Tera Naina Maar Hi Daalenge',
	"I'm Sorry Par Tumse Pyaar Ho Gaya" : "Tumse Pyar Ho Gaya",
	"Yeh Ishq" : "Ishq Da Maara",
	"Bihari Valentine" : "Bihari Valentine",
	"Guddu Ki Gun" : "Guddu Ki Gun (Title)",
	"Kolkata Qutub Minar" : "Kolkata Qutub Minar",
	"Surroor" : "Tera Suroor",
	"Icecream" : "Ice Cream Khaungi"
	}


for x in db['movie_jsons'].find():
	if x['meta']['lyrics_data'] == None:
		continue

	for each in x['meta']['buff']['track']:
		if 'Juke Box' in each['track_name']:
			continue
		try:
			tnam = str(each['track_name'].split("-")[0].strip().split("(")[0].strip().replace('Title Song', '')
				.replace("Lyrics","").strip()).encode('utf8') \
				.replace(" Mashup", "")

			got = False
			for lyr in x['meta']['lyrics_data']:
				if 'title' not in lyr:
					continue
				
				lyr['title'] = str(lyr['title'].split("(")[0].strip().replace('Title Song', '').replace("Lyrics","").strip()).encode('utf8')
				
				if lyr['title'] == tnam:
					got = True
					break
				elif ratio(lyr['title'], tnam) > 0.85:
					got = True 
					break

				elif lyr['title'][:15].startswith(tnam[:15]):
					got = True 
					break

				elif lyr['title'][:7].startswith(tnam[:7]):
					got = True 
					break

				elif lyr['title'].lower() in tnam.lower():
					got = True
					break

				elif tnam.lower() in lyr['title'].lower():
					got = True 
					break

			if got == True:
				lyrics = lyr['lyrics']
				each['lyrics'] = lyrics

			elif tnam in custom:
				for xx in x['meta']['lyrics_data']:
					xx['title'] = str(xx['title'].split("(")[0].strip().replace('Title Song', '').replace("Lyrics","").strip()).encode('utf8')
					if custom[tnam] == xx['title']:
						each['lyrics'] = xx['lyrics']

		except Exception as E:
			# print E 
			pass
	
	# _id = x['_id']
	# trk = x['meta']['buff']['track']
	# print _id
	# print db['movie_jsons'].update( {'_id' : _id } , { '$set' :   {  'meta.buff.tracks'  : trk  }})
	# break