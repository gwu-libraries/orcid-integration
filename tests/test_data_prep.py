import pytest
from orcid.lyterati_utils import Lyterati
from orcid.orcid import ORCiDWork, ORCiDBatch, ORCiDFuzzyDate
import json
from dataclasses import asdict
import requests_mock 
from orcid.external_sources import OpenAlexClient

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
            'pub_date': ORCiDFuzzyDate(year='2000'),
            'orcid': '9999-9999-9999-9999',
            'user_id': 'G123456789',
             '_metadata_source': 'lyterati' },
            { 'title': 'A fascinating article',
             'container': 'Journal of Fascinating Ideas',
             'work_type': 'article',
             'pub_date': ORCiDFuzzyDate(year='1994'),
             'external_id_type': 'doi',
             'external_id': 'fake-doi-9999',
             'external_id_url': 'https://doi.org/fake-doi-9999',
             'orcid': '9999-9999-9999-9999',
             'user_id': 'G123456789',
              '_metadata_source': 'open_alex' }
            ]

@pytest.fixture
def openalex_result():
    with open('./tests/oa_work.json') as f:
        return json.load(f)

@pytest.fixture
def openalex_work():
    return { 'title': 'Progress toward more fascinaing journal articles on topics of recurrent fascination',
             'container': 'arXiv (Cornell University)',
             'work_type': 'preprint',
             'pub_date': '2014-01-01',
             'external_id_type': 'doi',
             'external_id': 'https://doi.org/10.9999/999999',
             'url': 'https://arxiv.org/abs/99999999999',
             'contributors': [{ 'name': 'Beatrix Potter', 
                               'sequence': 'first', 
                               'orcid': 'https://orcid.org/0000-0000-0000-0000'
                               }]
            }

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

@pytest.fixture
def oa_client():
    gwu_ror = 'https://ror.org/00y4zzh67'
    email_address = 'dsmith@gwu.edu'
    return OpenAlexClient(gwu_ror, email_address)

@pytest.fixture
def orcid_csv():
    with open('./tests/orcid_to_review.csv') as f:
        return f.read()

@pytest.fixture()
def date():
    return {'2022-01-02': ('2022', '01', '02')}

@pytest.fixture()
def date_parts():
    return { ('2022', '1', '2'): ('2022', '01', '02'),
            (2022, 1, 2):('2022', '01', '02'),
            ('2022', '4'): ('2022', '04', None),
            ('2022', 'July', '10'): ('2022', None, None),
            ('2022', '20', '4'): ('2022', None, None),
            ('22', '4', '1'): (None, None, None)   }

class TestLyterati:

    def test_load_work_files(self, user_id, file_path):
        lyterati = Lyterati(user_id=user_id, file_path=file_path, subset='work_files')
        assert lyterati.user_data[0]['user_id'] == user_id
        assert len(lyterati.user_data) == 2
        assert lyterati.user_data[1]["title"] == 'Fascinating problems in fascinating literature'
        assert { k for record in lyterati.user_data for k in record.keys() } == {'user_id', 'title', 'publisher', 'authors', 'start_year','file_name', '_index'}
        assert lyterati.user_name == {'first_name': 'Jeremy', 'last_name': 'Fisher'}        
    
    def test_load_employment_files(self, user_id, file_path):
        lyterati = Lyterati(user_id=user_id, file_path=file_path, subset='employment_files')
        assert lyterati.user_data[0]['user_id'] == user_id
        assert len(lyterati.user_data) == 2
        assert lyterati.user_data[1]["title"] == 'Professor'
        assert { k for record in lyterati.user_data for k in record.keys() } == {'user_id', 'title', 'college', 'department', 'start_term', 'end_term', 'rank', 'file_name', '_index'}
        assert lyterati.user_name == {'first_name': 'Jeremy', 'last_name': 'Fisher'}
    
class TestOPenAlex:

   
    def test_open_alex_get_works(self, oa_client, works, openalex_result):
        with requests_mock.Mocker() as m:
            m.get(f'{OpenAlexClient.OPEN_ALEX_URL}/works', text=json.dumps(openalex_result))
            results = [r for r in oa_client.get_works(author_id='12345', titles=[works[0]['title']], years=['2014'])]
        assert len(results) == 1
    
    def test_open_alex_extract_metadata(self, oa_client, openalex_result, openalex_work):
        assert oa_client.extract_metadata(openalex_result) == openalex_work

class TestORCiDFuzzyDate:

    def test_add_date(self, date):
        ofd = ORCiDFuzzyDate()
        for _in, _out in date.items():
            ofd.add_date(_in)
            assert (ofd.year, ofd.month, ofd.day) == _out
    
    def test_validate_dates(self, date_parts):
        for _in, _out in date_parts.items():
            ofd = ORCiDFuzzyDate(*_in)
            assert (ofd.year, ofd.month, ofd.day) == _out



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
            assert set(work.to_dict().keys()) >= { 'title', 'container', 'contributors', 'work_type', 'pub_date', 'orcid',
                                                  'user_id', 'external_id', 'external_id_type', 'external_id_url', 'url', '_work_id', '_index' }
    
    def test_create_oa_work(self, openalex_work, user_id, orcid):
        orcid_work = ORCiDWork.create_from_source(openalex_work, source='open_alex', user_id=user_id, orcid=orcid)
        assert orcid_work.title == openalex_work['title']
        assert orcid_work.work_type == 'preprint'
        assert orcid_work.orcid == orcid
        assert orcid_work.contributors[0]['name'] == 'Beatrix Potter'
        assert orcid_work._metadata_source == 'open_alex'
    
class TestORCiDBatch:
    
    def test_create_csv(self, orcid_batch, orcid_csv):
        assert orcid_batch.to_csv().getvalue() == orcid_csv

