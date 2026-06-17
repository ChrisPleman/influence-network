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
        # No trailing slash: endpoint function appends identifier + '.json'
        'search': 'https://projects.propublica.org/nonprofits/api/v2/search',
        'organization': 'https://projects.propublica.org/nonprofits/api/v2/organizations/'
    },
    'FEC': {
        'root': 'https://api.open.fec.gov/v1/',
        'committees': 'https://api.open.fec.gov/v1/committees/',
        'schedule_a': 'https://api.open.fec.gov/v1/schedules/schedule_a/',
        'schedule_b': 'https://api.open.fec.gov/v1/schedules/schedule_b/',
        'schedule_e': 'https://api.open.fec.gov/v1/schedules/schedule_e/'
    },
    'OpenSecrets': {
        # Single parameterized root; pass method= in request params.
        # Apply for an API key at: https://www.opensecrets.org/api/admin/apikey/request
        'root': 'https://www.opensecrets.org/api/'
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


def propublica_endpoint(endpoint_key: str, identifier: str = '') -> str:
    '''Return the specific ProPublica Nonprofit Explorer API endpoint.

    For search: propublica_endpoint('search')            -> .../search.json
    For org:    propublica_endpoint('organization', ein) -> .../organizations/EIN.json
    '''
    return endpoints['ProPublica'][endpoint_key] + identifier + '.json'


def fec_endpoint(endpoint_key: str) -> str:
    '''Return the specific openFEC API endpoint.'''

    return endpoints['FEC'][endpoint_key]


def opensecrets_endpoint(endpoint_key: str = 'root') -> str:
    '''Return the OpenSecrets API root endpoint.

    All OpenSecrets API calls use the root URL with a 'method' query parameter.
    Apply for an API key at: https://www.opensecrets.org/api/admin/apikey/request
    '''
    return endpoints['OpenSecrets'][endpoint_key]
