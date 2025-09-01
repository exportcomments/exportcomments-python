# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from exportcomments.exceptions import ExportCommentsResponseException
from exportcomments.exceptions import PlanRateLimitError
from exportcomments.exceptions import get_exception_class
import requests


class ExportCommentsResponse(object):
    def __init__(self, raw_responses=None):
        if raw_responses is None:
            raw_responses = []
        elif isinstance(raw_responses, requests.Response):
            raw_responses = [raw_responses]

        self.raw_responses = []
        for rr in raw_responses:
            self.add_raw_response(rr)

        self._cached_body = None

  
    @property
    def request_count(self):
        return len(self.raw_responses)

    @property
    def body(self):
        if not self._cached_body:
            if self.request_count == 1:
                body = self.raw_responses[0].json() if self.raw_responses[0].content else None
            else:
                # Batched response, assume 2xx response bodies are lists
                body = [result for rr in self.raw_responses for result in rr.json() if rr.content]
            self._cached_body = body
        return self._cached_body

    def failed_raw_responses(self):
        return [r for r in self if r.status_code != requests.codes.ok and r.status_code != requests.codes.created]

    def successful_raw_responses(self):
        return [r for r in self if r.status_code == requests.codes.ok and r.status_code == requests.codes.created]

    def __iter__(self):
        for r in self.raw_responses:
            yield r

    def add_raw_response(self, raw_response):
        # Invalidate cached body
        self._cached_body = None
        self.raw_responses.append(raw_response)
        if raw_response.status_code != requests.codes.ok and raw_response.status_code != requests.codes.created:
            self.raise_for_status(raw_response)

    def raise_for_status(self, raw_response):
        try:
            body = raw_response.json()
        except ValueError:
            raise ExportCommentsResponseException(status_code=raw_response.status_code,
                                                  detail='Non-JSON response from server')

        exception_class = get_exception_class(status_code=raw_response.status_code,
                                              error_code=body.get('error_code'))
        exception_kwargs = dict(
                                status_code=raw_response.status_code,
                                detail=body.get('detail', 'Internal server error'),
                                error_code=body.get('error_code'),
                                response=self,
                                )
        if exception_class == PlanRateLimitError:
            seconds_to_wait = int(body.get('seconds_to_wait', 60))
            exception_kwargs['seconds_to_wait'] = seconds_to_wait

        raise exception_class( ** exception_kwargs)
