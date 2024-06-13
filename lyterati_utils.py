from lxml import etree
from pathlib import Path
from typing import Optional
import pandas as pd

class Lyterati:

    parser = etree.XMLParser(recover=True)

    def __init__(self, 
                 user_id: str, 
                 file_path: str = None, 
                 subset: Optional[list[str]] = None):
        
        '''
        Handles importing of data from Lyterati source. 
        :param user_id: ID of user whose Lyterati records should be returned
        :param file_path: if given, a path to the data (presumed XML) on disk
        :param subset: a list of Lyterati files to include; if omitted, records from all files are returned
        '''
        self.user_id = user_id
        
        if file_path:
            self.user_data = Lyterati.load_data_from_files(user_id, file_path, subset)
            # The fis_faculty.xml contains the name of the user associated with the provided user ID
            self.user_metadata = Lyterati.load_data_from_files(user_id, file_path, subset=['fis_faculty.xml'])
        # Extract the name elements associated with this user
        # Assumes one record per user 
        self.user_name = {'first_name': self.user_metadata[0]['first_name'],
                     'last_name': self.user_metadata[0]['last_name']}
    
        self.author_ids = {}
    
    def update_with_author_ids(self, author_ids: list[dict[str, str]]):
        '''
        :param author_ids: each dict should include id_type and id_value as keys.
        '''
        for author_id in author_ids:
            self.author_ids.update({ author_id['id_type']: author_id['id_value'] })

    @staticmethod
    def load_data_from_files(user_id: str, 
                  file_path: str, 
                  subset: Optional[list[str]] = None) -> list[dict[str, str]]:
        '''
        Return a set of Lyterati records from XML files (subset or all). The @name attribute of each <field> element is mapped to a key of the included dict. 
        '''
        source_files = list(Path(file_path).glob('*.xml'))
        if subset:
            source_files = [ file for file in source_files if file.name in subset ]
        records = []
        index = 0 # unique index for each record
        for file in source_files:
            # Skip the file of basic information, as we capture this separately
            if not subset and (file.name == 'fis_faculty.xml'):
                continue
            doc = etree.parse(file, parser=Lyterati.parser)
            rows = doc.xpath(f'//row[field/@name="gw_id" and field/text() = "{user_id}"]')
            for row in rows:
                fields = row.xpath("field")
                row_dict = {f.get("name"): f.text for f in fields}
                row_dict.update({"file_name": file.name, 
                                 'index': index})
                index += 1
                records.append(row_dict)
        return records