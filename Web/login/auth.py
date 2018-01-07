import json
from flask import url_for, session, request, redirect
from flask_oauthlib.client import OAuth, OAuthException
from flask.ext.login import login_user, current_user
from myapp.redirects import get_redirect_target
from myapp.models import User

oauth = OAuth()
facebook = oauth.remote_app('facebook',
    'facebook',
    consumer_key=os.environ['FACEBOOK_APP_ID'],
    consumer_secret=os.environ['FACEBOOK_APP_SECRET'],
    base_url='https://graph.facebook.com',
    access_token_url='/oauth/access_token',
    access_token_method='GET',
    authorize_url='https://www.facebook.com/dialog/oauth',
    request_token_params={'display': 'popup'}
)


@app.route('/login')
def login():
    callback = url_for(
        'facebook_authorized',
        next=get_redirect_target(),
        _external=True
    )
    return facebook.authorize(callback=callback)


@app.route('/login/authorized')
def facebook_authorized():
    resp = facebook.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    if isinstance(resp, OAuthException):
        return 'Access denied: %s' % resp.message
    me = facebook.get('/me', token=(resp['access_token'], ''))
    user = User.objects(fb_id=me.data['id']).first()
    if user and user.fb_token != resp['access_token']:
        user.fb_token = resp['access_token']
        user.save()
    if not user:
        user = User(
            fb_id=me.data['id'],
            first_name=me.data['first_name'],
            last_name=me.data['last_name'],
            fb_token=resp['access_token']
        )
        user.save()
    login_user(user)
    return json.dumps(me.data)


@facebook.tokengetter
def get_facebook_oauth_token():
    if current_user.is_authenticated():