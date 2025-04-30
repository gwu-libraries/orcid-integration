import pytest 
from orcidflask.db.models import Token
from orcidflask.db import db
from sqlalchemy import inspect
import json

@pytest.fixture()
def sample_data(test_app):
    with test_app.app_context():
        db.session.add(Token(userId = 'testId2', access_token = 'test-token', refresh_token = 'test-refresh-token',
            expires_in = 1, token_scope = 'test-scope', orcid = 'test-orcid'))
        db.session.commit()
        db.session.close()

@pytest.fixture()
def token_file(tmp_path_factory):
    return tmp_path_factory.mktemp('tmp') / 'tokens.json'
    
def test_token_dump(test_app, sample_data, runner, token_file, database):
    # Create the Token table
    with test_app.app_context():
        runner.invoke(args=['serialize-db', token_file])
    with open(token_file) as f:
        token_dump = json.load(f)
    assert len(token_dump) == 1
    assert token_dump[0]['access_token'] == 'test-token'

''' This test causes pytest to hang!!
    def test_drop_table(runner, test_app):
    # Run the command that drops the table
    # Confirm that the table has been dropped
    with test_app.app_context():
        inspector = inspect(db.engines[None])
        runner.invoke(args='reset-db')
        assert not inspector.has_table('token')
'''
