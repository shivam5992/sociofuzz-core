from appDBHandler import get, update, db, fs
from ShowTimeExtractor import ShowTimeExtractor
from time import strftime
from getNews import getNews, getMovieVideos
from random import shuffle
from datetime import timedelta
from flask import make_response, current_app, Flask, render_template, jsonify, request, session, redirect, url_for
from functools import update_wrapper
import ast
from flask_mobility import Mobility
from collections import Counter 
import math
from flask_mobility.decorators import mobile_template
from flask_oauth import OAuth
app = Flask(__name__)
Mobility(app)
app.secret_key = '73767986698979858379786577'

FACEBOOK_APP_ID = '1538336346491255'
FACEBOOK_APP_SECRET = '8e275b0a77d130cc19488f17f3a27ca4'

oauth = OAuth()

facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=FACEBOOK_APP_ID,
    consumer_secret=FACEBOOK_APP_SECRET,
    request_token_params={'scope': ('email, ')}
)

@facebook.tokengetter
def get_facebook_token():
    return session.get('facebook_token')

def pop_login_session():
    session.pop('logged_in', None)
    session.pop('facebook_token', None)

@app.route("/facebook_login")
def facebook_login():
    return facebook.authorize(callback=url_for('facebook_authorized',
        next=request.args.get('next'), _external=True))

@app.route("/facebook_authorized")
@facebook.authorized_handler
def facebook_authorized(resp):
	next_url = request.args.get('next') or url_for('index')
	if resp is None or 'access_token' not in resp:
		return redirect(next_url)

	session['logged_in'] = True
	session['facebook_token'] = (resp['access_token'], '')

	data = facebook.get('/me?fields=name,picture,email,age_range,bio,birthday,gender,location').data

# devices,education,email,favorite_athletes,favorite_teams,first_name,hometown,inspirational_people,install_type,installed,interested_in,
# is_shared_login,is_verified,languages,last_name,link,location,locale,meeting_for,middle_name,
# name_format,payment_pricepoints,test_group,political,relationship_status,religion,security_settings,significant_other,sports,quotes,third_party_id,
# timezone,tokenbb_for_business,updated_time,shared_login_upgrade_required_by,verified,
# video_upload_limits,viewer_can_send_gift,website,work,public_key,cover ').data
	if 'id' in data:
		data['_id'] = data.pop('id')
		session['name'] = data['name']
		try:
			session['image'] = data['picture']['data']['url']
		except:
			session['image'] = ""
		try:
			db['RegisteredUsers'].insert( data )
		except:
			pass

	return redirect(next_url)

@app.route("/logout")
def logout():
    pop_login_session()
    return redirect(url_for('index'))






def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers
            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            h['Access-Control-Allow-Credentials'] = 'true'
            h['Access-Control-Allow-Headers'] = \
                "Origin, X-Requested-With, Content-Type, Accept, Authorization"
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator


from urlparse import urlparse, urlunparse
@app.before_request
def redirect_nonwww():
    """Redirect non-www requests to www."""
    urlparts = urlparse(request.url)
    if urlparts.netloc == 'sociofuzz.com':
        urlparts_list = list(urlparts)
        urlparts_list[1] = 'www.sociofuzz.com'
        return redirect(urlunparse(urlparts_list), code=301)




