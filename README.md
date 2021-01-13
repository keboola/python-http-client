# Python HTTP Client

## Introduction

This library serves as tool to work effectively when sending requests to external services. The library wraps on top of the `requests` library and implements a couple useful method, such as in-built retry, exception raising, etc.

It is being developed by the Keboola Data Services team and officially supported by Keboola. It aims to simplify the Keboola Component creation process, by removing the necessity to write complicated code to work with the APIs effectively.

## Links

- API Documentation: [API Docs](https://github.com/keboola/python-http-client/blob/main)
- Source code: [https://github.com/keboola/python-http-client](https://github.com/keboola/python-http-client)
- PYPI project code: [link](link)
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
response = cl.post_raw(self.base_url, data=data, headers=header)

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
response = cl.post(self.base_url, data=data, headers=header)
```

#### Usage Example

```python
import os
from urllib.parse import urljoin
from keboola.client import HttpClient

BASE_URL = 'https://connection.keboola.com/v2/'
TOKEN = os.environ['TOKEN']

cl = HttpClient(BASE_URL, auth_header={'x-storageapi-token': TOKEN})

request_params = {'exclude': 'components'}
response = cl.get_raw(url=urljoin(self.base_url, 'storage'),
                      params=request_params)

if response.ok is True:
    print(response.json())
```