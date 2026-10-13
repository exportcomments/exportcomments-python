# ExportComments API for Python

This is the official Python client for the ExportComments API v3. Export comments and reviews from 40+ social media and review platforms including Instagram, YouTube, TikTok, Facebook, Twitter/X, Reddit, Trustpilot, Amazon, and more.

## Installation

```bash
pip install exportcomments
```

Or install from source:

```bash
git clone https://github.com/exportcomments/exportcomments-python.git
cd exportcomments-python
pip install -r requirements.txt
python setup.py install
```

## Usage

Initialize the client with your API token (get it at [app.exportcomments.com/user/api](https://app.exportcomments.com/user/api)):

```python
from exportcomments import ExportComments

ex = ExportComments('<YOUR API TOKEN HERE>')
```

### Check API Connectivity

```python
result = ex.ping()
print(result)  # {'message': 'pong'}
```

### Create an Export Job

Start an export by submitting a URL. The queue is limited to 5 concurrent requests.

```python
response = ex.jobs.create(
    url='https://www.instagram.com/p/1234567',
    options={'replies': True, 'limit': 100}
)
guid = response.body['guid']
```

### Check Job Status

```python
response = ex.jobs.check(guid=guid)
status = response.body['status']  # 'queueing', 'progress', 'done', or 'error'

# Or block until the job is finished (polls every 10s, 1h timeout by default)
job = ex.jobs.wait(guid)
```

### Bulk Export (many URLs in one call)

Premium and Business plans can submit a list of URLs at once. The server queues
them and runs them at your plan's concurrency; every URL becomes a regular job.

```python
response = ex.jobs.create_batch(
    urls=[
        'https://www.instagram.com/p/AAAAAAA/',
        'https://www.instagram.com/p/BBBBBBB/',
    ],
    options={'replies': True},
)
batch_id = response.body['batchId']
guids = response.body['guids']        # one per accepted URL
rejected = response.body['errors']    # URLs the server did not accept

status = ex.jobs.wait_batch(batch_id)   # or ex.jobs.check_batch(batch_id).body
for job in status['exports']:
    print(job['url'], job['status'], job['total'])
```

Limits: Business tokens may hold up to 100 queued URLs and send 5 batch
submissions per 10 minutes (Premium: 25 queued, 5 per 30 minutes). Only
accepted submissions count toward the window.

### Exports with 0 results

When the source returns nothing for a URL (private or login-gated content,
comments disabled, filters too narrow), the job finishes as `done` with
`total: 0`. **No file is produced in that case** — `download_url` / `json_url`
are `null` and `result_note` explains why. `download()` and `download_json()`
raise `EmptyExportError` instead of failing on a dead link:

```python
from exportcomments.exceptions import EmptyExportError

try:
    ex.jobs.download(guid)
except EmptyExportError as e:
    print(e.result_note)
```

For login-gated content, run the export with your own session cookies
(Advanced Mode, see *Job Options* below).

### List Jobs

```python
response = ex.jobs.list(page=1, limit=10)
jobs = response.body
```

### Download Export File

Download the Excel/CSV file for a completed job:

```python
# Downloads and saves the file, returns the file path
file_path = ex.jobs.download(guid=guid)
print(f"Saved to: {file_path}")

# Or specify a custom output path
file_path = ex.jobs.download(guid=guid, output_path='my_export.xlsx')
```

### Download Raw JSON Data

Get the exported data as parsed JSON:

```python
data = ex.jobs.download_json(guid=guid)
for comment in data:
    print(comment['message'], comment['author_name'])
```

### Job Options

The API supports various options when creating a job:

```python
response = ex.jobs.create(
    url='https://www.instagram.com/p/1234567',
    options={
        'replies': True,
        'limit': 500,
        'minTimestamp': 1622505600,
        'maxTimestamp': 1625097600,
        'vpn': 'Norway',
        'cookies': {
            'sessionid': 'your_session_id'
        }
    }
)
```

### Backward Compatibility

For backward compatibility, `ex.exports` still works as an alias for `ex.jobs`:

```python
response = ex.exports.create(
    url='https://www.instagram.com/p/1234567',
    options={'replies': True}
)
```

### Handling Errors

```python
from exportcomments.exceptions import ExportCommentsException

try:
    response = ex.jobs.create(
        url='https://www.instagram.com/p/1234567',
        options={'replies': True}
    )
except ExportCommentsException as e:
    print(e)
```

| Exception Class              | Description                                                                                |
| ---------------------------- | ------------------------------------------------------------------------------------------ |
| `ExportCommentsException`    | Base class for all exceptions.                                                             |
| `RequestParamsError`         | Invalid parameter sent. Check the message or response object for details.                  |
| `AuthenticationError`        | Authentication failed, typically due to an invalid API token.                               |
| `ForbiddenError`             | Insufficient permissions for the requested action.                                         |
| `PlanRateLimitError`         | Too many requests per minute according to your plan's limits.                              |
| `ConcurrencyRateLimitError`  | Too many requests per second.                                                              |
| `EmptyExportError`           | The job finished with 0 results, so there is no file to download (`result_note` says why). |

## Complete Example

```python
from exportcomments import ExportComments
from exportcomments.exceptions import ExportCommentsException
import time
import sys

ex = ExportComments('<YOUR API TOKEN HERE>')

# Verify connectivity
print(ex.ping())

# Create export
try:
    response = ex.jobs.create(
        url='https://www.instagram.com/p/1234567',
        options={'replies': True, 'limit': 100}
    )
except ExportCommentsException as e:
    print(e)
    sys.exit()

guid = response.body['guid']

# Poll until done
while True:
    response = ex.jobs.check(guid=guid)
    status = response.body['status']

    if status == 'done':
        break
    elif status == 'error':
        print("Error:", response.body.get('error'))
        sys.exit()

    time.sleep(5)

# Download the file
file_path = ex.jobs.download(guid=guid)
print(f"Downloaded: {file_path}")

# Or get raw JSON data
data = ex.jobs.download_json(guid=guid)
print(f"Got {len(data)} comments")
```

## Changelog

**2.2.0**

- Bulk exports: `create_batch()`, `check_batch()`, `wait_batch()` (`POST /api/v1/batch-export`)
- `wait(guid)` polls a job until it is finished
- `EmptyExportError` for jobs that finished with 0 results (no file exists); reads the API's `result_note`
- Error messages surface the API's `error` text instead of a generic "Internal server error"

## API v3 Changes

Version 2.0.0 supports API v3:

- **New method names**: Use `ex.jobs` instead of `ex.exports` (backward compatibility maintained)
- **Updated parameters**: `create()` uses an `options` dict instead of individual parameters
- **New methods**: `ping()`, `download()`, `download_json()`
- **Endpoints**: Uses `/api/v3/` endpoints

For more information, visit [ExportComments API Documentation](https://docs.exportcomments.com).