''' APIs for Apps '''
@app.route("/app/about/<moviename>")
@crossdomain(origin='*')
def AboutMovie(moviename):
	moviejson = db['movie_jsons'].find_one({'_id' : moviename}, 
						{ '_id' : 1, 'name' : 1, 'MovieId' : 1, 
						 'actsimg' : 1, 'box' : 1, 'meta.buff.description' : 1, 'meta.buff.genre' : 1, 
						 'meta.buff.lang' : 1, 'meta.buff.release_date' : 1, 'meta.buff.running_time' : 1,
						 'meta.wiki.name' : 1, 'meta.wiki.Directed by' : 1,'meta.wiki.Music by' : 1,
						 'meta.wiki.Produced by' : 1, 'meta.wiki.Written by' : 1, 'meta.buff.gallery' :1  })
	moviejson['poster'] = moviejson['meta']['buff']['gallery'][0]['Posters'][0].replace("?w=1000","?w=200")
	moviejson['trailerId'] = moviejson['meta']['buff']['gallery'][0]['Trailers'][0]['video_link'].split("watch?v=")[1]

	moviejson['meta']['wiki']['Produced by'] = [x.strip() for x in "".join(moviejson['meta']['wiki']['Produced by']).split(",") if len(x)>1]
	moviejson['meta']['wiki']['Written by'] = [x.strip() for x in "".join(moviejson['meta']['wiki']['Produced by']).split(",") if len(x)>1]
	moviejson['meta']['wiki']['Music by'] = [x.strip() for x in "".join(moviejson['meta']['wiki']['Produced by']).split(",") if len(x)>1]

	del moviejson['meta']['buff']['gallery']
	return jsonify(**{ 'data' : moviejson })


@app.route("/app/movie/<moviename>")
@crossdomain(origin='*')
def MobleMovie(moviename):
	moviejson = db['movie_jsons'].find_one({'_id' : moviename}, {'_id' : 1, 'MovieId' : 1, 'meta.wiki.name' : 1,
								'stars' : 1, 'rank' : 1, 'meta.buff.gallery' : 1, 'analyzed.total_tweets' : 1,
								'analyzed.total_users' : 1, 'reviews_data' : 1, 'buffimg' : 1, 'wikiimg' :1	})

	moviejson['poster'] = moviejson['meta']['buff']['gallery'][0]['Posters'][0].replace("?w=1000","?w=200")
	del moviejson['meta']['buff']['gallery'][0]['Posters']
	del moviejson['meta']['buff']['gallery'][0]['Images']
	del moviejson['meta']['buff']['gallery'][0]['Music']
	del moviejson['meta']['buff']['gallery'][0]['Videos']

	moviejson['reviews_data_len'] = len(moviejson['reviews_data'])
	del moviejson['reviews_data']

	moviejson['stars'][0] = moviejson['stars'][0].replace("fa fa-star-o fvstar", "ion-ios-star-outline").replace("fa fa-star-half-o fvstar", "ion-ios-star-half") \
	.replace("fa fa-star-half-o frstar", "ion-ios-star-half") \
		.replace("fa fa-star-half-o tstar", "ion-ios-star-half") \
		.replace("fa fa-star-half-o sstar", "ion-ios-star-half") \
		.replace("fa fa-star-half-o fstar", "ion-ios-star-half") \
		.replace("fa fa-star fvstar", "ion-ios-star") \
		.replace("fa fa-star frstar", "ion-ios-star") \
		.replace("fa fa-star tstar", "ion-ios-star") \
		.replace("fa fa-star sstar", "ion-ios-star") \
		.replace("fa fa-star fstar", "ion-ios-star")   

	return jsonify(**{'data' : moviejson})

@app.route("/app/analyzed/<moviename>")
@crossdomain(origin='*')
def GetAnalyzed(moviename):
	analzed = db['movie_jsons'].find_one({'_id' : moviename}, {'analyzed' : 1})
	return jsonify(**{'data' : analzed})

@app.route("/app/trivias/<moviename>")
@crossdomain(origin='*')
def GetTrivias(moviename):
	trivias = db.movie_jsons.find_one({ '_id' : moviename }, {'meta.trivias' : 1 , 'meta.buff.track' :1})
	
	data1 = []
	for x in trivias['meta']['buff']['track']:
		if 'Juke Box' in x['track_name']:
			continue

		got = False 
		for each in x['track_sec']:
			if 'Playback Singer' in each:
				x['singer'] = each 
				got = True
		if got == False:
			x['singer'] = "" 
		data1.append(x)

	return jsonify(**{'data' : trivias['meta']['trivias']  , 'music' : data1 })

