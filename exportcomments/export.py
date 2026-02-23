# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from exportcomments.base import ModelEndpointSet
from exportcomments.response import ExportCommentsResponse


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

    def download(self, guid, output_path=None, retry_if_throttled=True):
        """Download the export file for a completed job.

        First fetches the job to get the download URL, then downloads the file.

        Args:
            guid: The job GUID.
            output_path: Optional file path to save to. If None, uses the
                         server-provided filename.
            retry_if_throttled: Auto-retry on rate limit.

        Returns:
            The file path where the export was saved.
        """
        import os

        job_response = self.check(guid, retry_if_throttled=retry_if_throttled)
        job = job_response.body

        download_url = job.get('download_url') or job.get('download_link')
        if not download_url:
            raise ValueError('No download URL available for job {}. Status: {}'.format(
                guid, job.get('status')))

        response = self.make_request('GET', download_url, retry_if_throttled=retry_if_throttled)

        if output_path is None:
            filename = job.get('file_name') or 'export-{}.xlsx'.format(guid)
            output_path = os.path.abspath(filename)

        with open(output_path, 'wb') as f:
            f.write(response.content)

        return output_path

    def download_json(self, guid, retry_if_throttled=True):
        """Download the raw JSON data for a completed job.

        Args:
            guid: The job GUID.
            retry_if_throttled: Auto-retry on rate limit.

        Returns:
            The parsed JSON data (list of comments/reviews).
        """
        job_response = self.check(guid, retry_if_throttled=retry_if_throttled)
        job = job_response.body

        json_url = job.get('json_url')
        if not json_url:
            raise ValueError('No JSON URL available for job {}. Status: {}'.format(
                guid, job.get('status')))

        response = self.make_request('GET', json_url, retry_if_throttled=retry_if_throttled)
        return response.json()
