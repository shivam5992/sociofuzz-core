from pattern.web import Twitter
import json

def twitter_pattern():
    twitter = Twitter()
    stream = twitter.stream('YaaraSillySilly')
    
    list_ids = []
    while True:
        stream.update()
        try:
            if len(list_ids) > 1:
                for ids in list_ids:
                    if stream[-1].id == ids:
                        flag = 1
                        break
                    else:
                        flag = 0
                if flag == 0:
                    tweet = {}
                    tweet['id'] = stream[-1].id
                    tweet['author'] = stream[-1].author
                    tweet['text'] = stream[-1].text
                    tweet['date'] = stream[-1].date
                    list_ids.append(stream[-1].id)
                    print str(tweet) + ','
            else:
                list_ids.append(stream[-1].id)
        except Exception as e:
            print e 
            pass

twitter_pattern()