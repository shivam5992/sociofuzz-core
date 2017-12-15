import requests 
resp = requests.get('http://lyrics.javatpoint.com/lyricid/2227/dekhe-meri-aankhon-mein-jo')
print resp.text