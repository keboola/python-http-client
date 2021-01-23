# Python HTTP Client

## Introduction

This library serves as tool to work effectively when sending requests to external services. The library wraps on top of the `requests` library and implements a couple useful method, such as in-built retry, exception raising, etc.

It is being developed by the Keboola Data Services team and officially supported by Keboola. It aims to simplify the Keboola Component creation process, by removing the necessity to write complicated code to work with the APIs effectively.

## Links

- API Documentation: [API Docs](https://github.com/keboola/python-http-client/blob/main)
- Source code: [https://github.com/keboola/python-http-client](https://github.com/keboola/python-http-client)
- PYPI project code: [https://test.pypi.org/project/keboola.client/](https://test.pypi.org/project/keboola.client/)
- Documentation: [https://developers.keboola.com/extend/component/python-component-library](https://developers.keboola.com/extend/component/python-component-library)

## Quick Start

### Installation

The package may be installed via PIP:

```
pip install keboola.http_client
```

### Structure and Functionality

The package contains a single core module:
- `keboola.client` - Contains the `HttpClient` class for easy manipulation with APIs and external services

### `HttpClient`

The core class that serves as a tool to communicate with external services. The class is a wrapper around the `requests` library with implemented retry mechanism, and automatic error handling in case of HTTP error returned.

For each HTTP method, following methods are implemented in the `HttpClient`:
- GET - `get()`, `get_raw()`
- POST - `post()`, `post_raw()`
- PATCH - `patch()`, `patch_raw()`
- UPDATE - `update()`, `update_raw()`
- PUT - `put()`, `put_raw()`
- DELETE - `delete()`, `delete_raw()`

The difference between `_raw()` methods and their non-`_raw()` counterparts is, that raw methods will return `requests.Response` object, while non-raw methods will return a json body if the request is successful and raise an error if an HTTP error is encountered.

All abovementioned methods support all parameters supported by `requests.request()` functions - as described in the [documentation](https://requests.readthedocs.io/en/latest/api/#main-interface).

#### Initialization

The core class is `keboola.client.http.HttpClient`, which can be initialized by specifying the `base_url` parameter:

```python
from keboola.client import HttpClient

BASE_URL = 'https://connection.keboola.com/v2/storage/'
cl = HttpClient(BASE_URL)
```

#### Default arguments

For `HttpClient`, it is possible to define default arguments, which will be sent with every request. It's possible to define `default_http_header`, `auth_header` and `default_params` - a default header, a default authentication header and default parameters, respectively.

```python
from keboola.client import HttpClient

BASE_URL = 'https://connection.keboola.com/v2/storage/'
AUTH_HEADER = {
    'x-storageapi-token': '1234-STORAGETOKENSTRING'
}
DEFAULT_PARAMS = {
    'include': 'columns'
}
DEFAULT_HEADER = {
    'Content-Type': 'application/json'
}

cl = HttpClient(BASE_URL, default_http_header=DEFAULT_HEADER,
                auth_header=AUTH_HEADER, default_params=DEFAULT_PARAMS)
```

#### Basic authentication

By specifying the `auth` argument, the `HttpClient` will utilize the basic authentication.

```python
from keboola.client import HttpClient

BASE_URL = 'https://connection.keboola.com/v2/storage/'
USERNAME = 'TestUser'
PASSWORD = '@bcd1234'

cl = HttpClient(BASE_URL, auth=(USERNAME, PASSWORD))
```

#### Simple POST request

Making a simple POST request using `post_raw()` method.

```python
from keboola.client import HttpClient

BASE_URL = 'https://www.example.com/change'
cl = HttpClient(BASE_URL)

data = {'attr_1': 'value_1', 'attr_2': 'value_2'}
header = {'content-type': 'application/json'}
response = cl.post_raw(data=data, headers=header)

if response.ok is not True:
    raise ValueError(response.json())
else:
    return response.json()
```

Making a simple POST request using `post()` method.

```python
from keboola.client import HttpClient

BASE_URL = 'https://www.example.com/change'
cl = HttpClient(BASE_URL)

data = {'attr_1': 'value_1', 'attr_2': 'value_2'}
header = {'content-type': 'application/json'}
response = cl.post(data=data, headers=header)
```

#### Working with URL paths

Each of the methods takes an optional positional argument `endpoint_path`. If specified, the value of the `endpoint_path` will be appended to the URL specified in the `base_url` parameter, when initializing the class. When appending the `endpoint_path`, the [`urllib.parse.urljoin()`](https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urljoin) function is used.

The below code will send a POST request to the URL `https://example.com/api/v1/events`:

```python
from keboola.client import HttpClient

BASE_URL = 'https://example.com/api/v1'
cl = HttpClient(BASE_URL)

header = {'token': 'token_value'}
cl.post_raw('events', headers=header)
```

It is also possible to override this behavior by using parameter `is_absolute_path=True`. If specified, the value of `endpoint_path` will not be appended to the `base_url` parameter, but will rather be used as an absolute URL to which the HTTP request will be made.

In the below code, the `base_url` parameter is set to `https://example.com/api/v1`, but the base URL will be overriden by specifying `is_absolute_path=True` and the HTTP request will be made to the URL specified in the `post()` request - `https://anothersite.com/v2`.

```python
from keboola.client import HttpClient

BASE_URL = 'https://example.com/api/v1'
cl = HttpClient(BASE_URL)

header = {'token': 'token_value'}
cl.post_raw('https://anothersite.com/v2', headers=header, is_absolute_path=True)
```

#### Usage Example

A simple request made with default authentication header and parameters.

```python
import os
from keboola.client import HttpClient

BASE_URL = 'https://connection.keboola.com/v2/'
TOKEN = os.environ['TOKEN']

cl = HttpClient(BASE_URL, auth_header={'x-storageapi-token': TOKEN})

request_params = {'exclude': 'components'}
response = cl.get_raw('storage', params=request_params)

if response.ok is True:
    print(response.json())
```