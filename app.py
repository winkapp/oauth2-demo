#!/usr/bin/env python

import flask
import os
import requests_oauthlib
import sys
import time

app = flask.Flask(__name__)

CLIENT_ID = os.environ.get('WINK_CLIENT_ID')
CLIENT_SECRET = os.environ.get('WINK_CLIENT_SECRET')
BASE_URL = 'https://api.wink.com'
AUTHORIZATION_URL = BASE_URL + '/oauth2/authorize'
TOKEN_URL = BASE_URL + '/oauth2/token'
REDIRECT_URI = 'http://127.0.0.1:5000/complete_association'
ACCESS_TOKEN_COOKIE_NAME = 'wink_access_token'

def get_client(access_token = None):
    token = None
    if access_token:
        token = {'access_token': access_token, 'token_type': 'bearer'}
    return requests_oauthlib.OAuth2Session(client_id=CLIENT_ID, redirect_uri=REDIRECT_URI, token=token)

@app.route("/")
def index():
    access_token = flask.request.cookies.get(ACCESS_TOKEN_COOKIE_NAME, None)
    name = None
    if access_token:
        response = get_client(access_token).get(BASE_URL + '/users/me').json()
        name = response['data']['first_name']
    return flask.render_template('index.html', name=name)

@app.route('/begin_association')
def begin_association():
    authorization_url, state = get_client().authorization_url(AUTHORIZATION_URL)
    return flask.redirect(authorization_url)

@app.route('/complete_association')
def complete_association():
    access_token = get_client().fetch_token(TOKEN_URL, client_id=CLIENT_ID, client_secret=CLIENT_SECRET, code=flask.request.args.get('code', None))['access_token']
    response = flask.make_response(flask.redirect(flask.url_for('.index')))
    response.set_cookie(ACCESS_TOKEN_COOKIE_NAME, value=access_token)
    return response



if __name__ == '__main__':
    if CLIENT_ID is None or CLIENT_SECRET is None:
        print 'Usage: WINK_CLIENT_ID=<your client id> WINK_CLIENT_SECRET=<your client secret> python ' + __file__
        sys.exit(1)
    app.secret_key = os.urandom(24)
    app.run()
