import pytest
from lyterati_utils import Lyterati


@pytest.fixture
def user_id():
    return 'G123456789'
    
@pytest.fixture
def file_path():
    return './tests'

class TestLyterati:

    def test_load_files(self, user_id, file_path):
        lyterati = Lyterati(user_id=user_id, file_path=file_path)
        assert lyterati.user_data[0]['gw_id'] == user_id
        assert len(lyterati.user_data) == 2
        assert lyterati.user_data[1]["title"] == 'Fascinating problems in fascinating literature'
        assert { k for record in lyterati.user_data for k in record.keys() } == {'gw_id', 'title', 'publisher', 'authors', 'start_year','file_name'}