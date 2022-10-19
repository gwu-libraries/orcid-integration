from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import click
from orcid_utils import load_encryption_key, new_encryption_key

app = Flask(__name__)
# load default configs from default_settings.py
app.config.from_object('orcidflask.default_settings')
# load sensitive config settings 
app.config.from_envvar('ORCIDFLASK_SETTINGS')
# Personal attributes from SAML metadata definitions
app.config['orcid_auth_url'] = 'https://sandbox.orcid.org/oauth/authorize?client_id={orcid_client_id}&response_type=code&scope={scopes}&redirect_uri={redirect_uri}&family_names={lastname}&given_names={firstname}&email={emailaddress}'
app.config['orcid_register_url'] = 'https://sandbox.orcid.org/register?client_id={orcid_client_id}&response_type=code&scope={scopes}&redirect_uri={redirect_uri}&family_names={lastname}&given_names={firstname}&email={emailaddress}'
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
db_key_file = os.getenv('DB_ENCRYPTION_FILE')
app.config['db_encryption_key'] = load_encryption_key(db_key_file)
db = SQLAlchemy(app)
db.create_all()

import orcidflask.views

@app.cli.command('create-secret-key')
@click.argument('file')
def create_secret_key(file):
    '''
    Creates a new database encryption key and saves to the provided file path. Will not overwrite the existing file, if it exists.
    '''
    store_encryption_key(file)

@app.cli.command('reset-db')
def reset_db():
    '''
    Resets the associated database by dropping all tables. Warning: for development purposes only. Do not run on a production instance without first backing up the database, as this command will result in the loss of all data.
    '''
    db.drop_all()