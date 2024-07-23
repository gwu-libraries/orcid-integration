from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Optional, Type, Callable
from jinja2 import Environment, PackageLoader
from datetime import datetime
from io import StringIO
from itertools import groupby
import re, uuid
import pandas as pd


def finalize(value):
    '''
    Ensures that Jinja passes an empty string and "None" where None is set in the Python object
    '''
    return value if value is not None else ''

ENV = Environment(
    loader=PackageLoader(package_name='orcid', package_path='schemas'),
    finalize=finalize
)

@dataclass
class ORCiDWork:
    '''
    Class for all ORCiD work types
    '''
    title: str                                      # work title
    container: str                                  # publisher, journal title, etc.
    contributors: list[dict[str, str]]              # author names, possibly with ORCiD and sequence indicator
    work_type: str                                  # ORCiD work type
    pub_date: ORCiDFuzzyDate                        # publication date
    orcid: str                                      # The ORCiD associated with the user whose work this is
    user_id: str                                    # The (internal) ID of the user associated with this work
    external_id_type: Optional[str] = None          # possible external ID type, from among those recognized by the ORCiD API
    external_id: Optional[str] = None               # possible external ID, e.g., DOI
    external_id_url: Optional[str] = None           # possible URL (for DOI)
    url: Optional[str] = None                       # possible URL for work
    _work_id: uuid.UUID = field(default_factory=uuid.uuid4) # internal ID for works; used in creating ORCiD records without DOI's
    _index: Optional[int] = None                    # Used for identifying possible duplicates when creating a sorted list of results
    _metadata_source: Optional[str] = None          # To indicate the external source for the data (lyterati, open_alex)


    template = ENV.get_template('work-full-3.0.json') # template for works

    # mappinng fields from Lyterati to ORCiD
    LYTERATI_FIELD_MAPPING = { field: 'container' for field in [ 'publisher',
                                                                'publication_venue', 
                                                                'conference', 
                                                                'event', 
                                                                'distributor' ]}
   
    LYTERATI_TYPE_MAPPING = { 'acad_articles': 'journal-article',
                             'articles': 'journal-article',
                             'article_abstracts': 'journal-article',
                             'books': 'book',
                             'chapters': 'book-chapter',
                             'conf_papers': 'conference-paper',
                             'presentations': 'lecture-speech',
                             'reports': 'report',
                             'reviews': 'book-review' }
    # https://api.openalex.org/works?group_by=type
    OPENALEX_TYPE_MAPPING = { 'article': 'journal-article',
                             'book-chapter': 'book-chapter',
                             'book': 'book',
                             'dataset': 'data-set',
                             'dissertation': 'disseration',
                             'preprint': 'preprint',
                             'reference-entry': 'encyclopaedia-entry',
                             'review': 'book-review',
                             'report': 'report',
                             'other': 'other',
                             'peer-review': 'review',
                             'standard': 'standards-and-policy',
                             'editorial': 'other',
                             'erratum': 'other',
                             'letter': 'other',
                             'supplementary-materials': 'other'   }

    @staticmethod
    def split_authors(authors_str: str) -> list[str]:
        # Split the input string by comma, &, with, and
        # Return empty string for None
        if not authors_str:
            return ''
        authors = re.split(r',|&|\s+with\s+|\(\s*with\s+|\s+and\s+|\(and\s+', authors_str, flags=re.IGNORECASE)
        # Strip leading/trailing whitespace from each name and convert to title case if necessary
        return [author.strip().replace(')', '') for author in authors if author.strip()]

    @classmethod
    def create_from_source(cls, 
                           record: dict[str, str], 
                           source: str, 
                           orcid: str, 
                           user_id: str, 
                           user_name: dict[str, str] = None) -> Type[ORCiDWork]:
        '''
        Instantiates an ORCiDWork from another data source.
        :param record: it is expected that this record contain an index field for sorting/identifying duplicates
        :param source: either 'lyterati' or 'openalex'
        :param orcid: the user's ORCiD associated with this work
        :param user_id: the user's internal ID
        :param user_name: the user's name (from Lyterati, with first_name and last_name as keys)
        '''
        if not source in ( 'lyterati', 'open_alex' ):
            return
        orcid_work = { 'user_id': user_id,
                       'orcid': orcid }
        orcid_date = ORCiDFuzzyDate()
        for field, value in record.items():
            match (field, source):
                case ('file_name', 'lyterati'):
                    orcid_work['work_type'] = cls.LYTERATI_TYPE_MAPPING[value.replace('fis_', '').replace('.xml', '')]
                case ('authors', 'lyterati'):
                    contributors =  [{ 'name': name } for name in cls.split_authors(value) ]
                    orcid_work['contributors'] = contributors
                case ('work_type', 'open_alex'):
                    orcid_work['work_type'] = cls.OPENALEX_TYPE_MAPPING[value]
                case (lyterati_field, 'lyterati') if lyterati_field in cls.LYTERATI_FIELD_MAPPING.keys():
                    orcid_field = cls.LYTERATI_FIELD_MAPPING[lyterati_field]
                    orcid_work[orcid_field] = value
                case (('start_month' | 'start_year'), 'lyterati'):
                    key = field.split('_')[1]
                    setattr(orcid_work, key, value)
                case ('pub_date', 'open_alex'):
                    orcid_date.add_date(value)
                case _:
                    orcid_work[field] = value
        # if the Lyterati field is empty, populate with just the Lyterati user's name
        if not orcid_work.get('contributors'):
            orcid_work['contributors'] = [{ 'name': f'{user_name["first_name"]} {user_name["last_name"]}' }]
        orcid_work['_metadata_source'] = source
        orcid_work['pub_date'] = orcid_date
        return ORCiDWork(**orcid_work)

    
    def create_json(self):
       return ORCiDWork.template.render(work=self) 
    
    def to_dict(self) -> dict[str, str]:
        '''
        Returns a dictionary representation of an instance, where the instance attributes correspond to columns. Flattens the contributors element, creating semicolon-delimited strings.
        '''
        obj_dict = asdict(self)
        obj_dict['contributors'] = ';'.join([ c['name'] for c in obj_dict['contributors'] ])
        return obj_dict        

