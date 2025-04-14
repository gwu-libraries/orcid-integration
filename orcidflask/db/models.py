from . import db
from sqlalchemy.sql import func
from sqlalchemy import TypeDecorator
from cryptography.fernet import Fernet
from flask import current_app
from uuid import uuid1

def fernet_encrypt(data):
    '''
    Encrypts data using the Fernet algorithm with the key set in the app's config object
    '''
    fernet = Fernet(current_app.config['db_encryption_key'])
    return fernet.encrypt(data.encode())


def fernet_decrypt(data):
    '''
    Decrypts data using the Fernet algorithm with the key set in the app's config object
    '''
    fernet = Fernet(current_app.config['db_encryption_key'])
    return fernet.decrypt(data).decode()

class EncryptedValue(TypeDecorator):
    impl = db.LargeBinary

    def process_bind_param(self, value, dialect):
        return fernet_encrypt(value)
    
    def process_result_value(self, value, dialect):
        return fernet_decrypt(value)
    

def generate_key():
    '''
    Generates a unique indentifier for use as an API key (using the system time)
    '''
    return str(uuid1())


class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.String(80), unique=False, nullable=False)
    access_token = db.Column(EncryptedValue, unique=False, nullable=False)
    refresh_token = db.Column(EncryptedValue, unique=False, nullable=False)
    expires_in = db.Column(db.Integer, nullable=False)
    token_scope = db.Column(db.String(80), unique=False, nullable=False)
    orcid = db.Column(db.String(80), unique=False, nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return '<User %r, access_token=%r, token_scope=%r, orcid=%r' % \
                (self.userId, self.access_token, self.token_scope, self.orcid)
    
    def to_dict(self):
        '''
        Returns the record as a Python dict
        '''
        record = {column.name: getattr(self, column.name) 
                for column in self.__table__.columns}
        # Convert timestamp to string
        record['timestamp'] = record['timestamp'].isoformat()
        return record

class APIKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    api_key = db.Column(db.String(36), unique=True, nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())
    # Email address of the user for whom the API key was created
    userId = db.Column(db.String(80), unique=False, nullable=False)

    @classmethod
    def check_api_key(cls, api_key: str):
        '''Checks whether the given key exists in the database.'''
        return cls.query.filter_by(api_key=api_key).first()