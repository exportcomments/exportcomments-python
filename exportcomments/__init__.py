# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division, absolute_import

from exportcomments.settings import DEFAULT_BASE_URL
from exportcomments.export import Export



class ExportComments(object):
    def __init__(self, token, base_url=DEFAULT_BASE_URL):
        self.token = token
        self.base_url = base_url

    @property
    def exports(self):
        if not hasattr(self, '_exports'):
            self._exports = Export(token=self.token, base_url=self.base_url)
        return self._exports