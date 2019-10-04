# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from exportcomments.base import ModelEndpointSet
from exportcomments.response import ExportCommentsResponse
from exportcomments.validation import validate_order_by_param


class Export(ModelEndpointSet):
    model_type = 'exports'

    @property
    def tags(self):
        if not hasattr(self, '_tags'):
            self._tags = Tags(self.token, self.base_url)
        return self._tags

    def list(self, page=None, per_page=None, order_by=None, retry_if_throttled=True):
        if order_by is not None:
            order_by = validate_order_by_param(order_by)
        query_string = self.remove_none_value(dict(
                                              page=page,
                                              per_page=per_page,
                                              order_by=order_by,
                                              ))
        url = self.get_list_url(query_string=query_string)
        response = self.make_request('GET', url, retry_if_throttled=retry_if_throttled)
        return ExportCommentsResponse(response)

    def check(self, uniqueId, retry_if_throttled=True):
        data = self.remove_none_value({
                                      'uniqueId': uniqueId
                                      })
        url = self.get_detail_url(data)
        response = self.make_request('GET', url, retry_if_throttled=retry_if_throttled)
        return ExportCommentsResponse(response)

   
    def create(self, url, replies='false', twitterType=None, retry_if_throttled=True):
        data = self.remove_none_value({
                                      'url': url,
                                      'replies': replies,
                                      'twitterType': twitterType
                                      })
        url = self.get_detail_url(data)
        response = self.make_request('POST', url, retry_if_throttled=retry_if_throttled)
        return ExportCommentsResponse(response)

    