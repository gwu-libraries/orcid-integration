import pytest 
from flask import url_for
from urllib.parse import urlparse, parse_qs
import responses
from responses import matchers
import requests
from orcidflask.db.models import Token
import datetime

@pytest.fixture()
def user_attributes():
    return {'samlUserdata': {
                            'emailaddress': ['test@example.com'],
                             'firstname': ['Test'],
                             'lastname': ['User']
                            },
            'samlNameId': 'testId'
            }

@pytest.fixture()
def auth_code():
    return 'test_code'

@pytest.fixture()
def redirect_url(test_app):
    with test_app.app_context():
        return url_for('registration.orcid_redirect', _external=True, _scheme='https')

def test_orcid_login(client, user_attributes, test_app):
    with client.session_transaction() as session:
        session['samlUserdata'] = user_attributes.get('samlUserdata')
        session['samlNameId'] = user_attributes.get('samlNameId')
    response = client.get('/orcid', query_string={'scopes': '/read-limited /activities/update', 'register': 'True'})
    assert response.status_code == 302  
    redirect = urlparse(response.location)
    query = parse_qs(redirect.query)
    if test_app.config['PREFILL_REGISTRATION']:
        assert redirect.path == urlparse(test_app.config['orcid_register_url']).path
        assert query['family_names'] == user_attributes['samlUserdata']['lastname']
        assert query['given_names'] == user_attributes['samlUserdata']['firstname']
        assert query['email'] == user_attributes['samlUserdata']['emailaddress']
    else:
        assert redirect.path == urlparse(test_app.config['orcid_auth_url']).path
    assert query['client_id'][0] == test_app.config['CLIENT_ID']

@responses.activate   
def test_orcid_redirect(client, test_app, auth_code, redirect_url, user_attributes, database):
    orcid_resp_mock = responses.Response(
        method='POST',
        url=test_app.config['orcid_token_url'],
        json={ 'access_token': 'test-access-token',
              'refresh_token': 'test-refresh-token',
              'expires_in': 631138518,
              'scope': '/read-limited /activities/update',
              'orcid': '0000-0000-0000-0000' },
        match=[matchers.urlencoded_params_matcher({ 'client_id': test_app.config['CLIENT_ID'],
                                                    'client_secret': test_app.config['CLIENT_SECRET'],
                                                    'grant_type': 'authorization_code',
                                                    'code': auth_code,
                                                     'redirect_uri': redirect_url})
            ],
    )
    responses.add(orcid_resp_mock)
    orcid_resp = client.get('/orcid-redirect', query_string={'code': auth_code})
    assert orcid_resp.status_code == 302
    db_state = [record.to_dict() for record in Token.query.all()]
    assert db_state[0]['userId'] == user_attributes.get('samlNameId')
    assert db_state[0]['access_token'] == 'test-access-token'
    assert db_state[0]['orcid'] == '0000-0000-0000-0000' 
