from dataclasses import dataclass, field
from typing import Optional
import re
from jinja2 import Environment, PackageLoader
import uuid

def finalize(value):
    '''
    Ensures that Jinja passes an empty string and "None" where None is set in the Python object
    '''
    return value if value is not None else ''

L2O_MAPPING = {'column': {column: 'publisher' for column in ['publisher',
                                                                            'publication_venue', 
                                                                            'conference', 
                                                                            'event', 
                                                                            'distributor']},
               'filename': {}}

ENV = Environment(
    loader=PackageLoader(package_name='orcid', package_path='schemas'),
    finalize=finalize
)

@dataclass
class ORCiDWork:
    '''
    Class for all ORCiD work types
    '''
    title: str                              # work title
    container: str                          # publisher, journal title, etc.
    contributors: list[dict[str, str]]      # author names, possibly with ORCiD and sequence indicator
    work_type: str                          # ORCiD work type
    pub_year: str                           # publication year
    pub_month: Optional[str] = None         # possible publication month
    pub_day: Optional[str] = None           # possible day of publication
    external_id_type: Optional[str] = None  # possible external ID type, from among those recognized by the ORCiD API
    external_id: Optional[str] = None       # possible external ID, e.g., DOI
    external_id_url: Optional[str] = None   # possible URL (for DOI)
    _work_id: uuid.UUID = field(default_factory=uuid.uuid4) # internal ID for works; used in creating ORCiD records without DOI's

    template = ENV.get_template('work-full-3.0.json') # template for works

    @staticmethod
    def split_authors(authors_str: str) -> list[str]:
        # Split the input string by comma, &, with, and
        authors = re.split(r',|&|\s+with\s+|\s+and\s+', authors_str, flags=re.IGNORECASE)
        # Strip leading/trailing whitespace from each name and convert to title case if necessary
        return [author.strip() for author in authors if author.strip()]
      
    def create_json(self):
       return ORCiDWork.template.render(work=self) 