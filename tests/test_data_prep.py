import pytest
from orcid.lyterati_utils import Lyterati
from orcid.orcid import ORCiDWork, ORCiDBatch
import json
from dataclasses import asdict


@pytest.fixture
def user_id():
    return 'G123456789'

@pytest.fixture
def orcid():
    return '9999-9999-9999-9999'
    
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
    return [
            { 'title': 'A fascinating monograph',
            'container': 'Oxfurred University Press',
            'work_type': 'book',
            'pub_year': '2000',
            'orcid': '9999-9999-9999-9999',
            'user_id': 'G123456789' },
            { 'title': 'A fascinating article',
             'container': 'Journal of Fascinating Ideas',
             'work_type': 'article',
             'pub_year': '1994',
             'external_id_type': 'doi',
             'external_id': 'fake-doi-9999',
             'external_id_url': 'https://doi.org/fake-doi-9999',
             'orcid': '9999-9999-9999-9999',
             'user_id': 'G123456789' }
            ]

@pytest.fixture
def openalex_work():
    return { 'title': 'A fascinating article',
             'container': 'Journal of Fascinating Ideas',
             'work_type': 'article',
             'pub_year': '1994',
             'external_id_type': 'doi',
             'external_id': 'fake-doi-9999',
             'external_id_url': 'https://doi.org/fake-doi-9999',
             '_index': 1 }

@pytest.fixture
def orcid_works(works, contributors):
    orcid_works = []
    for i, work in enumerate(works):
        work.update({ 'contributors': contributors, '_index': i })
        orcid_works.append(ORCiDWork(**work))
    return orcid_works

@pytest.fixture
def orcid_batch(orcid_works):
    return ORCiDBatch(user_id, orcid).add_works(orcid_works)

class TestLyterati:

    def test_load_files(self, user_id, file_path):
        lyterati = Lyterati(user_id=user_id, file_path=file_path)
        assert lyterati.user_data[0]['user_id'] == user_id
        assert len(lyterati.user_data) == 2
        assert lyterati.user_data[1]["title"] == 'Fascinating problems in fascinating literature'
        assert { k for record in lyterati.user_data for k in record.keys() } == {'user_id', 'title', 'publisher', 'authors', 'start_year','file_name', '_index'}
        assert lyterati.user_name == {'first_name': 'Jeremy', 'last_name': 'Fisher'}

class TestORCiDWorK:

    def test_split_authors(self, author_names):
        author_str_and = ' and '.join(author_names)
        author_str_with = ' with '.join(author_names)
        author_str_comma = ', '.join(author_names)
        for author_str in [author_str_and, author_str_with, author_str_comma]:
            assert ORCiDWork.split_authors(author_str) == author_names

    def test_create_valid_json(self, orcid_works):
        for orcid_work in orcid_works:
            json_work = orcid_work.create_json()
            assert json.loads(json_work) # tests for valid JSON

    def test_create_orcid_dict(self, orcid_works):
        for work in orcid_works:
            assert set(work.to_dict().keys()) >= { 'title', 'container', 'contributors', 'work_type', 'pub_year', 'orcid',
                                                  'user_id', 'pub_month', 'pub_day', 'external_id', 'external_id_type', 'external_id_url', 'url', '_work_id', '_index' }
    
    def test_create_oa_work(self, openalex_work, contributors, user_id, orcid):
        openalex_work.update({ 'contributors': contributors })
        orcid_work = ORCiDWork.create_from_source(openalex_work, source='open_alex', user_id=user_id, orcid=orcid)
        assert orcid_work.title == openalex_work['title']
        assert orcid_work.work_type == 'journal-article'
        assert orcid_work.orcid == orcid
        assert orcid_work.contributors[0]['name'] == 'Beatrix Potter'
        assert orcid_work._metadata_source == 'open_alex'
    
class TestORCiDBatch:
    
    def test_create_csv(self, orcid_batch):
        print(orcid_batch.to_csv().getvalue())

