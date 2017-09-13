import requests
import singer
from .singer.tap import Tap
from .streams import CurrenciesStream, DealsStream, NotesStream, ActivityTypesStream, FiltersStream
from .config import BASE_URL, CONFIG_DEFAULTS
from .exceptions import InvalidResponseException


logger = singer.get_logger()


class PipedriveTap(Tap):
    streams = [
        CurrenciesStream(),
        DealsStream(),
        NotesStream(),
        ActivityTypesStream(),
        FiltersStream()
    ]

    def get_default_config(self):
        return CONFIG_DEFAULTS

    def iterate_response(self, response):
        payload = response.json()
        return payload['data']

    def execute_request(self, stream):
        headers = {
            'User-Agent': self.config['user-agent']
        }
        params = {
            'api_token': self.config['api_token'],
            'start': stream.start,
            'limit': stream.limit
        }
        url = "{}/{}".format(BASE_URL, stream.endpoint)
        logger.info('Firing request at {} with start {} and limit {}'.format(url,
                                                                             stream.start,
                                                                             stream.limit))
        return requests.get(url, headers=headers, params=params)

    def validate_response(self, response):
        if isinstance(response, requests.Response) and response.status_code == 200:
            try:
                payload = response.json()
                if payload['success'] and payload['data']:
                    return True

            # TODO narrow down
            except Exception as e:
                pass

        raise InvalidResponseException("Response from Pipedrive API is not valid, wonder why ..")
