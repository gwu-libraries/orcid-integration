from flask import request, url_for, redirect, session, render_template
from orcidflask import app, db
from orcidflask.models import Token
from saml_utils import *
from orcid_utils import *
from onelogin.saml2.utils import OneLogin_Saml2_Utils
import requests
from requests.exceptions import HTTPError

@app.route('/', methods=['GET', 'POST'])
def index():
    '''
    Route handles the SSO process
    '''
    auth, auth_req = init_saml_auth(request)
    errors = []
    error_reason = None
    not_auth_warn = False
    success_slo = False
    attributes = False
    paint_logout = False

    # Initiating the SSO process
    if 'sso' in request.args:
        # Redirect to ORCID login upon successful SSO
        return redirect(auth.login(return_to=url_for('orcid_login')))
    # Initiating the SLO process
    elif 'slo' in request.args:
        metadata = get_metadata_from_session(session)
        return redirect(auth.logout(**metadata)) 

    # Consuming the SAML attributes from the IdP
    if 'acs' in request.args:
        # Getting the request ID, if necessary
        request_id = None
        if 'AuthNRequestID' in session:
            request_id = session['AuthNRequestID']
        # Process the XML
        auth.process_response(request_id=request_id)
        errors = auth.get_errors()
        # Check for errors
        not_auth_warn = not auth.is_authenticated()
        if len(errors) == 0:
            # Update the Flask session object with the SAML attributes for this user
            # Updating by reference here; otherwise, we break the session context local
            add_metadata_to_session(auth, session)
            # Redirect to a new page, if necessary
            self_url = OneLogin_Saml2_Utils.get_self_url(auth_req)
            if 'RelayState' in request.form and self_url != request.form['RelayState']:
                return redirect(auth.redirect_to(request.form['RelayState']))
        # Get the reason for auth failure if exists
        elif auth.get_settings().is_debug_active():
            error_reason = auth.get_last_error_reason()

    # Handle logout
    elif 'sls' in request.args:
        request_id = None
        if 'LogoutRequestID' in session:
            request_id = session['LogoutRequestID']
        dscb = lambda: session.clear()
        url = auth.process_slo(request_id=request_id, delete_session_cb=dscb)
        errors = auth.get_errors()
        if len(errors) == 0:
            if url is not None:
                return redirect(url)
            else:
                success_slo = True
        elif auth.get_settings().is_debug_active():
            error_reason = auth.get_last_error_reason()

    # Redirect for login if no params provided
    else:
        return redirect(auth.login(return_to=url_for('orcid_login')))

    # Redirect from logout process
    return redirect(app.config['SLO_REDIRECT'])

@app.route('/attrs/')
def attrs():
    attributes, paint_logout = get_attributes(session)
    return render_template('attrs.html', paint_logout=paint_logout,
                           attributes=attributes)


@app.route('/metadata/')
def metadata():
    req = prepare_flask_request(request)
    auth = init_saml_auth(req)
    settings = auth.get_settings()
    metadata = settings.get_sp_metadata()
    errors = settings.validate_metadata(metadata)

    if len(errors) == 0:
        resp = make_response(metadata, 200)
        resp.headers['Content-Type'] = 'text/xml'
    else:
        resp = make_response(', '.join(errors), 500)
    return resp


@app.route('/orcid', methods=('GET', 'POST'))
def orcid_login():
    '''
    Should render homepage and if behind SSO, retrieve netID from SAML and store in a session variable.
    See the example here: https://github.com/onelogin/python3-saml/blob/master/demo-flask/index.py
    '''
    # If no SAML attributes, redirect for SSO
    if not session.get('samlNameId'):
        return redirect(url_for('index'))

    if request.method == 'POST':
        app.logger.debug(request.form)
        scopes = ' '.join(request.form.keys())
        return redirect(app.config['orcid_auth_url'].format(orcid_client_id=app.config['CLIENT_ID'], 
                                                        scopes=scopes,
                                                        redirect_uri=url_for('orcid_redirect',
                                                        _scheme='https', 
                                                        _external=True)))
    return render_template('orcid_login.html')

@app.route('/orcid-redirect')
def orcid_redirect():
    '''
    Redirect route that retrieves the one-time code from ORCID after user logs in and approves.
    '''
    # Redirect here for access denied page
    if request.args.get('error') == 'access_denied':
        return render_template('orcid_denied.html') 
    
    elif request.args.get('error'):
        app.logger.error(request.args.get('error'))
        return render_template('oauth_error.html')

    orcid_code = request.args.get('code')
    headers = {'Accept': 'application/json',
                'Content-Type': 'application/x-www-form-urlencoded'}
    try:
        response = requests.post(app.config['orcid_token_url'], 
                                headers=headers, 
                                data=prepare_token_payload(orcid_code))
        response.raise_for_status()
    except HTTPError as e:
        app.logger.error(f'HTTPError {response.status_code}; Message {response.text}')
        return render_template('oauth_error.html')
    orcid_auth = response.json()
    # Get the user's ID from the SSO process
    saml_id = session.get('samlNameId')
    # Get token info from the response object
    access_token = orcid_auth['access_token']
    refresh_token = orcid_auth['refresh_token']
    expires_in = orcid_auth['expires_in']
    token_scope = orcid_auth['scope']
    orcid = orcid_auth['orcid']

    # Save to data store
    token = Token(userId = saml_id, access_token = access_token, refresh_token = refresh_token,
            expires_in = expires_in, token_scope = token_scope, orcid = orcid)
    db.session.add(token)
    db.session.commit()

    # return success page
    return render_template('orcid_success.html', saml_id=saml_id, orcid_auth={k: v for k,v in orcid_auth.items() if not k.endswith('token')})
