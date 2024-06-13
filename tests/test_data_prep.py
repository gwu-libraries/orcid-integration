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
def works():
    return [{'title': 'A fascinating monograph',
            'container': 'Oxfurred University Press',
            'work_type': 'book',
            'pub_year': '2000'}, 
            {'title': 'A fascinating article',
             'container': 'Journal of Fascinating Ideas',
             'work_type': 'article',
             'pub_year': '1994',
             'external_id_type': 'doi',
             'external_id': 'fake-doi-9999',
             'external_id_url': 'https://doi.org/fake-doi-9999'}
            ]

class TestLyterati:

    def test_load_files(self, user_id, file_path):
        lyterati = Lyterati(user_id=user_id, file_path=file_path)
        assert lyterati.user_data[0]['gw_id'] == user_id
        assert len(lyterati.user_data) == 2
        assert lyterati.user_data[1]["title"] == 'Fascinating problems in fascinating literature'
        assert { k for record in lyterati.user_data for k in record.keys() } == {'gw_id', 'title', 'publisher', 'authors', 'start_year','file_name'}
        assert lyterati.user_name == {'first_name': 'Jeremy', 'last_name': 'Fisher'}

class TestORCiDWord:

    def test_split_authors(self, author_names):
        author_str_and = ' and '.join(author_names)
        author_str_with = ' with '.join(author_names)
        author_str_comma = ', '.join(author_names)
        for author_str in [author_str_and, author_str_with, author_str_comma]:
            assert ORCiDWork.split_authors(author_str) == author_names

    def test_create_work(self, works, contributors):
        for work in works:
            work.update({'contributors': contributors})
            orcid_work = ORCiDWork(**work)
            json_work = orcid_work.create_json()
            assert json.loads(json_work) # tests for valid JSON