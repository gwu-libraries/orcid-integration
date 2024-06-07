import pytest
from orcid.lyterati_utils import Lyterati
from orcid.orcid import ORCiDWork
import json


@pytest.fixture
def user_id():
    return 'G123456789'
    
@pytest.fixture
def file_path():
    return './tests'

@pytest.fixture
def author_names():
    return ['Beatrix Potter', 'Frank Chateaubriand']

@pytest.fixture
def contributors():
    return [{'name': 'Beatrix Potter',
             'orcid': '0000-0000-0000-0000'},
             {'name': 'Kenneth Grahame',
              'orcid': '0000-0000-0000-0001'}]

@pytest.fixture
def work():
    return {'title': 'A fascinating monograph',
            'container': 'Oxfurred University Press',
            'work_type': 'book',
            'pub_year': '2000'}

class TestLyterati:

    def test_load_files(self, user_id, file_path):
        lyterati = Lyterati(user_id=user_id, file_path=file_path)
        assert lyterati.user_data[0]['gw_id'] == user_id
        assert len(lyterati.user_data) == 2
        assert lyterati.user_data[1]["title"] == 'Fascinating problems in fascinating literature'
        assert { k for record in lyterati.user_data for k in record.keys() } == {'gw_id', 'title', 'publisher', 'authors', 'start_year','file_name'}

class TestORCiDWord:

    def test_split_authors(self, author_names):
        author_str_and = ' and '.join(author_names)
        author_str_with = ' with '.join(author_names)
        author_str_comma = ', '.join(author_names)
        for author_str in [author_str_and, author_str_with, author_str_comma]:
            assert ORCiDWork.split_authors(author_str) == author_names

    def test_create_work(self, work, contributors):
        work.update({'contributors': contributors})
        orcid_work = ORCiDWork(**work)
        json_work = orcid_work.create_json()
        assert json.loads(json_work) # tests for valid JSON