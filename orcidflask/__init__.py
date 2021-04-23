from flask import Flask
import os

app = Flask(__name__)
# load default configs from default_settings.py
app.config.from_object('orcidflask.default_settings')
# load sensitive config settings 
app.config.from_envvar('ORCIDFLASK_SETTINGS')
app.config['orcid_auth_url'] = 'https://sandbox.orcid.org/oauth/authorize?client_id={orcid_client_id}&response_type=code&scope=/read-limited /activities/update /person/update&redirect_uri={redirect_uri}'
app.config['orcid_token_url'] = 'https://sandbox.orcid.org/oauth/token'
app.config['SAML_PATH'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'saml')
app.secret_key = app.config['SECRET_KEY']

import orcidflask.views