@app.route("/appcontent/<category>/<moviename>", methods = ['GET','POST'])
@crossdomain(origin='*')
def GetContent(category, moviename):
	if category == 'news':
		content = get.get_next_news(moviename)
		contentNews = []
		for each in content:
			if type(each['title']) == list:
				each['title'] = each['title'][0]
			if len(each['title'].split()) > 1:
				contentNews.append(each)

			del each['desc_text']
			del each['meta_description']
			del each['text']
			del each['count']
			del each['date']
			del each['source']

		return jsonify(**{'data' : contentNews})
	else:
		content = get.get_next_reviews(moviename)
		for each in content:
			val = db.CriticMaster.find_one({'_id' : each['name']})
			if val:
				if len(val['src']) < 1:
					each['newSrc'] = "img/null.jpg"
				else:
					each['newSrc'] = val['src']
			else:
				each['newSrc'] = "img/null.jpg"
			if 'rating' not in each:
				each['rating'] = str("")
			else:
				if each['rating'] < 3:
					each['color'] = "#DD0000"
				elif each['rating'] >= 3 and each['rating'] < 5:
					each['color'] = "#EEAB00"
				elif each['rating'] >= 5 and each['rating'] < 6:
					each['color'] = "#00DD00"
				else:
					each['color'] = "#499914"
				if "." not in str(each['rating']):
					each['rating'] = str(each['rating']).strip() + ".0"
			
			del each['desc_text']
			del each['meta_description']
			del each['neg']
			del each['pos']
			del each['text']
			del each['count']
			del each['tot']
		return jsonify(**{'data' : content})


def trimmoviejson(mlst, limit):
	for x in range(0,limit):
		mlst[0]['projection'][x]['stars'][0] = mlst[0]['projection'][x]['stars'][0].replace("fa fa-star-o fvstar", "ion-ios-star-outline").replace("fa fa-star-half-o fvstar", "ion-ios-star-half") \
		.replace("fa fa-star-half-o frstar", "ion-ios-star-half") \
		.replace("fa fa-star-half-o tstar", "ion-ios-star-half") \
		.replace("fa fa-star-half-o sstar", "ion-ios-star-half") \
		.replace("fa fa-star-half-o fstar", "ion-ios-star-half") \
		.replace("fa fa-star fvstar", "ion-ios-star") \
		.replace("fa fa-star frstar", "ion-ios-star") \
		.replace("fa fa-star tstar", "ion-ios-star") \
		.replace("fa fa-star sstar", "ion-ios-star") \
		.replace("fa fa-star fstar", "ion-ios-star")

		try:
			del mlst[0]['projection'][x]['MovieId']
			del mlst[0]['projection'][x]['date']
			# del mlst[0]['projection'][x]['wikiimg']
			# del mlst[0]['projection'][x]['buffimg']
			del mlst[0]['projection'][x]['trailer'][0]['Images']
			del mlst[0]['projection'][x]['trailer'][0]['Music']
			del mlst[0]['projection'][x]['trailer'][0]['Posters']
			del mlst[0]['projection'][x]['trailer'][0]['Videos']
		except Exception as E:
			print E 
			pass
	return mlst


@app.route("/appindex")
@crossdomain(origin='*')
def appIndes():
	limit = 6
	upcoming = get.get_upcoming_movies(limit)
	upcoming = trimmoviejson(upcoming, limit)

	alltime = get.get_top_movies(limit)
	alltime = trimmoviejson(alltime, limit)
	
	return jsonify(**{ 'upcoming' : upcoming, 'alltime' : alltime })

# FOR WEB AND APP BOTH
@app.route("/getTweets/<moviename>/<limit>", methods = ['GET','POST'])
@crossdomain(origin='*')
def getTweets(moviename, limit):
	res = get.get_movie_content(moviename + '_ParsedPopTweets', 'tweet')
	res = res[0]
	p = res['pos'][:20]
	n = res['neg'][:20]
	pop = res['pop'][:20]
	p, n = update.convert_tweets(p, n)
	pop = update.parse_sect_tweet(pop, "1", "x")
	return jsonify(**{'pos' : p, 'neg': n, 'pop' : pop})

