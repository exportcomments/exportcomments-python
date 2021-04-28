# ExportComments API for Python

Official Python client for the [ExportComments API](https://exportcomments.com/api). Build and run machine learning models for language processing from your Python apps.

## Installation

You can use pip to install the library:

```bash
$ pip install exportcomments
```

Alternatively, you can just clone the repository and run the setup.py script:

```bash
$ python setup.py install
```

## Usage

Before making requests to the API, you need to create an instance of the ExportComments client. You will have to use your [account API Key](https://exportcomments.com/pricing):

```python
from exportcomments import ExportComments

# Instantiate the client Using your API key
ex = ExportComments('<YOUR API TOKEN HERE>')
```

### Usage Examples

From the ExportComments client instance, you can call any endpoint:

## Check export

```python
response = ex.exports.check(
    guid='dfd6a2f2-5579-421f-96ac-98993d0edea1'
)

```

### Responses

The response object returned by every endpoint call is a `ExportCommentsResponse` object. The `body` attribute has the parsed response from the API:

```python
print(response.body)

# =>  {
# =>      "code": 200,
# =>      "success": true,
# =>      "data": {
# =>          "url": "https://www.instagram.com/p/1234567",
# =>          "guid": "2cfb0b9d-7633-4341-a702-cb889fe549eb",
# =>          "status": "queueing",
# =>          "replies": false,
# =>          "fileName": "comments5ea4b4d5a7602-1325511884314646.xlsx",
# =>          "fileNameRAW": "08b735760a5a40eb1fd70ca16e97aed3-2e0916fe-de86-4422-8449-fb608cbe5221.json",
# =>          "total": 0,
# =>          "totalExported": 0,
# =>          "retry": 0,
# =>          "error": null,
# =>          "repliesCount": 0,
# =>          "twitterType": null,
# =>          "timezone": "UTC",
# =>          "createdAt": "2016-08-26T07:32:09+00:00",
# =>          "updatedAt": "2016-08-26T07:32:09+00:00",
# =>          "exportedAt": "",
# =>          "downloadUrl": "/exports/comments5ea4b4d5a7602-1325511884314646.xlsx",
# =>          "rawUrl": "/exports/08b735760a5a40eb1fd70ca16e97aed3-2e0916fe-de86-4422-8449-fb608cbe5221.json"
# =>      },
# =>      "message": null
# =>  }
```

## Create export

```python
response = ex.exports.create(
    url='https://www.instagram.com/p/1234567', replies='false', twitterType=None
)

```

### Errors

Endpoint calls may raise exceptions. Here is an example on how to handle them:

```python
from exportcomments.exceptions import PlanQueryLimitError, ExportCommentsException

try:
    response = ex.exports.create(url='https://www.instagram.com/p/1234567', replies='false', twitterType=None)
except PlanQueryLimitError as e:
    # No monthly queries left
    # e.response contains the ExportCommentsResponse object
    print(e.error_code, e.detail)
except ExportCommentsException:
    raise
```

Available exceptions:

| class                       | Description                                                                                         |
| --------------------------- | --------------------------------------------------------------------------------------------------- |
| `ExportCommentsException`   | Base class for every exception below.                                                               |
| `RequestParamsError`        | An invalid parameter was sent. Check the exception message or response object for more information. |
| `AuthenticationError`       | Authentication failed, usually because an invalid token was provided. Check the exception message.  |
| `ForbiddenError`            | You don't have permissions to perform the action on the given resource.                             |
| `PlanRateLimitError`        | You have sent too many requests in the last minute.                                                 |
| `ConcurrencyRateLimitError` | You have sent too many requests in the last second.                                                 |
