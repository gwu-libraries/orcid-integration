from flask import Flask, session, request, url_for, redirect
import requests
from requests.exceptions import HTTPError

app = Flask(__name__)
# Property used for encoding session cookies
# Key from documentation
# TO DO: replace with actual randomly generated key and move to ENV variable
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Move to ENV variable
app.config['orcid_client_id'] = ''
app.config['orcid_client_secret'] = ''
app.config['orcid_auth_url'] = 'https://sandbox.orcid.org/oauth/authorize?client_id={orcid_client_id}&response_type=code&scope=/read-limited /activities/update /person/update&redirect_uri={redirect_uri}'
app.config['orcid_token_url'] = 'https://sandbox.orcid.org/oauth/token'

@app.route('/')
def index():
    '''
    Should render homepage and if behind SSO, retrieve netID from SAML and store in a session variable.
    See the example here: https://github.com/onelogin/python3-saml/blob/master/demo-flask/index.py
    '''
    # TO DO: Add template with button to take user to the ORCID authorization site
    # TO DO: Capture SAML identifier in session object
    return redirect(app.config['orcid_auth_url'].format(orcid_client_id=app.config['orcid_client_id'], 
                                                        redirect_uri=url_for('orcid_redirect', 
                                                        _external=True)))

@app.route('/orcid-redirect')
def orcid_redirect():
    '''
    Redirect route that retrieves the one-time code from ORCID after user logs in and approves.
    '''
    # TO DO: Check for error/access denied
    orcid_code = request.args.get('code')
    headers = {'Accept': 'application/json',
                'Content-Type': 'application/x-www-form-urlencoded'}
    try:
        response = requests.post(app.config['orcid_token_url'], 
                                headers=headers, 
                                data=prepare_token_payload(orcid_code))
        response.raise_for_status()
    except HTTPError as e:
        # TO DO: handle HTTP errors
        raise
    orcid_auth = response.json()
    print(orcid_auth)
    # TO DO: Retrieve SAML identifier from session object
    # TO DO: Save to data store
    # TO DO: return success template
    return "Successfully authorized!"
   

def prepare_token_payload(code: str):
    '''
    :param code: the code returned from ORCID after the user authorizes our application.
    '''
    return  {'client_id': app.config['orcid_client_id'],
            'client_secret': app.config['orcid_client_secret'],
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': url_for('orcid_redirect', _external=True)}



