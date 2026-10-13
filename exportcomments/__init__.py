# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division, absolute_import

from exportcomments.settings import DEFAULT_BASE_URL, installed_version
from exportcomments.export import Export

import requests

_version = installed_version()


class ExportComments(object):
    def __init__(self, token, base_url=DEFAULT_BASE_URL):
        self.token = token
        self.base_url = base_url

    @property
    def jobs(self):
        if not hasattr(self, '_jobs'):
            self._jobs = Export(token=self.token, base_url=self.base_url)
        return self._jobs

    # Keep backward compatibility
    @property
    def exports(self):
        return self.jobs

    def ping(self):
        """Check API connectivity.

        Returns:
            dict: {'message': 'pong'} on success.
        """
        url = self.base_url.replace('/v3', '/v1') + '/ping'
        response = requests.get(url, headers={
            'X-AUTH-TOKEN': self.token,
            'Content-Type': 'application/json',
            'User-Agent': 'python-sdk-{}'.format(_version),
        })
        return response.json()
