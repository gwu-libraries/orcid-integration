from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
# load default configs from default_settings.py
app.config.from_object('orcidflask.default_settings')
# load sensitive config settings 
app.config.from_envvar('ORCIDFLASK_SETTINGS')
app.config['orcid_auth_url'] = 'https://sandbox.orcid.org/oauth/authorize?client_id={orcid_client_id}&response_type=code&scope={scopes}&redirect_uri={redirect_uri}'
app.config['orcid_token_url'] = 'https://sandbox.orcid.org/oauth/token'
app.config['SAML_PATH'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'saml')
app.secret_key = app.config['SECRET_KEY']

postgres_user = os.getenv('POSTGRES_USER')
postgres_pwd = os.getenv('POSTGRES_PASSWORD')
postgres_db_host = os.getenv('POSTGRES_DB_HOST')
postgres_port = os.getenv('POSTGRES_PORT')
postgres_db = os.getenv('POSTGRES_DB')
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{postgres_user}:{postgres_pwd}@{postgres_db_host}:{postgres_port}/{postgres_db}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
db.create_all()

import orcidflask.views