''' APIs for WEB '''
@app.route("/movieold/<moviename>")
def movie(moviename):
	moviejson = get.get_latest_movie_json(moviename)
	
	# Remove these permenantly from data
	if 'imgelem' in moviejson:
		del moviejson['imgelem']	
	if 'box' in moviejson:
		del moviejson['box']

	upcoming = get.get_upcoming_movies(8)
	alltime = get.get_top_movies(8)
	total = get.get_total_insights()
	showTime = update.IsShowable(moviename)
	
	''' Add this section before extracting new data '''
	if moviejson['meta']['lyrics_data'] != None:
		for sing in moviejson['meta']['lyrics_data']:
			if 'singer' in sing and ">" in sing['singer']:
				sing['singer'] = sing['singer'].split(">")[1].replace("</a","")
			if 'singer' in sing:
				sing['singer'] = sing['singer'].replace('lyricsmint.com','').replace('&amp;','&')

	shuffle(moviejson['meta']['trivias'])
	a, b, acts = get.getImagesFromGrid(moviename)
	moviejson['percent'] = get.getPercent(moviejson['rank'])

	moviejson['boxoffice'] = get.getBoxOfficeDetails(moviename)
	if moviejson['boxoffice'] != None:
		fd = get.getBoxPercent(moviename, 'First Day')
		fwd = get.getBoxPercent(moviename, 'First Weekend')
		fw = get.getBoxPercent(moviename, 'First Week')

		if fd != None:
			fd = int(fd)

		if fw != None:
			fw = int(fw)
		
		if fwd != None:
			fwd = int(fwd)

		moviejson['boxoffice']['betterday'] = fd
		moviejson['boxoffice']['betterweekend'] = fwd
		moviejson['boxoffice']['betterweek'] = fw

		if 'day_fix' not in moviejson['boxoffice']:
			moviejson['boxoffice'] = None

	# critic_data = moviejson['reviews_data']
	# avg = float(sum([x['rating'] for x in critic_data]))/len(critic_data) 
	# pos = len([x for x in critic_data if x['rating'] >= 6.5])
	# neg = len([x for x in critic_data if x['rating'] < 6.5])	
	# calls = dict(Counter([math.floor(x['rating']) for x in critic_data]))
	# callslist = []
	# for k,v in calls.iteritems():
	# 	callslist.append({ 'letter' : k , 'frequency' : v})

	# moviejson['critic'] = {}
	# moviejson['critic']['average'] = avg
	# moviejson['critic']['total'] = len(critic_data)
	# moviejson['critic']['pos'] = pos
	# moviejson['critic']['neg'] = neg
	# moviejson['critic']['calls'] = callslist
	indian_cities = ", ".join( [str(c).title() for c in get.get_indian_cities()] )
	
	return render_template("moviePage.html", 
						movie = moviejson, 
						alltime = alltime,
						upcoming = upcoming,
						actsimg = acts ,
						total = total,
						showTime = showTime,
						cities = indian_cities
						)

@app.route("/get_pics/<moviename>", methods = ['GET','POST'])
@crossdomain(origin='*')
def get_pics(moviename):
	media = get.get_media_api(moviename)
	return jsonify(**{'data' : media})

@app.route("/getMoviesNews", methods = ['GET', 'POST'])
@crossdomain(origin='*')
def getMoviesNews():
	news = news.getNews()
	return jsonify(**{'data' : news})

@app.route("/getmovienames/<tag>", methods = ['GET', 'POST'])
@crossdomain(origin='*')
def getmovienames1(tag):
	res = get.get_movienames(tag)
	htmldata = update.get_movie_cards(res)
	return jsonify(**{'data' : htmldata})

@app.route("/get_users/<moviename>/<limitimg>", methods = ['GET','POST'])
@crossdomain(origin='*')
def get_users(moviename, limitimg):
	limit = int(limitimg)
	imgs = get.get_users_api(moviename, limit)
	inf = get.get_infulencer_api(moviename)
	return jsonify(**{'img' : imgs, 'inf': inf})


