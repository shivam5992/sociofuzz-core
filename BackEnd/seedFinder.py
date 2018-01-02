from google import search

sources = ['wiki', 'moviebuff','filmyquotes','reviewschview','lyricsmint','imdb','timesofindia', 'wiki']

moviename = 'Charlie Key Chakkar Mein'
for source in sources:
	query = moviename + " " + source
	for url in search(query, stop=4):
		if source in url:
			print url
			break