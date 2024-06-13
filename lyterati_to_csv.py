from lyterati_utils import Lyterati
from external_sources import OpenAlexClient
import click
import json
import pandas as pd

@click.command()
@click.argument('path_to_files')
@click.argument('user_id')
def lyterati_to_csv(path_to_files, user_id):
    '''Given a path to XML Lyterati data files and a user ID, retrieves records for that ID from the XML files, queries OpenAlex for external identifiers, and prepares a CSV of the data.'''
    # subset of work files
    work_files = ['fis_acad_articles.xml', 'fis_article_abstracts.xml', 'fis_articles.xml', 'fis_books.xml', 'fis_chapters.xml', 'fis_conference_papers.xml', 'fis_presentations.xml', 'fis_reports.xml', 'fis_reviews.xml']
    # move to .env
    gwu_ror = 'https://ror.org/00y4zzh67'
    email_address = 'dsmith@gwu.edu'
    lyterati = Lyterati(user_id, path_to_files, subset=work_files)
    open_alex = OpenAlexClient(gwu_ror, email_address)
    author_data = open_alex.get_author_ids(' '.join(lyterati.user_name.values()))
    # TO DO: 
    # If only one result, use the OpenAlex ID
    # Check ORCiD in results against ORCiD linked to account
    # Flag if they don't match
    # If more than one result, look for a matching ORCiD and use that OpenAlex ID
    # If none match, don't use
    author_ids = [ { 'id_type': 'openalex_id',
                    'id_value': author_data['results'][0]['id'] },
                   { 'id_type': 'orcid',
                     'id_value': author_data['results'][0].get('orcid') }
                ]
    lyterati.update_with_author_ids(author_ids)
    # filter out conference presentations and papers (likely not to have DOI's)
    lyterati_works = [ record for record in lyterati.user_data 
                      if record['file_name'] not in ('fis_presentations.xml', 'fis_conference_papers.xml') ]

    titles = [ record['title'] for record in lyterati_works ]
    years = [ record['start_year'] for record in lyterati_works ]
    indices = [ record['index'] for record in lyterati_works ]
    oa_results = [ (index, result) for result, index in zip(open_alex.get_works(author_id=lyterati.author_ids['openalex_id'],
                                                                                titles=titles,
                                                                                years=years), indices) if result ]
    oa_metadata = []
    for index, result in oa_results:
        work = open_alex.extract_metadata(result)
        if work:
            work['index'] = index
            oa_metadata.append(work)
    


    

if __name__ == '__main__':
    lyterati_to_csv()