def colorTweets(this):
	ignore = ['starring', 'critic', 'phantom', 'talking', 'bumper', 'torrent']
	for x in this:	
		txt = []
		try:
			for wrd in x['text'].split():
				if wrd.lower() not in ignore:
					if wrd in x['positive_words']:
						wrd = "<font color='#7CB02E'>"+wrd+"</font>"
					if wrd in x['negative_words']:
						wrd = "<font color='#DE4343'>"+wrd+"</font>"
				wrd = wrd.replace(".@"," @")
				wrd = wrd.replace(".http"," http")
				if wrd.startswith('RT'):
					continue
				if wrd.startswith("http"):
					wrd = "<a href='"+wrd+"' target='_blank'>"+wrd+"</a>"
					continue
				elif wrd.startswith("@"):
					wrd = "<font color='#65BEDB'><a href='http://www.twitter.com/" + wrd.replace("@","") + "' target='_blank'>"+wrd+"</a></font>"
				elif wrd.startswith("#"):
					wrd = "<font color='#65BEDB' style='font-weight:600'><a href='#'>"+wrd+"</a></font>"
				txt.append(wrd)
		except:
			continue
		x['text'] = " ".join(txt)

@app.route("/get/<category>/<moviename>/<index>", methods = ['GET','POST'])
@crossdomain(origin='*')
def get_content(category, moviename, index):
	if category == 'news':
		data = db['NewsMaster'].find({'movie' : moviename})
		if data.count() == 0:
			content = get.get_next_news(moviename)
			html_data = update.convert_news(content)
			return jsonify(**{'data' : html_data})
		else:
			data = db['NewsMaster'].find({'movie' : moviename})
			data = [c for c in data]
			html_data = update.convert_new_news(data, moviename)
			return jsonify(**{'data' : html_data})

	elif category == 'image':
		index = int(index) - 1
		limit = 24
		data = get.get_movie_content(moviename + '_ParsedPopTweets', 'socialImage')
		data = [x for x in data]
		data = data[index*limit:index*limit+limit]
		html_data = update.convert_social_images(data)
		return jsonify(**{'data' : html_data})

	else:
		index = int(index) - 1
		limit = 100
		content = get.get_next_reviews(moviename)
		for x in content:
			val = db.CriticMaster.find_one({'_id' : x['name'].strip() })
			val1 = db.CriticMaster.find_one({'_id' : x['source'].strip() })
			if val != None and len(val['src'].strip()) > 1 and not str(val['src']).endswith("base64"):
				x['newSrc'] = val['src']
			elif val1 != None and len(val1['src'].strip()) > 1:
				x['newSrc'] = val1['src']
			else:
				x['newSrc'] = "../static/images/null.jpg"
		data = content[index*limit:index*limit+limit]
		html_data, mobile_data = update.convert_reviews(data)
		return jsonify(**{'data' : html_data, 'mobile' : mobile_data})


@app.route("/getAllMovies")
@crossdomain(origin='*')
def allmovies():
	allmovies = get.get_allmovies_mobile_movies()
	return jsonify(**{ 'data' : allmovies })


@app.route("/movies")
@crossdomain(origin='*')
def collection():
	total = get.get_total_insights()
	return render_template("movies.html", total = total)

@app.route("/about")
def about():
	total = get.get_total_insights()
	return render_template("about.html", total = total)

@app.route("/blog")
def blog():
	posts = get.getAllBlogs()
	return render_template("blogIndex.html", posts = posts)

@app.route("/blogs/<post>")
@crossdomain(origin='*')
def blogpost(post):
	blog = get.getBlogPost(post)
	posts = get.getAllBlogs()
	return render_template("blogPage.html" , blog = blog, posts = posts)

@app.route("/headerSearch", methods = ['GET','POST'])
def header():
	header = get.getSearchElements()
	return jsonify(**{'head' : header})

# @app.route('/')
# def hello():
#     return redirect("http://www.example.com", code=302)

