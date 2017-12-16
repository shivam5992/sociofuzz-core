import csv

def getAuthKeysFromCSV(twitterAuthKeyFilePath):
	with open(twitterAuthKeyFilePath, 'rb') as csvfile:
		reader = csv.DictReader(csvfile)
		twitterAuthKeyList = []
		for row in reader:
			authKeyRow = (row['Consumer Key'], row['Consumer Secret'], row['Access Token'], row['Access Token Secret'])
			twitterAuthKeyList.append(authKeyRow)

		return twitterAuthKeyList

def cycle(iterable):
    saved = []
    for element in iterable:
        yield element
        saved.append(element)
    while saved:
        for element in saved:
              yield element