import pytest
from lyterati_utils import Lyterati
from orcid import ORCiDWork


@pytest.fixture
def user_id():
    return 'G123456789'
    
@pytest.fixture
def file_path():
    return './tests'

@pytest.fixture
def author_names():
    return ['Beatrix Potter', 'Frank Chateaubriand']

class TestLyterati:

    def test_load_files(self, user_id, file_path):
        lyterati = Lyterati(user_id=user_id, file_path=file_path)
        assert lyterati.user_data[0]['gw_id'] == user_id
        assert len(lyterati.user_data) == 2
        assert lyterati.user_data[1]["title"] == 'Fascinating problems in fascinating literature'
        assert { k for record in lyterati.user_data for k in record.keys() } == {'gw_id', 'title', 'publisher', 'authors', 'start_year','file_name'}

class TestORCiD:

    def test_split_authors(self, author_names):
        author_str_and = ' and '.join(author_names)
        author_str_with = ' with '.join(author_names)
        author_str_comma = ', '.join(author_names)
        for author_str in [author_str_and, author_str_with, author_str_comma]:
            assert ORCiDWork.split_authors(author_str) == author_names