@app.route("/")
@mobile_template('{mobile/}index.html')
def index(template):
	upcoming = get.get_upcoming_movies(5)
	queries = []
	for x in upcoming[0]['projection'][:2]:
		qur = x['name'] + " " + "bollywood"
		qur = qur.replace(" ","+")
		queries.append(qur)
	# news = getNews(queries)
	posts = get.getAllBlogs()
	alltime = get.get_top_movies(5)
	about = get.getAboutGraphData()
	about = str(about).replace('"',"'")
	total = get.get_total_insights()

	trailers = db['HomeContent'].find({'type' : 'trailer'})
	trailers = [c for c in trailers][-8:]
	
	return render_template(template, 
							trailers_data = trailers,
							upcoming = upcoming, 
							alltime = alltime,
							posts = posts ,
							about = about ,
							# news = news,
							total = total
							)

@app.route("/terms")
def terms():
	total = get.get_total_insights()
	return render_template("terms.html", total = total)

@app.route("/bap")
def bap():
	total = get.get_total_insights()
	return render_template("bap.html", total = total)

@app.route("/searchTimes", methods = ['GET','POST'])
def get_time():
	if request.method == 'POST':
		city = request.form['city']
		movie = request.form['moviename']
		metadata = get.check_doc_exist('Movie Name', movie ,'moviemeta')
		buff_url = metadata['BuffUrl']
		time = ShowTimeExtractor(city.title(), buff_url)
		timejson = time.get_times()
		
		if timejson == None:
			time_html = -1
			latlong = -1
		else:	
			time_html, latlong = time.json_to_html(timejson)
		data_ret = []
		data_ret.append(time_html)
		data_ret.append(latlong)
		return jsonify(**{ 'data' : data_ret })
	return jsonify(**{ 'data' : 'None' })




''' APIs for WEB '''
@app.route("/trend/<trendname>")
def trend(trendname):
	trendjson = get.get_latest_movie_json(trendname, isTrend = True)
	
	newsdata = db['NewsMaster'].find({'movie' : trendname})
	
	if newsdata != None:
		newsdata = [c for c in newsdata]
		total = get.get_total_insights()
		trendjson['news'] = newsdata 
	else:
		trendjson['news'] = None

	return render_template("trendPage.html", 
						trend = trendjson, 
						total = total,
						)


''' APIs for WEB '''
@app.route("/movie/<moviename>")
@app.route("/movies/<moviename>")
def movie1(moviename):
	moviejson = db['movie_jsons_1'].find_one({'_id' : moviename}, {'reviews_data' : 0})
	upcoming = get.get_upcoming_movies(8)
	alltime = get.get_top_movies(8)
	total = get.get_total_insights()
	showTime = update.IsShowable(moviename)
	a, b, acts = get.getImagesFromGrid(moviename)

	moviejson['boxoffice'] = get.getBoxOfficeDetails(moviename)
	if moviejson['boxoffice'] != None:
		fd = get.getBoxPercent(moviename, 'First Day')
		fwd = get.getBoxPercent(moviename, 'First Weekend')
		fw = get.getBoxPercent(moviename, 'First Week')
		if fd != None:
			fd = int(fd)
		if fw != None:
			fw = int(fw)
		if fwd != None:
			fwd = int(fwd)
		moviejson['boxoffice']['betterday'] = fd
		moviejson['boxoffice']['betterweekend'] = fwd
		moviejson['boxoffice']['betterweek'] = fw
		if 'day_fix' not in moviejson['boxoffice']:
			moviejson['boxoffice'] = None

	posts = get.getAllBlogs()
	img = fs.get_last_version(_id = 'playstore').read().encode('base64')
	indian_cities = ", ".join( [str(c).title() for c in get.get_indian_cities()] )
	return render_template("moviePage1.html", movie = moviejson, alltime = alltime, upcoming = upcoming, actsimg = acts, total = total,
						                    showTime = showTime, cities = indian_cities, playstore = img, posts = posts)

app.run(host='0.0.0.0', debug=True)