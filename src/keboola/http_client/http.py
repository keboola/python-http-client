import functools
import logging
from urllib.parse import urlparse, urljoin, quote, urlencode
from http.cookiejar import CookieJar
from typing import Dict, Union, Tuple, Optional

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

Cookie = Union[Dict[str, str], CookieJar]

METHOD_RETRY_WHITELIST = ('GET', 'POST', 'PATCH', 'UPDATE', 'PUT', 'DELETE')
ALLOWED_METHODS = ['GET', 'POST', 'PATCH', 'UPDATE', 'PUT', 'DELETE']


class HttpClient:
    """
    Base class for implementing a simple HTTP client. Typically used as a base for a REST service client.


    Usage:

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

    files_response = cl.get("files", params={"showExpired": True})
    ```

    """

    def __init__(self, base_url: str, max_retries: int = 10, backoff_factor: float = 0.3,
                 status_forcelist: Tuple[int, ...] = (500, 502, 504), default_http_header: Dict = None,
                 auth_header: Dict = None, auth: Tuple = None, default_params: Dict = None,
                 allowed_methods: Tuple = METHOD_RETRY_WHITELIST):
        """
        Create an endpoint.

        Args:
            base_url: The base URL for this endpoint. e.g. https://exampleservice.com/api_v1/
            max_retries: Total number of retries to allow.
            backoff_factor:  A back-off factor to apply between attempts.
            status_forcelist:  A set of HTTP status codes that we should force a retry on. e.g. [500,502]
            default_http_header: Default header to be sent with each request
                eg. ```{
                        'Content-Type' : 'application/json',
                        'Accept' : 'application/json'
                    }```
            auth_header: Auth header to be sent with each request
                eg. `{'Authorization': 'Bearer ' + token}`
            auth: Default Authentication tuple or object to attach to (from  requests.Session().auth).
                eg. auth = (user, password)
            default_params: default parameters to be sent with each request eg. `{'param':'value'}`
            allowed_methods (tuple): Set of upper-cased HTTP method verbs that we should retry on.
        """
        if base_url is None:
            raise ValueError("Base URL is required.")
        # Add trailing slash because of nature of urllib.parse.urljoin()
        self.base_url = base_url if base_url.endswith('/') else base_url + '/'
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.status_forcelist = status_forcelist
        self._auth = auth
        self._auth_header = auth_header if auth_header else {}
        self._default_header = default_http_header if default_http_header else {}
        self._default_params = default_params
        self.allowed_methods = allowed_methods

    def _requests_retry_session(self, session=None):
        session = session or requests.Session()
        retry = Retry(
            total=self.max_retries,
            read=self.max_retries,
            connect=self.max_retries,
            backoff_factor=self.backoff_factor,
            status_forcelist=self.status_forcelist,
            allowed_methods=self.allowed_methods
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    def _build_url(self, endpoint_path: Optional[str] = None, is_absolute_path=False):
        # build URL Specification
        url_path = str(endpoint_path).strip() if endpoint_path is not None else ''

        if not url_path:
            return self.base_url

        if not is_absolute_path:
            full_path = urljoin(self.base_url, url_path)
            parsed = urlparse(full_path)
            encoded_path = quote(parsed.path, safe="/()=-")
            query = f"?{parsed.query}" if parsed.query else ""
            return f"{parsed.scheme}://{parsed.netloc}{encoded_path}{query}"

        parsed = urlparse(endpoint_path)
        encoded_path = quote(parsed.path, safe="/()&=<>-")
        query = f"?{urlencode(parsed.query, safe='&=')}" if parsed.query else ""
        return f"{parsed.scheme}://{parsed.netloc}{encoded_path}{query}"

    def _request_raw(self, method: str, endpoint_path: Optional[str] = None, **kwargs) -> requests.Response:
        """
        Construct a requests call with args and kwargs and process the
        results.

        Args:
            method: A HTTP method to be used. One of PUT/POST/PATCH/GET/UPDATE/DELETE
            endpoint_path (Optional[str]): Optional full URL or a relative URL path. If empty the base_url is used.
            **kwargs: Key word arguments to pass to the
                [`requests.request`](https://requests.readthedocs.io/en/latest/api/#requests.request).
                Accepts supported params in requests.sessions.Session#request
                eg. params = {'locId':'1'}, header = {some additional header}
                parameters and headers are appended to the default ones
                ignore_auth  - True to skip authentication
                is_absolute_path - False to append URL to base url; True to override base url with value of url arg.

        Returns:
            A [`requests.Response`](https://requests.readthedocs.io/en/latest/api/#requests.Response) object.
        """
        s = requests.Session()

        # build URL Specification
        is_absolute_path = kwargs.pop('is_absolute_path', False)
        url = self._build_url(endpoint_path, is_absolute_path)

        # Update headers
        headers = kwargs.pop('headers', {})
        if headers is None:
            headers = {}

        # Default headers
        headers.update(self._default_header)

        # Auth headers
        if kwargs.pop('ignore_auth', False) is False:
            headers.update(self._auth_header)
            s.headers.update(headers)
            s.auth = self._auth

        s.headers.update(headers)

        # Update parameters
        params = kwargs.pop('params', {})
        if params is None:
            params = {}

        # Default parameters
        if self._default_params is not None:
            all_pars = {**params, **self._default_params}
            kwargs.update({'params': all_pars})

        else:
            kwargs.update({'params': params})

        r = self._requests_retry_session(session=s).request(method, url, **kwargs)
        return r

    def response_error_handling(func):
        """Function, that handles response handling of HTTP requests.
        """

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                r = func(*args, **kwargs)
                r.raise_for_status()
            except requests.HTTPError as e:
                logging.warning(e, exc_info=True)
                # Handle different error codes
                raise
            else:
                return r.json()

        return wrapper

    def update_auth_header(self, updated_header: Dict, overwrite: bool = False):
        """
        Updates the default auth header by providing new values.

        Args:
            updated_header: An updated header which will be used to update the current header.
            overwrite: If `False`, the existing header will be updated with new header. If `True`, the new header will
                overwrite (replace) the current authentication header.
        """

        if overwrite is False:
            self._auth_header.update(updated_header)
        else:
            self._auth_header = updated_header

    def get_raw(self, endpoint_path: Optional[str] = None, params: Dict = None, headers: Dict = None,
                is_absolute_path: bool = False, cookies: Cookie = None,
                ignore_auth: bool = False, **kwargs) -> requests.Response:
        """
        Constructs a requests GET call with specified url and kwargs to process the result.

        Args:
            endpoint_path: Relative URL path or absolute URL to which the request will be made.
                By default a relative path is expected and will be appended to the `self.base_url` value.

                Depending on the value of `is_absolute_path`, the value will be either appended to `self.base_url`,
                or used as an absolute URL.
            params: Dictionary to send in the query string for the request.
            headers: Dictionary of HTTP Headers to send with the request.
            is_absolute_path: A boolean value specifying, whether the URL specified in `endpoint_path` parameter
                is an absolute path or not.

                If set to False, the value of `endpoint_path` will be appended to `self.base_url` using
                [`urllib.parse.urljoin()`](https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urljoin)
                function.

                If set to True, base url will be overridden and the value of the `endpoint_path` will
                used instead.
            cookies: Dict or CookieJar object of cookies to send with the request
            ignore_auth: Boolean marking, whether the default auth_header should be ignored.
            **kwargs: All other keyword arguments supported by
                [`requests.request`](https://requests.readthedocs.io/en/latest/api/#requests.request).

        Returns:
            A [`requests.Response`](https://requests.readthedocs.io/en/latest/api/#requests.Response) object.
        """

        method = 'GET'
        return self._request_raw(method, endpoint_path, params=params, headers=headers, cookies=cookies,
                                 is_absolute_path=is_absolute_path, ignore_auth=ignore_auth, **kwargs)

    @response_error_handling
    def get(self, endpoint_path: Optional[str] = None, params: Dict = None, headers: Dict = None,
            is_absolute_path: bool = False, cookies: Cookie = None,
            ignore_auth: bool = False, **kwargs) -> requests.Response:
        """
        Constructs a requests GET call with specified url and kwargs to process the result.

        Args:
            endpoint_path: Relative URL path or absolute URL to which the request will be made.
                By default a relative path is expected and will be appended to the `self.base_url` value.

                Depending on the value of `is_absolute_path`, the value will be either appended to `self.base_url`,
                or used as an absolute URL.
            params: Dictionary to send in the query string for the request.
            headers: Dictionary of HTTP Headers to send with the request.
            is_absolute_path: A boolean value specifying, whether the URL specified in `endpoint_path` parameter
                is an absolute path or not.

                If set to False, the value of `endpoint_path` will be appended to `self.base_url` using
                [`urllib.parse.urljoin()`](https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urljoin)
                function.

                If set to True, base url will be overridden and the value of the `endpoint_path` will
                used instead.
            cookies: Dict or CookieJar object of cookies to send with the request
            files: Dictionary of 'name': file-like-objects (or {'name': file-tuple}) for multipart encoding upload.
            ignore_auth: Boolean marking, whether the default auth_header should be ignored.
            **kwargs: All other keyword arguments supported by
                [`requests.request`](https://requests.readthedocs.io/en/latest/api/#requests.request).

        Returns:
            A JSON-encoded response of the request.

        Raises:
            requests.HTTPError: If the API request fails.
        """

        return self.get_raw(endpoint_path, params=params, headers=headers, cookies=cookies,
                            is_absolute_path=is_absolute_path, ignore_auth=ignore_auth, **kwargs)

    def post_raw(self, endpoint_path: Optional[str] = None, params: Dict = None, headers: Dict = None,
                 data: Dict = None, json: Dict = None, is_absolute_path: bool = False, cookies: Cookie = None,
                 files: Dict = None, ignore_auth: bool = False, **kwargs) -> requests.Response:
        """
        Constructs a requests POST call with specified url and kwargs to process the result.

        Args:
            endpoint_path: Relative URL path or absolute URL to which the request will be made.
                By default a relative path is expected and will be appended to the `self.base_url` value.

                Depending on the value of `is_absolute_path`, the value will be either appended to `self.base_url`,
                or used as an absolute URL.
            params: Dictionary to send in the query string for the request.
            headers: Dictionary of HTTP Headers to send with the request.
            data: Dictionary to send in the body of the request.
            json: A JSON serializable Python object to send in the body of the request.
            is_absolute_path: A boolean value specifying, whether the URL specified in `endpoint_path` parameter
                is an absolute path or not.

                If set to False, the value of `endpoint_path` will be appended to `self.base_url` using
                [`urllib.parse.urljoin()`](https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urljoin)
                function.

                If set to True, base url will be overridden and the value of the `endpoint_path` will
                used instead.
            cookies: Dict or CookieJar object of cookies to send with the request
            files: Dictionary of 'name': file-like-objects (or {'name': file-tuple}) for multipart encoding upload.
            ignore_auth: Boolean marking, whether the default auth_header should be ignored.
            **kwargs: All other keyword arguments supported by
                [`requests.request`](https://requests.readthedocs.io/en/latest/api/#requests.request).

        Returns:
            A [`requests.Response`](https://requests.readthedocs.io/en/latest/api/#requests.Response) object.
        """

        method = 'POST'
        return self._request_raw(method, endpoint_path, params=params, headers=headers, data=data, json=json,
                                 cookies=cookies, is_absolute_path=is_absolute_path, files=files,
                                 ignore_auth=ignore_auth, **kwargs)

    @response_error_handling
    def post(self, endpoint_path: Optional[str] = None, params: Dict = None, headers: Dict = None, data: Dict = None,
             json: Dict = None, is_absolute_path: bool = False, cookies: Cookie = None, files: Dict = None,
             ignore_auth: bool = False, **kwargs) -> requests.Response:
        """
        Constructs a requests POST call with specified url and kwargs to process the result.

        Args:
            endpoint_path: Relative URL path or absolute URL to which the request will be made.
                By default a relative path is expected and will be appended to the `self.base_url` value.

                Depending on the value of `is_absolute_path`, the value will be either appended to `self.base_url`,
                or used as an absolute URL.
            params: Dictionary to send in the query string for the request.
            headers: Dictionary of HTTP Headers to send with the request.
            data: Dictionary to send in the body of the request.
            json: A JSON serializable Python object to send in the body of the request.
            is_absolute_path: A boolean value specifying, whether the URL specified in `endpoint_path` parameter
                is an absolute path or not.

                If set to False, the value of `endpoint_path` will be appended to `self.base_url` using
                [`urllib.parse.urljoin()`](https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urljoin)
                function.

                If set to True, base url will be overridden and the value of the `endpoint_path` will
                used instead.
            cookies: Dict or CookieJar object of cookies to send with the request
            files: Dictionary of 'name': file-like-objects (or {'name': file-tuple}) for multipart encoding upload.
            ignore_auth: Boolean marking, whether the default auth_header should be ignored.
            **kwargs: All other keyword arguments supported by
                [`requests.request`](https://requests.readthedocs.io/en/latest/api/#requests.request).

        Returns:
            A JSON-encoded response of the request.

        Raises:
            requests.HTTPError: If the API request fails.
        """

        return self.post_raw(endpoint_path, params=params, headers=headers, data=data, json=json, cookies=cookies,
                             is_absolute_path=is_absolute_path, files=files, ignore_auth=ignore_auth, **kwargs)

    def patch_raw(self, endpoint_path: Optional[str] = None, params: Dict = None, headers: Dict = None,
                  data: Dict = None, json: Dict = None, is_absolute_path: bool = False, cookies: Cookie = None,
                  files: Dict = None, ignore_auth: bool = False, **kwargs) -> requests.Response:
        """
        Constructs a requests PATCH call with specified url and kwargs to process the result.

        Args:
            endpoint_path: Relative URL path or absolute URL to which the request will be made.
                By default a relative path is expected and will be appended to the `self.base_url` value.

                Depending on the value of `is_absolute_path`, the value will be either appended to `self.base_url`,
                or used as an absolute URL.
            params: Dictionary to send in the query string for the request.
            headers: Dictionary of HTTP Headers to send with the request.
            data: Dictionary to send in the body of the request.
            json: A JSON serializable Python object to send in the body of the request.
            is_absolute_path: A boolean value specifying, whether the URL specified in `endpoint_path` parameter
                is an absolute path or not.

                If set to False, the value of `endpoint_path` will be appended to `self.base_url` using
                [`urllib.parse.urljoin()`](https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urljoin)
                function.

                If set to True, base url will be overridden and the value of the `endpoint_path` will
                used instead.
            cookies: Dict or CookieJar object of cookies to send with the request
            files: Dictionary of 'name': file-like-objects (or {'name': file-tuple}) for multipart encoding upload.
            ignore_auth: Boolean marking, whether the default auth_header should be ignored.
            **kwargs: All other keyword arguments supported by
                [`requests.request`](https://requests.readthedocs.io/en/latest/api/#requests.request).

        Returns:
            A [`requests.Response`](https://requests.readthedocs.io/en/latest/api/#requests.Response) object.
        """

        method = 'PATCH'
        return self._request_raw(method, endpoint_path, params=params, headers=headers, data=data, json=json,
                                 cookies=cookies, is_absolute_path=is_absolute_path, files=files,
                                 ignore_auth=ignore_auth, **kwargs)

    @response_error_handling
    def patch(self, endpoint_path: Optional[str] = None, params: Dict = None, headers: Dict = None, data: Dict = None,
              json: Dict = None, is_absolute_path: bool = False, cookies: Cookie = None, files: Dict = None,
              ignore_auth: bool = False, **kwargs) -> requests.Response:
        """
        Constructs a requests PATCH call with specified url and kwargs to process the result.

        Args:
            endpoint_path: Relative URL path or absolute URL to which the request will be made.
                By default a relative path is expected and will be appended to the `self.base_url` value.

                Depending on the value of `is_absolute_path`, the value will be either appended to `self.base_url`,
                or used as an absolute URL.
            params: Dictionary to send in the query string for the request.
            headers: Dictionary of HTTP Headers to send with the request.
            data: Dictionary to send in the body of the request.
            json: A JSON serializable Python object to send in the body of the request.
            is_absolute_path: A boolean value specifying, whether the URL specified in `endpoint_path` parameter
                is an absolute path or not.

                If set to False, the value of `endpoint_path` will be appended to `self.base_url` using
                [`urllib.parse.urljoin()`](https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urljoin)
                function.

                If set to True, base url will be overridden and the value of the `endpoint_path` will
                used instead.
            cookies: Dict or CookieJar object of cookies to send with the request
            files: Dictionary of 'name': file-like-objects (or {'name': file-tuple}) for multipart encoding upload.
            ignore_auth: Boolean marking, whether the default auth_header should be ignored.
            **kwargs: All other keyword arguments supported by
                [`requests.request`](https://requests.readthedocs.io/en/latest/api/#requests.request).

        Returns:
            A JSON-encoded response of the request.

        Raises:
            requests.HTTPError: If the API request fails.
        """

        return self.patch_raw(endpoint_path, params=params, headers=headers, data=data, json=json, cookies=cookies,
                              is_absolute_path=is_absolute_path, files=files, ignore_auth=ignore_auth, **kwargs)

    def update_raw(self, endpoint_path: Optional[str] = None, params: Dict = None, headers: Dict = None,
                   data: Dict = None, json: Dict = None, is_absolute_path: bool = False, cookies: Cookie = None,
                   files: Dict = None, ignore_auth: bool = False, **kwargs) -> requests.Response:
        """
        Constructs a requests UPDATE call with specified url and kwargs to process the result.

        Args:
            endpoint_path: Relative URL path or absolute URL to which the request will be made.
                By default a relative path is expected and will be appended to the `self.base_url` value.

                Depending on the value of `is_absolute_path`, the value will be either appended to `self.base_url`,
                or used as an absolute URL.
            params: Dictionary to send in the query string for the request.
            headers: Dictionary of HTTP Headers to send with the request.
            data: Dictionary to send in the body of the request.
            json: A JSON serializable Python object to send in the body of the request.
            is_absolute_path: A boolean value specifying, whether the URL specified in `endpoint_path` parameter
                is an absolute path or not.

                If set to False, the value of `endpoint_path` will be appended to `self.base_url` using
                [`urllib.parse.urljoin()`](https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urljoin)
                function.

                If set to True, base url will be overridden and the value of the `endpoint_path` will
                used instead.
            cookies: Dict or CookieJar object of cookies to send with the request
            files: Dictionary of 'name': file-like-objects (or {'name': file-tuple}) for multipart encoding upload.
            ignore_auth: Boolean marking, whether the default auth_header should be ignored.
            **kwargs: All other keyword arguments supported by
                [`requests.request`](https://requests.readthedocs.io/en/latest/api/#requests.request).

        Returns:
            A [`requests.Response`](https://requests.readthedocs.io/en/latest/api/#requests.Response) object.
        """

        method = 'UPDATE'
        return self._request_raw(method, endpoint_path, params=params, headers=headers, data=data, json=json,
                                 cookies=cookies, is_absolute_path=is_absolute_path, files=files,
                                 ignore_auth=ignore_auth, **kwargs)

    @response_error_handling
    def update(self, endpoint_path: Optional[str] = None, params: Dict = None, headers: Dict = None, data: Dict = None,
               json: Dict = None, is_absolute_path: bool = False, cookies: Cookie = None, files: Dict = None,
               ignore_auth: bool = False, **kwargs) -> requests.Response:
        """
        Constructs a requests UPDATE call with specified url and kwargs to process the result.

        Args:
            endpoint_path: Relative URL path or absolute URL to which the request will be made.
                By default a relative path is expected and will be appended to the `self.base_url` value.

                Depending on the value of `is_absolute_path`, the value will be either appended to `self.base_url`,
                or used as an absolute URL.
            params: Dictionary to send in the query string for the request.
            headers: Dictionary of HTTP Headers to send with the request.
            data: Dictionary to send in the body of the request.
            json: A JSON serializable Python object to send in the body of the request.
            is_absolute_path: A boolean value specifying, whether the URL specified in `endpoint_path` parameter
                is an absolute path or not.

                If set to False, the value of `endpoint_path` will be appended to `self.base_url` using
                [`urllib.parse.urljoin()`](https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urljoin)
                function.

                If set to True, base url will be overridden and the value of the `endpoint_path` will
                used instead.
            cookies: Dict or CookieJar object of cookies to send with the request
            files: Dictionary of 'name': file-like-objects (or {'name': file-tuple}) for multipart encoding upload.
            ignore_auth: Boolean marking, whether the default auth_header should be ignored.
            **kwargs: All other keyword arguments supported by
                [`requests.request`](https://requests.readthedocs.io/en/latest/api/#requests.request).

        Returns:
            A JSON-encoded response of the request.

        Raises:
            requests.HTTPError: If the API request fails.
        """

        return self.update_raw(endpoint_path, params=params, headers=headers, data=data, json=json, cookies=cookies,
                               is_absolute_path=is_absolute_path, files=files, ignore_auth=ignore_auth, **kwargs)

    def put_raw(self, endpoint_path: Optional[str] = None, params: Dict = None, headers: Dict = None,
                data: Dict = None, json: Dict = None, is_absolute_path: bool = False, cookies: Cookie = None,
                files: Dict = None, ignore_auth: bool = False, **kwargs) -> requests.Response:
        """
        Constructs a requests PUT call with specified url and kwargs to process the result.

        Args:
            endpoint_path: Relative URL path or absolute URL to which the request will be made.
                By default a relative path is expected and will be appended to the `self.base_url` value.

                Depending on the value of `is_absolute_path`, the value will be either appended to `self.base_url`,
                or used as an absolute URL.
            params: Dictionary to send in the query string for the request.
            headers: Dictionary of HTTP Headers to send with the request.
            data: Dictionary to send in the body of the request.
            json: A JSON serializable Python object to send in the body of the request.
            is_absolute_path: A boolean value specifying, whether the URL specified in `endpoint_path` parameter
                is an absolute path or not.

                If set to False, the value of `endpoint_path` will be appended to `self.base_url` using
                [`urllib.parse.urljoin()`](https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urljoin)
                function.

                If set to True, base url will be overridden and the value of the `endpoint_path` will
                used instead.
            cookies: Dict or CookieJar object of cookies to send with the request
            files: Dictionary of 'name': file-like-objects (or {'name': file-tuple}) for multipart encoding upload.
            ignore_auth: Boolean marking, whether the default auth_header should be ignored.
            **kwargs: All other keyword arguments supported by
                [`requests.request`](https://requests.readthedocs.io/en/latest/api/#requests.request).

        Returns:
            A [`requests.Response`](https://requests.readthedocs.io/en/latest/api/#requests.Response) object.
        """

        method = 'PUT'
        return self._request_raw(method, endpoint_path, params=params, headers=headers, data=data, json=json,
                                 cookies=cookies, is_absolute_path=is_absolute_path, files=files,
                                 ignore_auth=ignore_auth, **kwargs)

    @response_error_handling
    def put(self, endpoint_path: Optional[str] = None, params: Dict = None, headers: Dict = None, data: Dict = None,
            json: Dict = None, is_absolute_path: bool = False, cookies: Cookie = None, files: Dict = None,
            ignore_auth: bool = False, **kwargs) -> requests.Response:
        """
        Constructs a requests PUT call with specified url and kwargs to process the result.

        Args:
            endpoint_path: Relative URL path or absolute URL to which the request will be made.
                By default a relative path is expected and will be appended to the `self.base_url` value.

                Depending on the value of `is_absolute_path`, the value will be either appended to `self.base_url`,
                or used as an absolute URL.
            params: Dictionary to send in the query string for the request.
            headers: Dictionary of HTTP Headers to send with the request.
            data: Dictionary to send in the body of the request.
            json: A JSON serializable Python object to send in the body of the request.
            is_absolute_path: A boolean value specifying, whether the URL specified in `endpoint_path` parameter
                is an absolute path or not.

                If set to False, the value of `endpoint_path` will be appended to `self.base_url` using
                [`urllib.parse.urljoin()`](https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urljoin)
                function.

                If set to True, base url will be overridden and the value of the `endpoint_path` will
                used instead.
            cookies: Dict or CookieJar object of cookies to send with the request
            files: Dictionary of 'name': file-like-objects (or {'name': file-tuple}) for multipart encoding upload.
            ignore_auth: Boolean marking, whether the default auth_header should be ignored.
            **kwargs: All other keyword arguments supported by
                [`requests.request`](https://requests.readthedocs.io/en/latest/api/#requests.request).

        Returns:
            A JSON-encoded response of the request.

        Raises:
            requests.HTTPError: If the API request fails.
        """

        return self.put_raw(endpoint_path, params=params, headers=headers, data=data, json=json, cookies=cookies,
                            is_absolute_path=is_absolute_path, files=files, ignore_auth=ignore_auth, **kwargs)

    def delete_raw(self, endpoint_path: Optional[str] = None, params: Dict = None, headers: Dict = None,
                   data: Dict = None, json: Dict = None, is_absolute_path: bool = False, cookies: Cookie = None,
                   files: Dict = None, ignore_auth: bool = False, **kwargs) -> requests.Response:
        """
        Constructs a requests DELETE call with specified url and kwargs to process the result.

        Args:
            endpoint_path: Relative URL path or absolute URL to which the request will be made.
                By default a relative path is expected and will be appended to the `self.base_url` value.

                Depending on the value of `is_absolute_path`, the value will be either appended to `self.base_url`,
                or used as an absolute URL.
            params: Dictionary to send in the query string for the request.
            headers: Dictionary of HTTP Headers to send with the request.
            data: Dictionary to send in the body of the request.
            json: A JSON serializable Python object to send in the body of the request.
            is_absolute_path: A boolean value specifying, whether the URL specified in `endpoint_path` parameter
                is an absolute path or not.

                If set to False, the value of `endpoint_path` will be appended to `self.base_url` using
                [`urllib.parse.urljoin()`](https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urljoin)
                function.

                If set to True, base url will be overridden and the value of the `endpoint_path` will
                used instead.
            cookies: Dict or CookieJar object of cookies to send with the request
            files: Dictionary of 'name': file-like-objects (or {'name': file-tuple}) for multipart encoding upload.
            ignore_auth: Boolean marking, whether the default auth_header should be ignored.
            **kwargs: All other keyword arguments supported by
                [`requests.request`](https://requests.readthedocs.io/en/latest/api/#requests.request).

        Returns:
            A [`requests.Response`](https://requests.readthedocs.io/en/latest/api/#requests.Response) object.
        """

        method = 'DELETE'
        return self._request_raw(method, endpoint_path, params=params, headers=headers, data=data, json=json,
                                 cookies=cookies, is_absolute_path=is_absolute_path, files=files,
                                 ignore_auth=ignore_auth, **kwargs)

    @response_error_handling
    def delete(self, endpoint_path: Optional[str] = None, params: Dict = None, headers: Dict = None, data: Dict = None,
               json: Dict = None, is_absolute_path: bool = False, cookies: Cookie = None, files: Dict = None,
               ignore_auth: bool = False, **kwargs) -> requests.Response:
        """
        Constructs a requests DELETE call with specified url and kwargs to process the result.

        Args:
            endpoint_path: Relative URL path or absolute URL to which the request will be made.
                By default a relative path is expected and will be appended to the `self.base_url` value.

                Depending on the value of `is_absolute_path`, the value will be either appended to `self.base_url`,
                or used as an absolute URL.
            params: Dictionary to send in the query string for the request.
            headers: Dictionary of HTTP Headers to send with the request.
            data: Dictionary to send in the body of the request.
            json: A JSON serializable Python object to send in the body of the request.
            is_absolute_path: A boolean value specifying, whether the URL specified in `endpoint_path` parameter
                is an absolute path or not.

                If set to False, the value of `endpoint_path` will be appended to `self.base_url` using
                [`urllib.parse.urljoin()`](https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urljoin)
                function.

                If set to True, base url will be overridden and the value of the `endpoint_path` will
                used instead.
            cookies: Dict or CookieJar object of cookies to send with the request
            files: Dictionary of 'name': file-like-objects (or {'name': file-tuple}) for multipart encoding upload.
            ignore_auth: Boolean marking, whether the default auth_header should be ignored.
            **kwargs: All other keyword arguments supported by
                [`requests.request`](https://requests.readthedocs.io/en/latest/api/#requests.request).

        Returns:
            A JSON-encoded response of the request.

        Raises:
            requests.HTTPError: If the API request fails.
        """

        return self.delete_raw(endpoint_path, params=params, headers=headers, data=data, json=json, cookies=cookies,
                               is_absolute_path=is_absolute_path, files=files, ignore_auth=ignore_auth, **kwargs)
