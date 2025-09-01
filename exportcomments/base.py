# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from exportcomments.settings import DEFAULT_BASE_URL
import json
import pkg_resources
import requests
import six
from six.moves.urllib.parse import urlencode
import time

try:
    version = pkg_resources.get_distribution('exportcomments').version
except Exception:
    version = 'noversion'


class ModelEndpointSet(object):
    def __init__(self, token, base_url=DEFAULT_BASE_URL):
        self.token = token
        self.base_url = base_url

    def _add_action_or_query_string(self, url, action, query_string):
        if action is not None:
            url += '{}/'.format(action)
        if query_string is not None:
            url += '?' + urlencode(query_string)
        return url

    def get_list_url(self, action=None, query_string=None):
        url = '{}/jobs'.format(self.base_url)
        return self._add_action_or_query_string(url, action, query_string)

    def get_detail_url(self, guid, action=None, query_string=None):
        url = '{}/job/{}'.format(self.base_url, guid)
        return self._add_action_or_query_string(url, action, query_string)

    def get_create_url(self):
        return '{}/job'.format(self.base_url)

    def make_request(self, method, url, data=None, retry_if_throttled=True, params=None):
        if data is not None:
            data = json.dumps(data)

        retries_left = 3
        while retries_left:

            response = requests.request(method, url, data=data, params=params, headers={
                                        'X-AUTH-TOKEN': self.token,
                                        'Content-Type': 'application/json',
                                        'User-Agent': 'python-sdk-{}'.format(version),
                                        })
            if response.content:
                body = response.json()

            if retry_if_throttled and response.status_code == 429:
                error_code = body.get('error_code')

                wait = None
                if error_code in ('PLAN_RATE_LIMIT', 'CONCURRENCY_RATE_LIMIT'):
                    wait = int(body.get('seconds_to_wait', 2))

                if wait:
                    time.sleep(wait)
                    retries_left -= 1
                    continue

            return response
        return response

    def remove_none_value(self, d):
        return {k: v for k, v in six.iteritems(d) if v is not None}
