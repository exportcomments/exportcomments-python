# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from exportcomments.base import ModelEndpointSet
from exportcomments.response import ExportCommentsResponse
from exportcomments.validation import validate_order_by_param


class Export(ModelEndpointSet):
    model_type = 'jobs'

    def list(self, page=None, limit=None, retry_if_throttled=True):
        query_string = self.remove_none_value(dict(
                                              page=page,
                                              limit=limit,
                                              ))
        url = self.get_list_url(query_string=query_string)
        response = self.make_request('GET', url, retry_if_throttled=retry_if_throttled)
        return ExportCommentsResponse(response)

    def check(self, guid, retry_if_throttled=True):
        url = self.get_detail_url(guid)
        response = self.make_request('GET', url, retry_if_throttled=retry_if_throttled)
        return ExportCommentsResponse(response)

    def create(self, url, options=None, retry_if_throttled=True):
        data = self.remove_none_value({
                                      'url': url,
                                      'options': options
                                      })
        create_url = self.get_create_url()
        response = self.make_request('POST', create_url, data=data, retry_if_throttled=retry_if_throttled)
        return ExportCommentsResponse(response)

