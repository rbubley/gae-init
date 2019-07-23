# coding: utf-8

import flask
import jwt

import auth
import config
import util

from main import app


azure_ad_config = dict(
  access_token_method='POST',
  access_token_url='https://login.microsoftonline.com/common/oauth2/token',
  api_base_url='',
  authorize_url='https://login.microsoftonline.com/common/oauth2/authorize',
  client_id=config.CONFIG_DB.azure_ad_client_id,
  client_secret=config.CONFIG_DB.azure_ad_client_secret,
  request_token_params={
    'scope': 'openid profile user_impersonation',
  },
)

azure_ad = auth.create_oauth_app(azure_ad_config, 'azure_ad')


@app.route('/api/auth/callback/azure_ad/')
def azure_ad_authorized():
  id_token = azure_ad.authorize_access_token()
  if id_token is None:
    flask.flash('You denied the request to sign in.')
    return flask.redirect(util.get_next_url)
  flask.session['oauth_token'] = (id_token, '')
  try:
    decoded_id_token = jwt.decode(id_token, verify=False)
  except (jwt.DecodeError, jwt.ExpiredSignature):
    flask.flash('You denied the request to sign in.')
    return flask.redirect(util.get_next_url)
  user_db = retrieve_user_from_azure_ad(decoded_id_token)
  return auth.signin_user_db(user_db)


@app.route('/signin/azure_ad/')
def signin_azure_ad():
  return auth.signin_oauth(azure_ad)


def retrieve_user_from_azure_ad(response):
  auth_id = 'azure_ad_%s' % response['oid']
  email = response.get('upn', '')
  first_name = response.get('given_name', '')
  last_name = response.get('family_name', '')
  username = ' '.join((first_name, last_name)).strip()
  return auth.create_user_db(
    auth_id=auth_id,
    name='%s %s' % (first_name, last_name),
    username=email or username,
    email=email,
    verified=bool(email),
  )
