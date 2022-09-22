from flask import current_app, url_for
from cryptography.fernet import Fernet
    
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

def create_encryption_key():
    '''
    Creates a secret key using the Fernet algorithm. To be used only when setting up the app; key should be stored in the orcidflask/encryption directory.
    '''
    key = Fernet.generate_key()
    return key
