import pytest 
import os
from orcid_utils import create_encryption_key
import json
from orcidflask import create_app
from orcidflask.db import db
from orcidflask.db.models import generate_key

@pytest.fixture(scope='module')
def encryption_key():
    return create_encryption_key()


@pytest.fixture(scope='module')
def saml_settings():
    return {
        'strict': True,
        'debug': True,
        'sp': {
            'entityId': 'http://localhost/metadata/',
            'assertionConsumerService': {
                'url': 'http://localhost:8000/?acs',
                'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST'
            },
            'singleLogoutService': {
                'url': 'http://localhost:8000/?sls',
                'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect'
            },
            'NameIDFormat': 'urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified',
            'x509cert': 'MIICcDCCAdmgAwIBAgIBADANBgkqhkiG9w0BAQ0FADBVMQswCQYDVQQGEwJ1czEdMBsGA1UECAwURGlzdHJpY3Qgb2YgQ29sdW1iaWExDDAKBgNVBAoMA0dXVTEZMBcGA1UEAwwQaHR0cDovL2xvY2FsaG9zdDAeFw0yNTAzMTkxNTQ5MDdaFw0yNjAzMTkxNTQ5MDdaMFUxCzAJBgNVBAYTAnVzMR0wGwYDVQQIDBREaXN0cmljdCBvZiBDb2x1bWJpYTEMMAoGA1UECgwDR1dVMRkwFwYDVQQDDBBodHRwOi8vbG9jYWxob3N0MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC3/iGSSDB3YFu5Gvko8Hzyph+2FQ3nrHSKcMPjER5a5GX5I881VBLkfxLPRNLDlKPgTBou1jlVdmC09tEJyMdlK9V8NlgPIdKR09p4yopfFEZcDBJfjk8XL6qXMiRXkcV6UP68QRasNZ2hApqSIGm1UMwyE1teqtEZKHVoPZExBwIDAQABo1AwTjAdBgNVHQ4EFgQU/stj8DDeO15sEGHOeO+KP7j+XU4wHwYDVR0jBBgwFoAU/stj8DDeO15sEGHOeO+KP7j+XU4wDAYDVR0TBAUwAwEB/zANBgkqhkiG9w0BAQ0FAAOBgQA/sXiknflk7r0nsCg36mNijrUgneevdS2O9vXjSJaMCVDXgXBcXvoVJKkOlFoKzpWiX74TGe1kqcH+mphkt50PSZ5qpa7rtWYSdlKs9QMq4l3orud7vxllD9R4Wi9NNP4z4DNFwwCfkxn9lz3Kq+NRsqWy3JGOC/9nRXg35z+CAA==',
            'privateKey': 'MIICdQIBADANBgkqhkiG9w0BAQEFAASCAl8wggJbAgEAAoGBALf+IZJIMHdgW7ka+SjwfPKmH7YVDeesdIpww+MRHlrkZfkjzzVUEuR/Es9E0sOUo+BMGi7WOVV2YLT20QnIx2Ur1Xw2WA8h0pHT2njKil8URlwMEl+OTxcvqpcyJFeRxXpQ/rxBFqw1naECmpIgabVQzDITW16q0RkodWg9kTEHAgMBAAECgYBBoJO46abf7a7Jx6U3xQ/MPRTyjW/4QrsO5kn4pBJ/uRfmVa+DBgn3FpxO8e17dXk+d+ae7iplIWQ9KAxHwSXdhXoiZ89dh4iufNHj7WLsAjJhuCCeeqtaIXw5gDrSo9ulHKxWKqj9V6pPL0reWcg38D50EzW5mqlapEHxgk+GAQJBAN1fgpjBS8BGYk6ENNddWsL8pY48WlKJn64ZDJyGyr8Vt/0buMj9LtOzbh5WDXIXw8wEvgx6LyUdPyqCbpXWFdcCQQDUxcpIwwk4IIh5PhOYr6FCwxlgjFrLK76Bf7k7gPUYRMZxIhACLyE1UxT/qt++5O+sfA9uVCqcn9Fup5EANPhRAkBrRfM1LsYUgIb24V3x1w06W8+mI1zpjkNQzFauKytoeY/VGW/sBbSBZfvAu5Z8aUO6Q7oMtdDOvWN0qAwKk9m1AkAzc8D+52sLT5Kw/vnuKkpswpEYb9hk2ScwWZqJcR3TyI3UPdBxNsRpCLZDPSbuGp56r2Vr4J6NUXhrscm2qxiBAkBbYjXCh9VM3O9mXfRJT+QyORQB38GBvBAbzdh2PTOtNatSvF3eUo2pQlrxF77GzNKTx99dq0KVrBKZuL23bIyP'
        },
        'idp': {
            'entityId': 'https://saml.example.com/entityid',
            'singleSignOnService': {
                'url': 'http://localhost:4000/api/saml/sso',
                'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect'
            },
            'singleLogoutService': {
                'url': 'http://localhost:4000/api/saml',
                'responseUrl': 'http://localhost:4000/api/saml',
                'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect'
            },
            'x509cert': 'MIIEBTCCAu2gAwIBAgIUVuhF7lX6n9Z83MUAIXuHJxa7TaIwDQYJKoZIhvcNAQELBQAwgZAxCzAJBgNVBAYTAlVTMR0wGwYDVQQIDBREaXN0cmljdCBvZiBDb2x1bWJpYTETMBEGA1UEBwwKV2FzaGluZ3RvbjEMMAoGA1UECgwDR1dVMQwwCgYDVQQLDANMQUkxEjAQBgNVBAMMCWxvY2FsaG9zdDEdMBsGCSqGSIb3DQEJARYOZHNtaXRoQGd3dS5lZHUwIBcNMjUwNDE1MTI1MjUyWhgPMzAyNDA4MTYxMjUyNTJaMIGQMQswCQYDVQQGEwJVUzEdMBsGA1UECAwURGlzdHJpY3Qgb2YgQ29sdW1iaWExEzARBgNVBAcMCldhc2hpbmd0b24xDDAKBgNVBAoMA0dXVTEMMAoGA1UECwwDTEFJMRIwEAYDVQQDDAlsb2NhbGhvc3QxHTAbBgkqhkiG9w0BCQEWDmRzbWl0aEBnd3UuZWR1MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAuuU+IEOV4YD8M9DJ8yCBtcO9VfeFiS3Aj9vwNyPHQBXvXqgeMGvswZfj5ZJjpNEYAvELJuDV/19EeDBy5YBXq9WNdOg+V9d07HMnkb2nycZ3IKsOu20hYJJFHTnFJJhpx0snV86w2bLYrFDJS9nW8mBXfYEkTH/wSiWNfBXzeRKDwKEsch1k7xNzsXu+AyACXfhvNlWb6DrxFcKK2x/cUGNItPCJbAMqXc6WHmVkVb2GZCUP0jiwr594l0NlH8iyum4yrg6XzuCsNtqDVpL4i7O9ic76PLozHWdJcUN0Fs6bKiCaXT9g5dRptSwFpLnEDaB6MzeZcbSOdGRw711m2wIDAQABo1MwUTAdBgNVHQ4EFgQUbhztZb1kfwFOybEYRnwlYDCOOzQwHwYDVR0jBBgwFoAUbhztZb1kfwFOybEYRnwlYDCOOzQwDwYDVR0TAQH/BAUwAwEB/zANBgkqhkiG9w0BAQsFAAOCAQEAnTf1c4LedIsBEylIqYChEZUkUQ6BgPsMt+ZBfl/BMi2mrowJPWZ2Wx6N8h7ZycQ7D2fsEpQ4hAMqcX8RnFuqSwY5awE/MrRpaiR/8o5EvEB2ZePAybybrU22/aTLq93AtAyyuJTZ6DMp1aCuMkJmoLGwr+JasiZUSIYIGxwAj52FJsHgwL7rT9ME06AcUoAwK4KZE9FGvX3TQ+ogz6+1QAddDy/h8fiiAkuh7Xf1W2SrLGpkI7KRTjbz6b4fSY5j+S7nTCqERQxdgTR4g7qMuysxp5s6EEd1ReoIOanrUNHFHg9iSJY2myhgWbT09m9BD03zrVbSW8kYdGsObytsbQ=='
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
def test_app(saml_settings_path, encryption_key):
    app = create_app()
    app.config.update({'db_encryption_key': encryption_key,
                        'SAML_PATH': saml_settings_path,
                        'TESTING': True,
                        'PRESERVE_CONTEXT_ON_EXCEPTION': False
    })
    yield app


@pytest.fixture(scope='module')
def client(test_app):
    return test_app.test_client()

@pytest.fixture(scope='module')
def runner(test_app):
    return test_app.test_cli_runner()

@pytest.fixture(scope='module')
def database(test_app):

    with test_app.app_context():
        db.drop_all()
        db.create_all()

        yield

        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='module')
def test_app_api(encryption_key):
    app = create_app('api')
    app.config.update({'db_encryption_key': encryption_key,
                        'SAML_PATH': saml_settings_path,
                        'TESTING': True,
                        'PRESERVE_CONTEXT_ON_EXCEPTION': False
    })
    yield app 

@pytest.fixture(scope='module')
def client_api(test_app_api):
    return test_app_api.test_client()

@pytest.fixture(scope='module')
def api_key():
    return generate_key()