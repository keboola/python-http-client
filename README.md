# Python HTTP Client

## Introduction

![Build & Test](https://github.com/keboola/python-http-client/workflows/Build%20&%20Test/badge.svg?branch=main)
[![Code Climate](https://codeclimate.com/github/keboola/python-http-client/badges/gpa.svg)](https://codeclimate.com/github/keboola/python-http-client)
[![PyPI version](https://badge.fury.io/py/keboola.http-client.svg)](https://badge.fury.io/py/keboola.http-client)

This library serves as tool to work effectively when sending requests to external services. The library wraps on top of the `requests` library and implements a couple useful method, such as in-built retry, exception raising, etc.

It is being developed by the Keboola Data Services team and officially supported by Keboola. It aims to simplify the Keboola Component creation process, by removing the necessity to write complicated code to work with the APIs effectively.

## Links

- API Documentation: [API Docs](https://htmlpreview.github.io/?https://raw.githubusercontent.com/keboola/python-http-client/main/docs/api-html/http_client/http.html)
- Source code: [https://github.com/keboola/python-http-client](https://github.com/keboola/python-http-client)
- PYPI project code: [https://pypi.org/project/keboola.http-client](https://pypi.org/project/keboola.http-client)
- Documentation: [https://developers.keboola.com/extend/component/python-component-library](https://developers.keboola.com/extend/component/python-component-library)

## Quick Start

### Installation

The package may be installed via PIP:

```
pip install keboola.http-client
```

### Structure and Functionality

The package contains a single core module:
- `keboola.http_client` - Contains the `HttpClient` class for easy manipulation with APIs and external services

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

The core class is `keboola.http_client.HttpClient`, which can be initialized by specifying the `base_url` parameter:

```python
from keboola.http_client import HttpClient

BASE_URL = 'https://connection.keboola.com/v2/storage/'
cl = HttpClient(BASE_URL)
```

#### Default arguments

For `HttpClient`, it is possible to define default arguments, which will be sent with every request. It's possible to define `default_http_header`, `auth_header` and `default_params` - a default header, a default authentication header and default parameters, respectively.

```python
from keboola.http_client import HttpClient

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
from keboola.http_client import HttpClient

BASE_URL = 'https://connection.keboola.com/v2/storage/'
USERNAME = 'TestUser'
PASSWORD = '@bcd1234'

cl = HttpClient(BASE_URL, auth=(USERNAME, PASSWORD))
```

#### Simple POST request

Making a simple POST request using `post_raw()` method.

```python
from keboola.http_client import HttpClient

BASE_URL = 'https://www.example.com/change'
cl = HttpClient(BASE_URL)

data = {'attr_1': 'value_1', 'attr_2': 'value_2'}
header = {'content-type': 'application/json'}
response = cl.post_raw(data=data, headers=header)

if response.ok is not True:
    raise ValueError(response.json())
else:
    print(response.json())
```

Making a simple POST request using `post()` method.

```python
from keboola.http_client import HttpClient

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
from keboola.http_client import HttpClient

BASE_URL = 'https://example.com/api/v1'
cl = HttpClient(BASE_URL)

header = {'token': 'token_value'}
cl.post_raw('events', headers=header)
```

It is also possible to override this behavior by using parameter `is_absolute_path=True`. If specified, the value of `endpoint_path` will not be appended to the `base_url` parameter, but will rather be used as an absolute URL to which the HTTP request will be made.

In the below code, the `base_url` parameter is set to `https://example.com/api/v1`, but the base URL will be overriden by specifying `is_absolute_path=True` and the HTTP request will be made to the URL specified in the `post()` request - `https://anothersite.com/v2`.

```python
from keboola.http_client import HttpClient

BASE_URL = 'https://example.com/api/v1'
cl = HttpClient(BASE_URL)

header = {'token': 'token_value'}
cl.post_raw('https://anothersite.com/v2', headers=header, is_absolute_path=True)
```

#### Raw request Example

A simple request made with default authentication header and parameters.

```python
import os
from keboola.http_client import HttpClient

BASE_URL = 'https://connection.keboola.com/v2/'
TOKEN = os.environ['TOKEN']

cl = HttpClient(BASE_URL, auth_header={'x-storageapi-token': TOKEN})

request_params = {'exclude': 'components'}
response = cl.get_raw('storage', params=request_params)

if response.ok is True:
    print(response.json())
```

#### Building HTTP client based on HTTPClient Example

This example demonstrates the default use of the HTTPClient as a base for REST API clients.

```python
from keboola.http_client import HttpClient

BASE_URL = 'https://connection.eu-central-1.keboola.com/v2/storage'
MAX_RETRIES = 10


class KBCStorageClient(HttpClient):

    def __init__(self, storage_token):
        HttpClient.__init__(self, base_url=BASE_URL, max_retries=MAX_RETRIES, backoff_factor=0.3,
                            status_forcelist=(429, 500, 502, 504),
                            auth_header={"X-StorageApi-Token": storage_token})

    def get_files(self, show_expired=False):
        params = {"showExpired": show_expired}
        return self.get('files', params=params)

cl = KBCStorageClient("my_token")

print(cl.get_files())
```

## Async Usage

The package also provides an asynchronous version of the HTTP client called AsyncHttpClient. 
It allows you to make asynchronous requests using async/await syntax. To use the AsyncHttpClient, import it from keboola.http_client_async:

```python
from keboola.http_client import AsyncHttpClient
```

The AsyncHttpClient class provides similar functionality as the HttpClient class, but with asynchronous methods such as get, post, put, patch, and delete that return awaitable coroutines. 
You can use these methods within async functions to perform non-blocking HTTP requests.

```python
import asyncio
from keboola.http_client import AsyncHttpClient

async def main():
    base_url = "https://api.example.com/"
    async with AsyncHttpClient(base_url) as client:
        response = await client.get("endpoint")

        if response.status_code == 200:
            data = response.json()
            # Process the response data
        else:
            # Handle the error

asyncio.run(main())
```

The AsyncHttpClient provides similar initialization and request methods as the HttpClient. 
The request methods return awaitable coroutines that can be awaited in an asynchronous context.

#### Building HTTP client based on AsyncHttpClient Example
This example demonstrates the default use of the HTTPClient as a base for REST API clients.

```python
import asyncio
from keboola.http_client import AsyncHttpClient

BASE_URL = 'https://connection.keboola.com/v2/storage'
MAX_RETRIES = 3

class KBCStorageClient(AsyncHttpClient):

    def __init__(self, storage_token):
        AsyncHttpClient.__init__(
            self,
            base_url=BASE_URL,
            retries=MAX_RETRIES,
            backoff_factor=0.3,
            retry_status_codes=[429, 500, 502, 504],
            auth_header={"X-StorageApi-Token": storage_token}
        )

    async def get_files(self, show_expired=False):
        params = {"showExpired": show_expired}
        response = await self.get('tables', params=params, timeout=5)
        return response

async def main():
    cl = KBCStorageClient("my_token")
    files = await cl.get_files(show_expired=False)
    print(files)

asyncio.run(main())
```
**Note:** Since there are no parallel requests being made, you won't notice any speedup for this use case.
For an example where you can see the speedup thanks to async requests, you can view the pokeapi.py in docs/examples.
