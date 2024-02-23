
# ExportComments API for Python

This is the official Python client for the ExportComments API, designed to facilitate the integration of advanced language processing capabilities into Python applications. Utilize this client to efficiently build and manage machine learning models for natural language processing directly from your Python environment.

## Installation

To integrate the ExportComments library into your project, you can easily install it using pip:

```bash
pip install exportcomments
```

Alternatively, if you prefer to install from source or want to contribute to the project, clone the repository and install it manually:

```bash
git clone https://github.com/exportcomments/exportcomments-python.git
cd exportcomments-python
python setup.py install
```

## Usage

To begin utilizing the ExportComments API, you must first instantiate the ExportComments client with your API key, which is available on your ExportComments account.

```python
from exportcomments import ExportComments

# Initialize the client with your API key
ex = ExportComments('<YOUR API TOKEN HERE>')
```

Start an export process by submitting a URL to the API. This places the URL in the processing queue. Please note, the queue is limited to 5 concurrent requests.

```python
response = ex.exports.create(
    url='https://www.instagram.com/p/1234567', replies='false', twitterType=None
)
```

To monitor the status of your export, retrieve the GUID from the initial response and query the export's status.

```python
guid = response.body['data']['guid']
response = ex.exports.check(guid=guid)
```

The status of the export can be checked as follows, with potential statuses including "queueing", "error", "done", or "progress":

```python
# Note: The status is nested within a dictionary
status = response.body['data'][0]['status']
```

### Handling Errors

The API might raise exceptions during endpoint calls. Below is an example of how to catch and handle these exceptions:

```python
from exportcomments.exceptions import ExportCommentsException

try:
    response = ex.exports.create(url='https://www.instagram.com/p/1234567', replies='false', twitterType=None)
except ExportCommentsException as e:
    # Handles all exceptions derived from ExportCommentsException
    print(e)
```

The following table outlines the available exceptions and their descriptions:

| Exception Class              | Description                                                                                     |
| ---------------------------- | ----------------------------------------------------------------------------------------------- |
| `ExportCommentsException`    | The base class for all exceptions listed below.                                                 |
| `RequestParamsError`         | Indicates an invalid parameter was sent. Check the message or response object for details.      |
| `AuthenticationError`        | Occurs when authentication fails, typically due to an invalid API token.                        |
| `ForbiddenError`             | Indicates insufficient permissions for the requested action on the specified resource.          |
| `PlanRateLimitError`         | Triggered by too many requests in a minute, according to your subscription plan's limits.       |
| `ConcurrencyRateLimitError`  | Triggered by too many requests in a second, indicating a rate limit on concurrent requests.     |

You can download the resulting Excel file by using requests.get. Here's a good example:
```python
import requests
import pkg_resources

# downloadUrl is retrieved from the .check method (If it is from .create() you don't need "[0]")
download_url = response.body['data'][0]['downloadUrl']

# Set headers for download (might not be necesary, but just add it in case)
headers = {
    'Authorization': "Your API Token",
    'Content-Type': 'application/json',
    'User-Agent': 'python-sdk-{}'.format(pkg_resources.get_distribution('exportcomments').version),
}

# Get the excel
response = requests.get("https://exportcomments.com/" + download_url, headers=headers)

# Handle the excel if it is available
if response.status_code == 200:
    # Create an excel and save it
    with open("result.xlsx", "wb") as output:
        output.write(response.content)

    print(f"[SUCCESSFUL DOWNLOAD] File Downloaded: {download_url}")
else:
    print(f"[FAILED TO DOWNLOAD] Status Code: {response.status_code}")
```

## Code exaple
Here's a comprehensive example demonstrating a typical workflow when only using 1 URL:
```python
import requests
import pkg_resources
from exportcomments import ExportComments, ExportCommentsException
import time
import sys

ex = ExportComments('<YOUR API TOKEN HERE>')

def get_response(guid):
    while True:
        response = ex.exports.check(guid=guid)
        status = response.body['data'][0]['status']

        if status == 'done':
            break
        elif status == 'error':
            print("Error generating your file.")
            sys.exit()

        time.sleep(20)

    download_url = response.body['data'][0]['downloadUrl']
    headers = {
        'Authorization': "Your API Token",
        'Content-Type': 'application/json',
        'User-Agent': 'python-sdk-{}'.format(pkg_resources.get_distribution('exportcomments').version),
    }

    response = requests.get("https://exportcomments.com/" + download_url, headers=headers)

    if response.status_code == 200:
        with open("result.xlsx", "wb") as output:
            output.write(response.content)
        print(f"[SUCCESSFUL DOWNLOAD] File Downloaded: {download_url}")
    else:
        print(f"[FAILED TO DOWNLOAD] Status Code: {response.status_code}")

if __name__ == '__main__':
    try:
        response = ex.exports.create(
            url='https://www.instagram.com/p/1234567', replies='false', twitterType=None
        )
    except ExportCommentsException as e:
        print(e)
        sys.exit()

    guid = response.body['data']['guid']
    get_response(guid)
```