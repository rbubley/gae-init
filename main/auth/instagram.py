# coding: utf-8

from __future__ import absolute_import

import flask

import auth
import model
import util

from main import app

instagram_config = dict(
  access_token_method='POST',
  access_token_url='https://api.instagram.com/oauth/access_token',
  api_base_url='https://api.instagram.com/v1',
  authorize_url='https://instagram.com/oauth/authorize/',
  client_id=model.Config.get_master_db().instagram_client_id,
  client_secret=model.Config.get_master_db().instagram_client_secret,
  save_request_token=auth.save_oauth1_request_token,
  fetch_request_token=auth.fetch_oauth1_request_token,
)

instagram = auth.create_oauth_app(instagram_config, 'instagram')


@app.route('/api/auth/callback/instagram/')
def instagram_authorized():
  id_token = instagram.authorize_access_token()
  if id_token is None:
    flask.flash('You denied the request to sign in.')
    return flask.redirect(util.get_next_url())

  user_db = retrieve_user_from_instagram(response.json()['data'])
  return auth.signin_user_db(user_db)


@app.route('/signin/instagram/')
def signin_instagram():
  return auth.signin_oauth(instagram)


def retrieve_user_from_instagram(response):
  auth_id = 'instagram_%s' % response['id']
  user_db = model.User.get_by('auth_ids', auth_id)
  if user_db:
    return user_db

  return auth.create_user_db(
    auth_id=auth_id,
    name=response.get('full_name', '').strip() or response.get('username'),
    username=response.get('username'),
  )
