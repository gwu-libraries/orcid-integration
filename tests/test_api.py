import pytest 
from orcidflask.db.models import Token, APIKey, generate_key
from orcidflask.db import db
from datetime import datetime as dt
from uuid import uuid1


@pytest.fixture()
def orcid():
    return '0000-0000-0000-0000'

@pytest.fixture()
def user_id():
    return 'dsmith@gwu.edu'

@pytest.fixture()
def orcid_registration(test_app, orcid, user_id, database):
    with test_app.app_context():
        db.session.add(Token(userId=user_id, access_token='test-token', refresh_token='test-refresh-token',
            expires_in=1, token_scope='test-scope', orcid=orcid))
        db.session.commit()
        db.session.close()


@pytest.fixture()
def api_registration(test_app, user_id, api_key, database):
    with test_app.app_context():
        db.session.add(APIKey(userId=user_id, timestamp=dt.now(), api_key=api_key))
        db.session.commit()
        db.session.close()

def test_get_token(client_api, orcid, api_key, orcid_registration, api_registration, database):
    headers = {'Authorization': f'Apikey {api_key}'}
    resp = client_api.get('api/get-token', headers=headers, query_string={'orcid': orcid})
    assert resp.json['orcid'] == orcid
    assert resp.json['access_token'] == 'test-token'


def test_get_token_bad_key(client_api, orcid):
    headers = {'Authorization': f'Apikey {uuid1()}'}
    resp = client_api.get('api/get-token', headers=headers, query_string={'orcid': orcid})
    assert resp.status_code == 403
    assert resp.json['message'] == 'API key has not been registered. Please have the application administrator create an API key for you.'

def test_get_token_bad_orcid(client_api, api_key):
    bad_orcid = '0000-1111-0000-1111'
    headers = {'Authorization': f'Apikey {api_key}'}
    resp = client_api.get('api/get-token', headers=headers, query_string={'orcid': bad_orcid})
    assert resp.status_code == 200
    assert 'error' in resp.json and resp.json['error'] == f'Entry not found for ORCiD {bad_orcid}. Has the user registered with the GW ORCiD integration app?'