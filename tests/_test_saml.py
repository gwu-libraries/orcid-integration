import pytest 
from onelogin.saml2.utils import OneLogin_Saml2_Utils
from onelogin.saml2.xml_utils import OneLogin_Saml2_XML
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.constants import OneLogin_Saml2_Constants
from flask import session
from freezegun import freeze_time
from lxml import etree
#from signxml import XMLSigner, namespaces
import uuid
import xmlsec
#from signxml.algorithms import CanonicalizationMethod

@pytest.fixture()
def saml_response():
    with open('tests/test_saml_response.txt') as f:
        return f.read()
    
@pytest.fixture()
def saml_relay_state():
    return "http://localhost/orcid?scopes=/read-limited+/activities/update&register=False"

@pytest.fixture()
def saml_request(saml_relay_state, saml_response):
    return {
        'https': 'off',
        'http_host': 'http://localhost:4000/api/saml',
        'server_port': None,
        'script_name': '',
        'get_data': {'acs': None},
        # Uncomment if using ADFS as IdP, https://github.com/onelogin/python-saml/pull/144
        'lowercase_urlencoding': True,
        'post_data': {'SAMLResponse': saml_response,
                       'RelayState': saml_relay_state}
    }

@freeze_time('2025-04-15 13:25:00')
def test_acs(client, saml_response, saml_relay_state):
    response = client.post(query_string='acs', base_url='http://localhost:8000/', data=saml_response, content_type='application/x-www-form-urlencoded')
    print(response.text)