import pytest 
import os
from orcid_utils import create_encryption_key
import json
from orcidflask import app, db


@pytest.fixture(scope='module')
def saml_settings():
    return {
        'strict': True,
        'debug': True,
        'sp': {
            'entityId': 'https://test.orcid.library.gwu.edu/metadata/',
            'assertionConsumerService': {
                'url': 'http://localhost/?acs',
                'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST'
            },
            'singleLogoutService': {
                'url': 'http://localhost/?sls',
                'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect'
            },
            'NameIDFormat': 'urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified',
            'x509cert': '',
            'privateKey': ''
        },
        'idp': {
            'entityId': 'http://idp.example.com',
            'singleSignOnService': {
                'url': 'http://idp.example.com/saml2',
                'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect'
            },
            'singleLogoutService': {
                'url': 'http://idp.example.com/saml2',
                'responseUrl': 'http://idp.example.com/saml2',
                'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect'
            },
            'x509cert': 'MIICajCCAdOgAwIBAgIBADANBgkqhkiG9w0BAQ0FADBSMQswCQYDVQQGEwJ1czETMBEGA1UECAwKQ2FsaWZvcm5pYTEVMBMGA1UECgwMT25lbG9naW4gSW5jMRcwFQYDVQQDDA5zcC5leGFtcGxlLmNvbTAeFw0xNDA3MTcxNDEyNTZaFw0xNTA3MTcxNDEyNTZaMFIxCzAJBgNVBAYTAnVzMRMwEQYDVQQIDApDYWxpZm9ybmlhMRUwEwYDVQQKDAxPbmVsb2dpbiBJbmMxFzAVBgNVBAMMDnNwLmV4YW1wbGUuY29tMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDZx+ON4IUoIWxgukTb1tOiX3bMYzYQiwWPUNMp+Fq82xoNogso2bykZG0yiJm5o8zv/sd6pGouayMgkx/2FSOdc36T0jGbCHuRSbtia0PEzNIRtmViMrt3AeoWBidRXmZsxCNLwgIV6dn2WpuE5Az0bHgpZnQxTKFek0BMKU/d8wIDAQABo1AwTjAdBgNVHQ4EFgQUGHxYqZYyX7cTxKVODVgZwSTdCnwwHwYDVR0jBBgwFoAUGHxYqZYyX7cTxKVODVgZwSTdCnwwDAYDVR0TBAUwAwEB/zANBgkqhkiG9w0BAQ0FAAOBgQByFOl+hMFICbd3DJfnp2Rgd/dqttsZG/tyhILWvErbio/DEe98mXpowhTkC04ENprOyXi7ZbUqiicF89uAGyt1oqgTUCD1VsLahqIcmrzgumNyTwLGWo17WDAa1/usDhetWAMhgzF/Cnf5ek0nK00m0YZGyc4LzgD0CROMASTWNg=='
        }
    }

@pytest.fixture(scope='module')
def saml_settings_path(tmpdir_factory, saml_settings):
    settings_dir = tmpdir_factory.mktemp('saml')
    settings_file = settings_dir.join('settings.json')
    with open(settings_file, 'w') as f:
        json.dump(saml_settings, f)
    return str(settings_dir)



@pytest.fixture(scope='module')
def test_app(saml_settings_path):
    app.config.update({'db_encryption_key': create_encryption_key(),
                        'SAML_PATH': saml_settings_path,
    })
    yield app


@pytest.fixture(scope='module')
def client(test_app):
    return test_app.test_client()

@pytest.fixture()
def runner(test_app):
    return test_app.test_cli_runner()

@pytest.fixture(scope='module')
def database(client):

    db.drop_all()
    db.create_all()

    yield

    db.session.remove()
    db.drop_all()

