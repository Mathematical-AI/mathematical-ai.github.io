"""
Convert a bibtex library into a YAML library which 
can be used on the website. To do this, use the code

```python
from convert_bibtex import convert_library

convert_library(
    'references.bib',  # Input file name
    'references.yml',  # Output file name
    generate_citekeys=True  # or False if preferred
)
```
"""

import bibtexparser
import bibtexparser.middlewares as m
import yaml


known_acronyms = {
    'ACM',
    'ASE',
    'CDC',
    'DSS',
    'HPCC',
    'IAI',
    'ICML',
    'IEEE',
    'IFAC',
    'IJCNN',
    'NeurIPS',
    'PLoS ONE',
    'SIAM'
}


def load_library(filepath):
    """
    Load a Bibtex file using the bibtexparser library
    with some pre-set options.
    """
    name_fields = (
        'author', 'AUTHOR', 'Author',
        'editor', 'EDITOR', 'Editor',
        'translator', 'TRANSLATOR', 'Translator'
    )

    layers = [
        m.MonthIntMiddleware(True), # Months should be represented as int (0-12)
        m.SeparateCoAuthors(True, name_fields=name_fields), # Co-authors should be separated as list of strings
        m.SplitNameParts(True, name_fields=name_fields) # Individual Names should be split into first, von, last, jr parts
    ]

    return bibtexparser.parse_file(filepath, append_middleware=layers)


def parse_entry(entry):
    """
    Process an entry provided by tbe bibtexparser library
    into a dictionary which can be worked with more easily
    """
    entry_dict = {k.lower(): v for k, v in entry.fields_dict.items()}
    entry_dict['type'] = entry.entry_type
    entry_dict['citekey'] = entry.key
    for key in {'author', 'title', 'year', 'url', 'doi'}:
        if key in entry_dict:
            entry_dict[key] = entry_dict[key].value
    entry_dict['author_parts'] = entry_dict['author']
    entry_dict['author'] = extract_authors(entry_dict)
    return entry_dict


def extract_authors(entry_dict):
    """
    Extract and format the authors discovered by the library.
    Converts them into a list of strings where each name is
    formatted in the unified manner 'J. A. Bloggs'.
    """
    authors = entry_dict['author']
    author_names = []
    for a in authors:
        s = ''
        for i, forename in enumerate(a.first):
            s += forename[0] + '.'
            if i + 1 < len(a.first):
                s += ' '
        if len(a.von) > 0:
            for v in a.von:
                s += ' ' + v
        for l in a.last:
            s += ' ' + l
        if len(a.jr) > 0:
            for j in a.jr:
                s += ' ' + j
        author_names.append(s)
    
    return author_names


def clean_string(string):
    """
    Remove certain whitespace or unneccessary characters from a string
    """
    return string.strip().replace('\n', '').replace('    ', ' ').replace('   ', ' ').replace('  ', ' ').replace('{', '').replace('}', '').replace('`', '\'')


def doi_to_link(doi: str):
    """
    Convert a DOI into a link using the doi.org format
    """
    if doi.startswith('http'):
        return doi
    if doi.startswith('doi.org'):
        return 'https://' + doi
    
    return 'https://doi.org/' + doi


def acronym_formatter(name):
    """
    A hack to preserve acronyms when changing the case of
    a string. This relies on the list of 'known acronyms' 
    at the top of the file.
    """
    for ac in known_acronyms:
        name = name.replace(ac.title(), ac)
    return name.replace('Th ', 'th ').replace('St ', 'st ').replace('Nd ', 'nd')


def citekey_generator(entry):
    """
    Automatically generate a human-friendly citekey for a record,
    in the format
    <first author name><year>-<title word 1>-<title word 2>-<title word 3>
    """
    first_auth = entry['author_parts'][0]
    year = entry['year']
    title = entry['title']
    first_auth_ln = ''
    for name in first_auth.last:
        first_auth_ln += name
    citekey_base = first_auth_ln + str(year)
    title_words = ''
    for i, word in enumerate(title.replace('-', ' ').replace(':', '').split(' ')):
        if i > 2:
            break
        title_words += '-' + word.lower()
    return citekey_base + title_words


