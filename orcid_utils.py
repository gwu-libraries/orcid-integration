from flask import current_app, url_for
from cryptography.fernet import Fernet
from os.path import exists
    
def prepare_token_payload(code: str):
    '''
    :param code: the code returned from ORCID after the user authorizes our application.
    '''
    app = current_app._get_current_object()
    return  {'client_id': app.config['CLIENT_ID'],
            'client_secret': app.config['CLIENT_SECRET'],
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': url_for('orcid_redirect', _external=True, _scheme='https')}

def extract_saml_user_data(session):
    '''
    Extracts name and email attributes from the samlUserData object.
    :param session: a Flask session object
    '''
    saml_attrs = ['emailaddress', 'firstname', 'lastname']
    saml_data = {}
    if 'samlUserdata' in session:
        user_data = session['samlUserdata']
        for saml_attr in saml_attrs:
            value = user_data.get(saml_attr)
            # Name and email attributes appear to be arrays; not sure if there can be more than one element
            if value:
                value = value[0]
            saml_data[saml_attr] = value
    return saml_data

def new_encryption_key(file, replace=False):
    '''
    Creates and stores a new encryption key at the provided path to file and returns the key. If file exists and replace=True, it will overwrite an existing file; otherwise, it will skip saving.
    '''    
    key = create_encryption_key()
    if (not exists(file)) or (replace):
        with open(file, 'wb') as f:
            f.write(key)
    return key

def create_encryption_key():
    '''
    Creates a secret key using the Fernet algorithm. To be used only when setting up the app; key should be stored in the orcidflask/encryption directory.
    '''
    key = Fernet.generate_key()
    return key

def load_encryption_key(file):
    '''
    Loads a secret key as binary from the provided file, for use in encrypting database values. If file not found, creates a new key
    '''
    try:
        with open(file, 'rb') as f:
            key = f.read()
    except FileNotFoundError:
        key = new_encryption_key(file)
    return key