'''Description: This script scrapes the Google Scholar profile 
                of the author and extracts the publication details.'''

import os
import json
import typing
import re
import requests
from bs4 import BeautifulSoup

# Global settings
PUBLICATIONS_JSON = '/app/publications.json'
GOOGLE_SCHOOLAR_URL = 'https://scholar.google.com/citations?user={}&cstart={}&pagesize={}'
HEADERS = {
    'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        + 'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# Global dictionary to store the publications
parsed_pubs = {}

class Publication:
    '''
    Class to store the publication details.
    '''

    title: str
    url: str
    authors: str
    journal: str
    pages: str
    pub_date: str

    def __init__(self, title: str, url: str):
        self.title = title
        self.url = url
        self.authors = ""
        self.journal = ""
        self.pages = ""
        self.pub_date = ""

    def to_dict(self):
        '''
        Returns the publication details as a dictionary.
        '''
        return {
            'title': self.title,
            'url': self.url,
            'authors': self.authors,
            'journal': self.journal,
            'pages': self.pages,
            'pub_date': self.pub_date
        }

    def __str__(self) -> str:
        return f'{self.title} - {self.url} - {self.authors} - {self.journal} - {self.pages} - {self.pub_date}'

    def is_valid(self) -> bool:
        '''
        Checks if the publication is valid.
        '''

        if not (self.title and self.url and self.authors and self.journal and self.pages and self.pub_date):
            return False

        if not re.match(r'^\d+(-\d+)?$', str(self.pages)):
            return False

        if not re.match(r'^\d{4}$', str(self.pub_date)):
            return False

        if self.pages == self.pub_date:
            return False

        return True


def parse_google_scholar_entry(item: BeautifulSoup) -> Publication:
    '''
    Parses the Google Scholar entry and returns the publication details.
    Args:
        soup: BeautifulSoup object of the Google Scholar page.
    Returns:
        Publication instance with publication details.
    '''

    try:
        publication_url = item.select_one('.gsc_a_t a')
        publication_title = publication_url.text.strip() if publication_url else None
        publication_url = f'https://scholar.google.com{publication_url["href"]}' if publication_url else None
        details = item.select('.gs_gray')
        publication_authors = details[0].text.strip() if details else None
        publication_journal = details[1].text.strip() if len(
            details) > 1 else None
        year = item.select_one('.gsc_a_y span')
        publication_year = year.text.strip() if details else None

        if (publication_title is not None) and (publication_url is not None):
            pub = Publication(publication_title, publication_url)

            if publication_authors:
                pub.authors = publication_authors

            journal_details = publication_journal.split(',')
            print(journal_details)
            if journal_details and len(journal_details) > 1:
                pub.journal = journal_details[0].strip()
                pub.pages = journal_details[1].strip()

            if publication_year:
                pub.pub_date = publication_year

        return pub

    except Exception as e:
        print(f'Error while parsing Google Scholar entry: {e}')
        return None


def fetch_google_scholar(author_name: str) -> typing.List[dict]:
    '''
    Fetches the data from Google Scholar for the given author name.
    Args:
        author_name: Name of the author to fetch the data for.
    Returns:
        List of publications for the given author.
    '''

    _data = []
    cstart = 0
    pagesize = 100

    url = GOOGLE_SCHOOLAR_URL.format(author_name, cstart, pagesize)
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        try:
            for item in soup.select('#gsc_a_b .gsc_a_tr'):
                publication = parse_google_scholar_entry(item)

                if publication is not None:
                    print(f'Publication: {publication.title}')
                    if publication.title not in parsed_pubs.keys():
                        parsed_pubs[publication.title] = publication.to_dict()
                        print(
                            f' +++ The publication is valid: {publication.is_valid()}')
                        if publication.is_valid():
                            _data.append(publication.to_dict())
                    else:
                        print(' +++ The publication is already in the list')
        except Exception as e:
            print(f'Error while parsing Google Scholar page: {e}')

    return _data


# List of author names
author_names = ['t-vbHCoAAAAJ', 'OjFQpxIAAAAJ',
                'u8h7OSYAAAAJ', 'KgkltygAAAAJ', 'lOHxkQUAAAAJ']

# Get current publication
if os.path.exists(PUBLICATIONS_JSON):
    with open(PUBLICATIONS_JSON, 'r', encoding='utf-8') as file:
        publications = json.load(file)
else:
    publications = []

# Fetch data for each author
for name in author_names:
    data = fetch_google_scholar(name)

    if data:
        publications.extend(data)
        with open(PUBLICATIONS_JSON, 'w', encoding='utf-8') as file:
            json.dump(publications, file, indent=2)
           
    print(f'Nº of Publications: {len(publications)}')

print("Fetching data completed.")
