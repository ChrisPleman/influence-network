# Endpoint urls
endpoints = {
    'LDA': {
        'root': 'https://lda.senate.gov/api/v1/',
        'filings': 'https://lda.senate.gov/api/v1/filings/',
        'contributions': 'https://lda.senate.gov/api/v1/contributions/',
        'registrants': 'https://lda.senate.gov/api/v1/registrants/',
        'clients': 'https://lda.senate.gov/api/v1/clients/',
        'lobbyists': 'https://lda.senate.gov/api/v1/lobbyists/',
        'constants': {
            'filingtypes': 'https://lda.senate.gov/api/v1/constants/filing/filingtypes/',
            'lobbyingactivityissues': 'https://lda.senate.gov/api/v1/constants/filing/lobbyingactivityissues/',
            'governmententities': 'https://lda.senate.gov/api/v1/constants/filing/governmententities/',
            'countries': 'https://lda.senate.gov/api/v1/constants/general/countries/',
            'states': 'https://lda.senate.gov/api/v1/constants/general/states/',
            'prefixes': 'https://lda.senate.gov/api/v1/constants/lobbyist/prefixes/',
            'suffixes': 'https://lda.senate.gov/api/v1/constants/lobbyist/suffixes/',
            'itemtypes': 'https://lda.senate.gov/api/v1/constants/contribution/itemtypes/'
        }
    },
    'Congress': {
        'root': 'https://api.congress.gov/v3/',
        'bill': 'https://api.congress.gov/v3/bill/'
    },
    'ProPublica': {
        'root': 'https://projects.propublica.org/nonprofits/api/v2/',
        'search': 'https://projects.propublica.org/nonprofits/api/v2/search/',
        'organization': 'https://projects.propublica.org/nonprofits/api/v2/organizations/'
    }
}


def lda_endpoint(endpoint_key: str) -> str:
    '''Return the specific LDA API endpoint.'''
    if endpoint_key not in endpoints['LDA'].keys():
        return endpoints['LDA']['constants'][endpoint_key]

    return endpoints['LDA'][endpoint_key]


def congress_endpoint(endpoint_key: str) -> str:
    '''Return the specific Congress.gov API endpoint.'''

    return endpoints['Congress'][endpoint_key]


def propublica_endpoint(endpoint_key: str, search_method: str) -> str:
    '''Return the specific ProPublica API endpoint.'''

    return endpoints['ProPublica'][endpoint_key] + search_method + '.json'