class ORCiDBatch:
    '''
    Class for creating a batch of ORCiD works
    '''
    CSV_FIELDS = [ 'work_number', 'title', 'contributors', 'container', 'pub_year', 'pub_month', 'pub_day', 'work_type', 'doi', 'use_this_version', 'metadata_source']
    # for use in labeling duplicates
    PREFERRED_METADATA_SOURCE = 'open_alex'

    def __init__(self, user_id: str, orcid: str):
        '''
        Creates a new batch of ORCiD works associated with the provided user ID and ORCiD. Creates a unique identifier for this batch.
        '''
        self.user_id = user_id
        self.orcid = orcid
        self.batch_id = f'{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}_{self.orcid}'
    
    def add_works(self, works: list[Type[ORCiDWork]]):
        '''
        Adds a list of instances of the ORCiDWork class to the batch. Each work is assumed to have the ._index attribute for sorting
        '''
        self.works = works
        return self
    
    @classmethod
    def groupby_size_and_label(cls, df: Type[pd.DataFrame]) -> Type[pd.DataFrame]:
        '''
        Helper function to group duplicate works and flag the preferred datasource for duplicates
        '''
        df['size'] = len(df)
        if len(df) == 1:
            df['use_this_version'] = True
        else:
            df.loc[df._metadata_source == cls.PREFERRED_METADATA_SOURCE, 'use_this_version'] = True
        return df

    def flatten(self) -> Type[pd.DataFrame]:
        '''
        Formats the batch of ORCiD works as a DataFrame. Uses the _index attribute of each work for sorting and flagging duplicates.
        '''
        # Create a DataFrame of ORCiDWOrk instances, using the empty string for nulls
        works_df = pd.DataFrame.from_records([ work.to_dict() for work in self.works ]).fillna('')

        # sort so that duplicates works appear before unduplicated works and label preferred versions
        # explicitly passing all columns to avoid deprecation warning from pandas about group keys being excluded
        works_df = works_df.groupby('_index')[works_df.columns].apply(ORCiDBatch.groupby_size_and_label)

        works_df = works_df.rename(columns={ 'external_id': 'doi', 
                                            '_metadata_source': 'metadata_source',
                                             '_index': 'work_number' }).sort_values(['size', 'work_number'], ascending=False)
        return works_df[ORCiDBatch.CSV_FIELDS]

    def to_csv(self):
        '''Returns a flattened version of the batch of works as a CSV (string buffer) '''
        # Buffer for file output
        output = StringIO()
        self.flatten().to_csv(output, index=False)
        return output
            
           
@dataclass
class ORCiDAffiliation:
    '''
    Class for all ORCiD data types using the common:affiliation element (see https://github.com/ORCID/orcid-model/blob/master/src/main/resources/common_3.0/common-3.0.xsd)
    '''
    department_name: str                         
    role_title: str
    start_date: str


class ORCiDFuzzyDate:
    '''
    Utility class for creating elements using the common:fuzzy-date element (see https://github.com/ORCID/orcid-model/blob/master/src/main/resources/common_3.0/common-3.0.xsd)
    '''

    valid_year = re.compile(r'\d{4}')
    valid_date_part = re.compile(r'\d{2}')


    def __init__(self, year: str = None, month: str = None, day: str = None):
        '''
        Stores a date using separate attributes for year, month, and day
        '''
        self._year = year
        self._month = month
        self._day = day
    
    def validate(self, obj, obj_type):
        if not obj:
            return
        obj = str(obj).zfill(2)
        try:
            match obj_type:
                case 'year' if ORCiDFuzzyDate.valid_year.match(obj):
                    year = int(obj)
                    if year >= 1900 and year <= 2100:
                        return obj
                case 'month' if ORCiDFuzzyDate.valid_date_part.match(obj):
                    month = int(obj)
                    if month >= 1 and month <= 12 and self.year:
                        return obj
                case 'day' if ORCiDFuzzyDate.valid_date_part.match(obj):
                    day = int(obj)
                    if day >= 1 and day <= 31 and self.month:
                        return obj
                case _:
                    return 
        except TypeError:
            return None
    
    @property
    def year(self):
        return self.validate(self._year, 'year')
    
    @property
    def month(self):
        return self.validate(self._month, 'month')
    
    @property
    def day(self):
        return self.validate(self._day, 'day')
    
    def add_date(self, date_str: str):
        '''
        Parses a date string, expecting %Y-%m-%d format, and updates the instance field accordingly
        '''
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        self._year=date_obj.year
        self._month=date_obj.month
        self._day=date_obj.day

