from flask import Flask
from flask.cli import with_appcontext
from flask_migrate import Migrate
import os
import click
from orcid_utils import load_encryption_key, new_encryption_key
from orcidflask.registration.views import registration
from orcidflask.api.views import api
import json
from orcidflask.db import db
from datetime import datetime as dt

migrate = Migrate()

def create_app(blueprint: str='registration'):
    '''
    Application factory. The argument should be either "registration" or "api", depending on the version of the application to be started. For invocation, see https://flask.palletsprojects.com/en/stable/cli/
    '''
    app = Flask(__name__)
    # load default configs from default_settings.py
    app.config.from_object('orcidflask.default_settings')
    # load sensitive config settings 
    app.config.from_envvar('ORCIDFLASK_SETTINGS')
    # Set the ORCID URL based on the setting in default_settings.py
    if os.getenv('ORCID_SERVER') == 'sandbox':
        base_url = 'https://sandbox.orcid.org'
    else:
        base_url = 'https://orcid.org'
    # Personal attributes from SAML metadata definitions
    app.config['orcid_auth_url'] = base_url + '/oauth/authorize?client_id={orcid_client_id}&response_type=code&scope={scopes}&redirect_uri={redirect_uri}&family_names={lastname}&given_names={firstname}&email={emailaddress}'
    app.config['orcid_register_url'] = base_url + '/oauth/authorize?client_id={orcid_client_id}&response_type=code&scope={scopes}&redirect_uri={redirect_uri}&family_names={lastname}&given_names={firstname}&email={emailaddress}&show_login=false'
    app.config['orcid_token_url'] = base_url + '/oauth/token'
    app.config['SAML_PATH'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'saml')
    app.config["SESSION_COOKIE_DOMAIN"] = app.config["SERVER_NAME"]
    app.secret_key = app.config['SECRET_KEY']
    postgres_user = os.getenv('POSTGRES_USER')
    postgres_pwd = os.getenv('POSTGRES_PASSWORD')
    postgres_db_host = os.getenv('POSTGRES_DB_HOST')
    postgres_port = os.getenv('POSTGRES_PORT')
    postgres_db = os.getenv('POSTGRES_DB')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{postgres_user}:{postgres_pwd}@{postgres_db_host}:{postgres_port}/{postgres_db}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db_key_file = os.getenv('DB_ENCRYPTION_FILE')
    if not os.getenv('TESTING'):
        app.config['db_encryption_key'] = load_encryption_key(db_key_file)
    db.init_app(app)
    migrate.init_app(app, db)

    if blueprint == 'registration':
        app.register_blueprint(registration)
    else:
        app.register_blueprint(api)

    app.cli.add_command(reset_db)
    app.cli.add_command(create_secret_key)
    app.cli.add_command(serialize_db)
    app.cli.add_command(create_api_key)
    return app

from orcidflask.db.models import Token, APIKey, generate_key

@click.command('create-secret-key')
@click.argument('file')
@with_appcontext
def create_secret_key(file):
    '''
    Creates a new database encryption key and saves to the provided file path. Will not overwrite the existing file, if it exists.
    '''
    new_encryption_key(file)

@click.command('reset-db')
@with_appcontext
def reset_db():
    '''
    Resets the associated database by dropping all tables. Warning: for development purposes only. Do not run on a production instance without first backing up the database, as this command will result in the loss of all data.
    '''
    db.drop_all()

@click.command('serialize-db')
@click.argument('file', type=click.File('w'))
@with_appcontext
def serialize_db(file):
    '''
    Serializes the database as a JSON dump. Argument should be the path to a file, preferably in a volume mapped to the container, such as /opt/orcid_integration/data
    '''
    # get all records from the database
    records = Token.query.all()
    # convert to Python dicts
    records = [record.to_dict() for record in records] 
    json.dump(records, file)
    

@click.command('create-api-key')
@click.argument('userId')
@with_appcontext
def create_api_key(userId: str):
    '''userId should be an email address identifying the user for whom the key is being created.'''
    api_key_str = generate_key()
    api_key = APIKey(userId=userId, timestamp=dt.now(), api_key=api_key_str)
    db.session.add(api_key)
    db.session.commit()
    print(f'API key created for user {userId} is {api_key_str}. Please pass this key as a request header when making an API call: Authorization: APikey YOUR_API_KEY')