def parse_basic_info(entry, generate_citekey):
    """
    Extract some basic information from a record, which
    is common to all different types of publications. 
    Namely: citekey, authors, title, year, doi, link
    """
    if generate_citekey:
        citekey = citekey_generator(entry)
    else:
        citekey = entry['citekey']
    authors = [clean_string(a) for a in entry['author']]
    title = clean_string(entry['title'])
    year = int(entry['year'])

    if title == title.upper():
        title = title.title()

    data = {
        'citekey': citekey,
        'authors': authors,
        'title': title,
        'year': year,
    }
    
    if 'doi' in entry:
        doi = doi_to_link(entry['doi'])
        data['doi'] = doi

    if 'url' in entry:
        link = entry['url'] 
        data['link'] = link
    elif 'doi' in entry:
        data['link'] = doi
    
    return data


def parse_journal_article(entry, generate_citekey):
    """
    Extract the information required for a journal article
    from a bibtex library entry. This information is returned
    as a dictionary.
    If generate_citekey is True, then the citekey in the bibtex
    file will be discarded and a new one will be autogenerated.
    """
    basic_info = parse_basic_info(entry, generate_citekey)

    journal = acronym_formatter(clean_string(entry['journal'].value).title())
    extra = ''

    if 'volume' in entry:
        volume = entry['volume'].value
        extra += volume

    if 'number' in entry:
        number = entry['number'].value
        extra += '(' + number + ')'

    if 'pages' in entry:
        pages = entry['pages'].value
        extra += ', pages ' + pages

    return basic_info | {
        'venue': journal,
        'extra': extra,
        'type': 'journal'
    }


def parse_proceedings_article(entry, generate_citekey):
    """
    Extract the information required for a conference 
    proceedings article from a bibtex library entry. 
    This information is returned as a dictionary.
    If generate_citekey is True, then the citekey in the bibtex
    file will be discarded and a new one will be autogenerated.
    """
    basic_info = parse_basic_info(entry, generate_citekey)

    venue = acronym_formatter(clean_string(entry['booktitle'].value).title())

    return basic_info | {
        'venue': venue,
        'type': 'proceedings'
    }


def ensure_unique_citekey(record, existing_citekeys):
    """
    Updates a record to make sure that its citekey
    doesn't clash with any citekey present in the
    container existing_citekeys. This is achieved by 
    adding a number to the end of the original key.
    """
    citekey = citekey_base = record['citekey']
    i = 1
    while citekey in existing_citekeys:
        citekey = citekey_base + '-' + str(i)
        i += 1
    record['citekey'] = citekey


def convert_library(
        bibtex_filepath, 
        output_filepath, 
        generate_citekeys=False
):
    """
    Convert a bibtex library into a YAML library.
    If generate_citekey is True, then the citekeys in the bibtex
    file will be discarded and new ones will be autogenerated.
    """
    library = load_library(bibtex_filepath)
    entries = []
    citekeys = set()
    for entry in library.entries:
        record = parse_entry(entry)
        etype = record['type']
        if etype == 'article':
            data = parse_journal_article(record, generate_citekey=generate_citekeys)
            ensure_unique_citekey(data, citekeys)
            citekeys.add(data['citekey'])
            entries.append(data)
        elif etype == 'inproceedings':
            data = parse_proceedings_article(record, generate_citekey=generate_citekeys)
            ensure_unique_citekey(data, citekeys)
            citekeys.add(data['citekey'])
            entries.append(data)
        else:
            print(f'Unable to parse record with type "{etype}" and citekey "{record["citekey"]}"')

    articles = list(filter(lambda e: e['type'] == 'journal', entries))
    proceedings = list(filter(lambda e: e['type'] == 'proceedings', entries))

    print(f'Processed {len(articles)} journal and {len(proceedings)} proceedings articles.')

    with open(output_filepath, 'w') as file:
        print(f'# Automatically converted from bibtex file {bibtex_filepath}', file=file)
        print('', file=file)
        print('# Conference proceedings articles', file=file)
        yaml.dump(proceedings, file, allow_unicode=True, sort_keys=False, width=float("inf"))
        print('', file=file)
        print('# Journal articles', file=file)
        yaml.dump(articles, file, allow_unicode=True, sort_keys=False, width=float("inf"))

    print('YAML library exported to', output_filepath)


if __name__ == '__main__':
    convert_library('ivan_references.bib', 'references.yml', generate_citekeys=True)
