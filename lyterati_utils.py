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
        self.user_df = pd.DataFrame.from_records(self.user_data)
        
    
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
        for file in source_files:
            doc = etree.parse(file, parser=Lyterati.parser)
            rows = doc.xpath(f'//row[field/@name="gw_id" and field/text() = "{user_id}"]')
            for row in rows:
                fields = row.xpath("field")
                row_dict = {f.get("name"): f.text for f in fields}
                row_dict.update({"file_name": file.name})
                records.append(row_dict)
        return records