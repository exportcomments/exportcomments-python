# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import os
import time

from exportcomments.base import ModelEndpointSet
from exportcomments.exceptions import EmptyExportError
from exportcomments.response import ExportCommentsResponse

FINISHED_STATUSES = ('done', 'error')


def _is_done_without_results(job):
    """True when the job finished but gathered nothing — the API writes no file then."""
    if job.get('status') != 'done':
        return False
    if job.get('result_note'):
        return True
    total = job.get('total')
    return total is not None and int(total) == 0


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

    def wait(self, guid, poll_interval=10, timeout=3600, retry_if_throttled=True):
        """Poll a job until it reaches a final status ('done' or 'error').

        Args:
            guid: The job GUID.
            poll_interval: Seconds between status checks.
            timeout: Give up after this many seconds (raises ``TimeoutError``).
            retry_if_throttled: Auto-retry on rate limit.

        Returns:
            The final job dict (same shape as ``check(guid).body``).
        """
        deadline = time.time() + timeout
        while True:
            job = self.check(guid, retry_if_throttled=retry_if_throttled).body
            if job.get('status') in FINISHED_STATUSES:
                return job
            if time.time() >= deadline:
                raise TimeoutError('Job {} still {} after {}s'.format(guid, job.get('status'), timeout))
            time.sleep(poll_interval)

    # ------------------------------------------------------------------ #
    # Bulk (batch) exports — POST /api/v1/batch-export                    #
    # ------------------------------------------------------------------ #

    def create_batch(self, urls, options=None, retry_if_throttled=True):
        """Submit many URLs in one call (Premium / Business).

        The server queues them and drains the queue at your plan's concurrency.
        Each URL becomes a normal job; the response carries the job ``guids``
        plus a ``batchId`` for ``check_batch()``. URLs the server could not
        accept are listed under ``errors`` and do not stop the rest.

        Args:
            urls: List of post / profile / review-page URLs.
            options: Same options dict as ``create()``, applied to every URL.
            retry_if_throttled: Auto-retry on rate limit.
        """
        data = self.remove_none_value({
                                      'urls': list(urls),
                                      'options': options
                                      })
        response = self.make_request('POST', self.get_batch_url(), data=data,
                                     retry_if_throttled=retry_if_throttled)
        return ExportCommentsResponse(response)

    def check_batch(self, batch_id, retry_if_throttled=True):
        """Progress of a batch: counts plus one entry per URL.

        Each entry has ``guid``, ``url``, ``status``, ``total``,
        ``total_exported`` and ``error``. A ``done`` entry with ``total`` 0
        produced no file — see ``EmptyExportError``.
        """
        response = self.make_request('GET', self.get_batch_url(batch_id),
                                     retry_if_throttled=retry_if_throttled)
        return ExportCommentsResponse(response)

    def wait_batch(self, batch_id, poll_interval=15, timeout=7200, retry_if_throttled=True):
        """Poll a batch until ``is_complete`` is true; returns the final status dict."""
        deadline = time.time() + timeout
        while True:
            status = self.check_batch(batch_id, retry_if_throttled=retry_if_throttled).body
            if status.get('is_complete'):
                return status
            if time.time() >= deadline:
                raise TimeoutError('Batch {} still incomplete after {}s'.format(batch_id, timeout))
            time.sleep(poll_interval)

    # ------------------------------------------------------------------ #
    # Downloads                                                           #
    # ------------------------------------------------------------------ #

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

        Raises:
            EmptyExportError: the job finished with 0 results (no file exists).
            ValueError: the job is not finished yet or has no download URL.
        """
        job_response = self.check(guid, retry_if_throttled=retry_if_throttled)
        job = job_response.body

        if _is_done_without_results(job):
            raise EmptyExportError(guid, job.get('result_note'))

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

        Raises:
            EmptyExportError: the job finished with 0 results (no file exists).
            ValueError: the job is not finished yet or has no JSON URL.
        """
        job_response = self.check(guid, retry_if_throttled=retry_if_throttled)
        job = job_response.body

        if _is_done_without_results(job):
            raise EmptyExportError(guid, job.get('result_note'))

        json_url = job.get('json_url')
        if not json_url:
            raise ValueError('No JSON URL available for job {}. Status: {}'.format(
                guid, job.get('status')))

        response = self.make_request('GET', json_url, retry_if_throttled=retry_if_throttled)
        return response.json()
