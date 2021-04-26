from flask import current_app, url_for
    
def prepare_token_payload(code: str):
    '''
    :param code: the code returned from ORCID after the user authorizes our application.
    '''
    app = current_app._get_current_object()
    return  {'client_id': app.config['CLIENT_ID'],
            'client_secret': app.config['CLIENT_SECRET'],
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': url_for('orcid_redirect', _external=True)}