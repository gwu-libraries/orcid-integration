'''
Functions to handle the creation of SAML SP metadata and to retrieve attributes from the IdP metadata.
The following code closely follows the Flask example at https://github.com/onelogin/python3-saml/blob/master/demo-flask/index.py
'''

from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.utils import OneLogin_Saml2_Utils
from flask import current_app
from urllib.parse import urlparse

def init_saml_auth(request):
    '''
    :params request: a Flask request object
    returns a python-saml auth object and the modified request object
    '''
    # Get current Flask app (to access configurations)
    app = current_app._get_current_object()
    auth_req = prepare_flask_request(request)
    auth = OneLogin_Saml2_Auth(auth_req, custom_base_path=app.config['SAML_PATH'])
    return auth, auth_req

def prepare_flask_request(request):
    '''
    :param request: A Flask request object
    returns a python-saml request object with data from the Flask request object
    '''
    # host of the SP
    url_data = urlparse(request.url)
    return {
        'https': 'on' if request.scheme == 'https' else 'off',
        'http_host': request.host,
        'server_port': url_data.port,
        'script_name': request.path,
        'get_data': request.args.copy(),
        # Uncomment if using ADFS as IdP, https://github.com/onelogin/python-saml/pull/144
        'lowercase_urlencoding': True,
        'post_data': request.form.copy()
    }

def get_metadata_from_session(session):
    '''
    Extracts values from a Flask session object corresponding to certain SAML metadata attributes.
    :param session: a Flask session object
    '''
    # SAML attribute names
    attr_names = ['samlNameId', 'samlSessionIndex', 'samlNameIdFormat', 'samlNameIdNameQualifier', 'samlNameIdSPNameQualifier']
    # parameter names used by the python3-saml auth object
    keys = ['name_id', 'session_index', 'name_id_format', 'nq', 'spnq']
    metadata_dict = {key: session.get(attr_name) for (key, attr_name) in zip(keys, attr_names)}
    return metadata_dict

def add_metadata_to_session(auth, session):
    '''
    Stores the SAML metadata in the IdP response in a session object. 
    :param auth: a python-saml auth object.
    :param session: a Flask session object.
    '''
    # Delete the previous session ID if storing this
    if 'AuthNRequestID' in session:
        del session['AuthNRequestID']
    # Store SAML attributes in the session object
    session['samlUserdata'] = auth.get_attributes()
    session['samlNameId'] = auth.get_nameid()
    session['samlNameIdFormat'] = auth.get_nameid_format()
    session['samlNameIdNameQualifier'] = auth.get_nameid_nq()
    session['samlNameIdSPNameQualifier'] = auth.get_nameid_spnq()
    session['samlSessionIndex'] = auth.get_session_index()
    
    return session

def get_attributes(session):
    '''
    Retrieve SAML attributes from Flask session data.
    :param session: a Flask session object
    returns attributes (if any) and a Boolean flag for the logout button --> Not sure we need this
    '''
    if 'samlUserdata' in session:
        if len(session['samlUserdata']) > 0:
            attributes = session['samlUserdata'].items()
            return attributes, True
    return False, False