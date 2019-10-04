# ExportComments API for Python

Official Python client for the [ExportComments API](https://exportcomments.com/api/). Build and run machine learning models for language processing from your Python apps.


Installation
---------------


You can use pip to install the library:

```bash
$ pip install exportcomments
```

Alternatively, you can just clone the repository and run the setup.py script:

```bash
$ python setup.py install
```


Usage
------


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
    uniqueId='dfd6a2f2-5579-421f-96ac-98993d0edea1'
)

```

### Responses

The response object returned by every endpoint call is a `ExportCommentsResponse` object. The `body` attribute has the parsed response from the API:

```python
print(response.body)
# =>  [
# =>    {
# =>      "url": "https://www.instagram.com/p/1234567",
# =>      "datecreated": "2016-08-26T07:32:09+00:00",
# =>      "uniqueId": "dfd6a2f2-5579-421f-96ac-98993d0edea1",
# =>      "done": true,
# =>      "dateexported": "2016-08-26T07:32:27+00:00",
# =>      "error": null,
# =>      "total": 306,
# =>      "totalExported": 306,
# =>      "replies": true,
# =>      "dateNotified": null,
# =>      "repliesCount": 0,
# =>      "downloadUrl": "/exports/comments5d638af93ab70-1234567.xlsx",
# =>      "rawUrl": "/exports/6dbf1a87e0fb1f7f16b25be55bb37647-148d4d42-9db8-4e5a-9b51-a860e3646cb0.json"
# =>    }
# =>  ]
```


## Create export

```python
response = ex.export.create(
    url='https://www.instagram.com/p/1234567', replies='false', twitterType=None
)

```

### Responses

The response object returned by every endpoint call is a `ExportCommentsResponse` object. The `body` attribute has the parsed response from the API:

```python
print(response.body)
# =>    {
# =>        "uniqueId": "dfd6a2f2-5579-421f-96ac-98993d0edea1",
# =>        "date_created": "2016-08-26T07:32:09+00:00",
# =>        "status": false,
# =>        "error": null
# =>    }

```


### Errors

Endpoint calls may raise exceptions. Here is an example on how to handle them:

```python
from exportcomments.exceptions import PlanQueryLimitError, ExportCommentsException

try:
    response = ex.export.create(url='https://www.instagram.com/p/1234567', replies='false', twitterType=None)
except PlanQueryLimitError as e:
    # No monthly queries left
    # e.response contains the ExportCommentsResponse object
    print(e.error_code, e.detail)
except ExportCommentsException:
    raise
```

Available exceptions:

| class                       | Description |
|-----------------------------|-------------|
| `ExportCommentsException`      | Base class for every exception below.                                  |
| `RequestParamsError`        | An invalid parameter was sent. Check the exception message or response object for more information. |
| `AuthenticationError`       | Authentication failed, usually because an invalid token was provided. Check the exception message. |
| `ForbiddenError`            | You don't have permissions to perform the action on the given resource. |
| `PlanRateLimitError`        | You have sent too many requests in the last minute.|
| `ConcurrencyRateLimitError` | You have sent too many requests in the last second. |

