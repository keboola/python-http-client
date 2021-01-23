import functools
import logging
import requests
import urllib.parse as urlparse
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from typing import List, Dict, Union, Tuple
from http.cookiejar import CookieJar

Cookie = Union[Dict[str, str], CookieJar]
StatusForcelist = Union[List, Dict]

METHOD_RETRY_WHITELIST = ('GET', 'POST', 'PATCH', 'UPDATE', 'PUT', 'DELETE')


class HttpClient:
    """
    Base class for implementing a single Http client related to some REST API.

    """

    def __init__(self, base_url: str, max_retries: int = 10, backoff_factor: float = 0.3,
                 status_forcelist: StatusForcelist = (500, 502, 504), default_http_header: Dict = None,
                 auth_header: Dict = None, auth: Tuple = None, default_params: Dict = None,
                 method_whitelist: Tuple = METHOD_RETRY_WHITELIST):
        """
        Create an endpoint.

        Args:
            base_url: The base URL for this endpoint. e.g. https://exampleservice.com/api_v1/
            max_retries: Total number of retries to allow.
            backoff_factor:  A back-off factor to apply between attempts.
            status_forcelist:  A set of HTTP status codes that we should force a retry on. e.g. [500,502]
            default_http_header (dict): Default header to be sent with each request
                                        eg. {
                                                        'Content-Type' : 'application/json',
                                                        'Accept' : 'application/json'}
            auth_header (dict): Auth header to be sent with each request
                                        eg. {'Authorization': 'Bearer ' + token}
            auth: Default Authentication tuple or object to attach to (from  requests.Session().auth).
                    eg. auth = (user, password)
            default_params (dict): default parameters to be sent with each request eg. {'param':'value'}

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
        self.method_whitelist = method_whitelist

    def requests_retry_session(self, session=None):
        session = session or requests.Session()
        retry = Retry(
            total=self.max_retries,
            read=self.max_retries,
            connect=self.max_retries,
            backoff_factor=self.backoff_factor,
            status_forcelist=self.status_forcelist,
            allowed_methods=self.method_whitelist
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    def _request_raw(self, method: str, *endpoint_path: str, **kwargs) -> requests.Response:
        """
        Construct a requests call with args and kwargs and process the
        results.

        Args:
            method: A HTTP method to be used. One of PUT/POST/PATCH/GET/UPDATE/DELETE
            url: A URL or URL path.
            **kwargs: Key word arguments to pass to the requests.request.
                Accepts supported params in requests.sessions.Session#request
                eg. params = {'locId':'1'}, header = {some additional header}
                parameters and headers are appended to the default ones
                ignore_auth  - True to skip authentication
                is_absolute_path - False to append URL to base url; True to override base url with value of url arg.

        Returns:
            A requests.Response object.
        """
        s = requests.Session()

        print(endpoint_path)

        # URL Specification
        if kwargs.pop('is_absolute_path', False) is False:
            if endpoint_path != ():
                _endpoint = endpoint_path[0]
                endpoint = str(_endpoint).strip() if _endpoint is not None else ''
                url = urlparse.urljoin(self.base_url, endpoint)
            else:
                url = self.base_url
        else:
            url = endpoint_path[0]

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

        r = self.requests_retry_session(session=s).request(method, url, **kwargs)
        return r

    def response_error_handling(func):
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

    def get_raw(self, *endpoint_path: str, params: Dict = None, headers: Dict = None, is_absolute_path: bool = False,
                cookies: Cookie = None, ignore_auth: bool = False, **kwargs) -> requests.Response:
        """
        Constructs a requests GET call with specified url and kwargs to process the result.

        Args:
            endpoint_path: URL path or absolute URL to which the request will be made. Depending on the value of
                `is_absolute_path`, the value will be either appended to self.base_url, or used as an absolute URL.
            params: Dictionary to send in the query string for the request.
            headers: Dictionary of HTTP Headers to send with the request.
            is_absolute_path: A boolean value specifying, whether the URL specified in `url` parameter is absolute or
                not. If set to False, the value of `url` will be appended to `self.base_url` using
                `urllib.parse.urljoin()` function. If set to True, base url will be overriden and value of `url` wills
                accessed instead.
            cookies: Dict or CookieJar object of cookies to send with the request
            ignore_auth: Boolean marking, whether the `self._auth_header` should be ignored.
            **kwargs: All other keyword arguments supported by requests.request function.

        Returns:
            A requests.Response object.
        """

        method = 'GET'
        return self._request_raw(method, *endpoint_path, params=params, headers=headers, cookies=cookies,
                                 is_absolute_path=is_absolute_path, ignore_auth=ignore_auth, **kwargs)

    @response_error_handling
    def get(self, *endpoint_path: str, params: Dict = None, headers: Dict = None, is_absolute_path: bool = False,
            cookies: Cookie = None, ignore_auth: bool = False, **kwargs) -> requests.Response:
        """
        Constructs a requests GET call with specified url and kwargs to process the result.

        Args:
            endpoint_path: URL path or absolute URL to which the request will be made. Depending on the value of
                `is_absolute_path`, the value will be either appended to self.base_url, or used as an absolute URL.
            params: Dictionary to send in the query string for the request.
            headers: Dictionary of HTTP Headers to send with the request.
            is_absolute_path: A boolean value specifying, whether the URL specified in `url` parameter is absolute or
                not. If set to False, the value of `url` will be appended to `self.base_url` using
                `urllib.parse.urljoin()` function. If set to True, base url will be overriden and value of `url` wills
                accessed instead.
            cookies: Dict or CookieJar object of cookies to send with the request
            ignore_auth: Boolean marking, whether the `self._auth_header` should be ignored.
            **kwargs: All other keyword arguments supported by requests.request function.

        Returns:
            A JSON-encoded response of the request.

        Raises:
            requests.HTTPError: If the API request fails.
        """

        if not endpoint_path:
            endpoint_path = ''

        return self.get_raw(*endpoint_path, params=params, headers=headers, cookies=cookies,
                            is_absolute_path=is_absolute_path, ignore_auth=ignore_auth, **kwargs)

    def post_raw(self, *endpoint_path: str, params: Dict = None, headers: Dict = None, data: Dict = None,
                 json: Dict = None, is_absolute_path: bool = False, cookies: Cookie = None, files: Dict = None,
                 ignore_auth: bool = False, **kwargs) -> requests.Response:
        """
        Constructs a requests POST call with specified url and kwargs to process the result.

        Args:
            url: URL path or absolute URL to which the request will be made. Depending on the value of
                `is_absolute_path`, the value will be either appended to self.base_url, or used as an absolute URL.
            params: Dictionary to send in the query string for the request.
            headers: Dictionary of HTTP Headers to send with the request.
            data: Dictionary to send in the body of the request.
            json: A JSON serializable Python object to send in the body of the request.
            is_absolute_path: A boolean value specifying, whether the URL specified in `url` parameter is absolute or
                not. If set to False, the value of `url` will be appended to `self.base_url` using
                `urllib.parse.urljoin()` function. If set to True, base url will be overriden and value of `url` wills
                accessed instead.
            cookies: Dict or CookieJar object of cookies to send with the request
            files: Dictionary of 'name': file-like-objects (or {'name': file-tuple}) for multipart encoding upload.
            ignore_auth: Boolean marking, whether the `self._auth_header` should be ignored.
            **kwargs: All other keyword arguments supported by requests.request function.

        Returns:
            A requests.Response object.
        """

        if not endpoint_path:
            endpoint_path = ''

        method = 'POST'
        return self._request_raw(method, *endpoint_path, params=params, headers=headers, data=data, json=json,
                                 cookies=cookies, is_absolute_path=is_absolute_path, files=files,
                                 ignore_auth=ignore_auth, **kwargs)

    @response_error_handling
    def post(self, *endpoint_path: str, params: Dict = None, headers: Dict = None, data: Dict = None,
             json: Dict = None, is_absolute_path: bool = False, cookies: Cookie = None, files: Dict = None,
             ignore_auth: bool = False, **kwargs) -> requests.Response:
        """
        Constructs a requests POST call with specified url and kwargs to process the result.

        Args:
            url: URL path or absolute URL to which the request will be made. Depending on the value of
                `is_absolute_path`, the value will be either appended to self.base_url, or used as an absolute URL.
            params: Dictionary to send in the query string for the request.
            headers: Dictionary of HTTP Headers to send with the request.
            data: Dictionary to send in the body of the request.
            json: A JSON serializable Python object to send in the body of the request.
            is_absolute_path: A boolean value specifying, whether the URL specified in `url` parameter is absolute or
                not. If set to False, the value of `url` will be appended to `self.base_url` using
                `urllib.parse.urljoin()` function. If set to True, base url will be overriden and value of `url` wills
                accessed instead.
            cookies: Dict or CookieJar object of cookies to send with the request
            files: Dictionary of 'name': file-like-objects (or {'name': file-tuple}) for multipart encoding upload.
            ignore_auth: Boolean marking, whether the `self._auth_header` should be ignored.
            **kwargs: All other keyword arguments supported by requests.request function.

        Returns:
            A JSON-encoded response of the request.

        Raises:
            requests.HTTPError: If the API request fails.
        """

        if not endpoint_path:
            endpoint_path = ''

        return self.post_raw(*endpoint_path, params=params, headers=headers, data=data, json=json, cookies=cookies,
                             is_absolute_path=is_absolute_path, files=files, ignore_auth=ignore_auth, **kwargs)

    def patch_raw(self, *endpoint_path: str, params: Dict = None, headers: Dict = None, data: Dict = None,
                  json: Dict = None, is_absolute_path: bool = False, cookies: Cookie = None, files: Dict = None,
                  ignore_auth: bool = False, **kwargs) -> requests.Response:
        """
        Constructs a requests PATCH call with specified url and kwargs to process the result.

        Args:
            url: URL path or absolute URL to which the request will be made. Depending on the value of
                `is_absolute_path`, the value will be either appended to self.base_url, or used as an absolute URL.
            params: Dictionary to send in the query string for the request.
            headers: Dictionary of HTTP Headers to send with the request.
            data: Dictionary to send in the body of the request.
            json: A JSON serializable Python object to send in the body of the request.
            is_absolute_path: A boolean value specifying, whether the URL specified in `url` parameter is absolute or
                not. If set to False, the value of `url` will be appended to `self.base_url` using
                `urllib.parse.urljoin()` function. If set to True, base url will be overriden and value of `url` wills
                accessed instead.
            cookies: Dict or CookieJar object of cookies to send with the request
            files: Dictionary of 'name': file-like-objects (or {'name': file-tuple}) for multipart encoding upload.
            ignore_auth: Boolean marking, whether the `self._auth_header` should be ignored.
            **kwargs: All other keyword arguments supported by requests.request function.

        Returns:
            A requests.Response object.
        """

        method = 'PATCH'
        return self._request_raw(method, *endpoint_path, params=params, headers=headers, data=data, json=json,
                                 cookies=cookies, is_absolute_path=is_absolute_path, files=files,
                                 ignore_auth=ignore_auth, **kwargs)

    @response_error_handling
    def patch(self, *endpoint_path: str, params: Dict = None, headers: Dict = None, data: Dict = None,
              json: Dict = None, is_absolute_path: bool = False, cookies: Cookie = None, files: Dict = None,
              ignore_auth: bool = False, **kwargs) -> requests.Response:
        """
        Constructs a requests PATCH call with specified url and kwargs to process the result.

        Args:
            url: URL path or absolute URL to which the request will be made. Depending on the value of
                `is_absolute_path`, the value will be either appended to self.base_url, or used as an absolute URL.
            params: Dictionary to send in the query string for the request.
            headers: Dictionary of HTTP Headers to send with the request.
            data: Dictionary to send in the body of the request.
            json: A JSON serializable Python object to send in the body of the request.
            is_absolute_path: A boolean value specifying, whether the URL specified in `url` parameter is absolute or
                not. If set to False, the value of `url` will be appended to `self.base_url` using
                `urllib.parse.urljoin()` function. If set to True, base url will be overriden and value of `url` wills
                accessed instead.
            cookies: Dict or CookieJar object of cookies to send with the request
            files: Dictionary of 'name': file-like-objects (or {'name': file-tuple}) for multipart encoding upload.
            ignore_auth: Boolean marking, whether the `self._auth_header` should be ignored.
            **kwargs: All other keyword arguments supported by requests.request function.

        Returns:
            A JSON-encoded response of the request.

        Raises:
            requests.HTTPError: If the API request fails.
        """

        return self.patch_raw(*endpoint_path, params=params, headers=headers, data=data, json=json, cookies=cookies,
                              is_absolute_path=is_absolute_path, files=files, ignore_auth=ignore_auth, **kwargs)

    def update_raw(self, *endpoint_path: str, params: Dict = None, headers: Dict = None, data: Dict = None,
                   json: Dict = None, is_absolute_path: bool = False, cookies: Cookie = None, files: Dict = None,
                   ignore_auth: bool = False, **kwargs) -> requests.Response:
        """
        Constructs a requests UPDATE call with specified url and kwargs to process the result.

        Args:
            url: URL path or absolute URL to which the request will be made. Depending on the value of
                `is_absolute_path`, the value will be either appended to self.base_url, or used as an absolute URL.
            params: Dictionary to send in the query string for the request.
            headers: Dictionary of HTTP Headers to send with the request.
            data: Dictionary to send in the body of the request.
            json: A JSON serializable Python object to send in the body of the request.
            is_absolute_path: A boolean value specifying, whether the URL specified in `url` parameter is absolute or
                not. If set to False, the value of `url` will be appended to `self.base_url` using
                `urllib.parse.urljoin()` function. If set to True, base url will be overriden and value of `url` wills
                accessed instead.
            cookies: Dict or CookieJar object of cookies to send with the request
            files: Dictionary of 'name': file-like-objects (or {'name': file-tuple}) for multipart encoding upload.
            ignore_auth: Boolean marking, whether the `self._auth_header` should be ignored.
            **kwargs: All other keyword arguments supported by requests.request function.

        Returns:
            A requests.Response object.
        """

        method = 'UPDATE'
        return self._request_raw(method, *endpoint_path, params=params, headers=headers, data=data, json=json,
                                 cookies=cookies, is_absolute_path=is_absolute_path, files=files,
                                 ignore_auth=ignore_auth, **kwargs)

    @response_error_handling
    def update(self, *endpoint_path: str, params: Dict = None, headers: Dict = None, data: Dict = None,
               json: Dict = None, is_absolute_path: bool = False, cookies: Cookie = None, files: Dict = None,
               ignore_auth: bool = False, **kwargs) -> requests.Response:
        """
        Constructs a requests UPDATE call with specified url and kwargs to process the result.

        Args:
            url: URL path or absolute URL to which the request will be made. Depending on the value of
                `is_absolute_path`, the value will be either appended to self.base_url, or used as an absolute URL.
            params: Dictionary to send in the query string for the request.
            headers: Dictionary of HTTP Headers to send with the request.
            data: Dictionary to send in the body of the request.
            json: A JSON serializable Python object to send in the body of the request.
            is_absolute_path: A boolean value specifying, whether the URL specified in `url` parameter is absolute or
                not. If set to False, the value of `url` will be appended to `self.base_url` using
                `urllib.parse.urljoin()` function. If set to True, base url will be overriden and value of `url` wills
                accessed instead.
            cookies: Dict or CookieJar object of cookies to send with the request
            files: Dictionary of 'name': file-like-objects (or {'name': file-tuple}) for multipart encoding upload.
            ignore_auth: Boolean marking, whether the `self._auth_header` should be ignored.
            **kwargs: All other keyword arguments supported by requests.request function.

        Returns:
            A JSON-encoded response of the request.

        Raises:
            requests.HTTPError: If the API request fails.
        """

        return self.update_raw(*endpoint_path, params=params, headers=headers, data=data, json=json, cookies=cookies,
                               is_absolute_path=is_absolute_path, files=files, ignore_auth=ignore_auth, **kwargs)

    def put_raw(self, *endpoint_path: str, params: Dict = None, headers: Dict = None, data: Dict = None,
                json: Dict = None, is_absolute_path: bool = False, cookies: Cookie = None, files: Dict = None,
                ignore_auth: bool = False, **kwargs) -> requests.Response:
        """
        Constructs a requests PUT call with specified url and kwargs to process the result.

        Args:
            url: URL path or absolute URL to which the request will be made. Depending on the value of
                `is_absolute_path`, the value will be either appended to self.base_url, or used as an absolute URL.
            params: Dictionary to send in the query string for the request.
            headers: Dictionary of HTTP Headers to send with the request.
            data: Dictionary to send in the body of the request.
            json: A JSON serializable Python object to send in the body of the request.
            is_absolute_path: A boolean value specifying, whether the URL specified in `url` parameter is absolute or
                not. If set to False, the value of `url` will be appended to `self.base_url` using
                `urllib.parse.urljoin()` function. If set to True, base url will be overriden and value of `url` wills
                accessed instead.
            cookies: Dict or CookieJar object of cookies to send with the request
            files: Dictionary of 'name': file-like-objects (or {'name': file-tuple}) for multipart encoding upload.
            ignore_auth: Boolean marking, whether the `self._auth_header` should be ignored.
            **kwargs: All other keyword arguments supported by requests.request function.

        Returns:
            A requests.Response object.
        """

        method = 'PUT'
        return self._request_raw(method, *endpoint_path, params=params, headers=headers, data=data, json=json,
                                 cookies=cookies, is_absolute_path=is_absolute_path, files=files,
                                 ignore_auth=ignore_auth, **kwargs)

    @response_error_handling
    def put(self, *endpoint_path: str, params: Dict = None, headers: Dict = None, data: Dict = None,
            json: Dict = None, is_absolute_path: bool = False, cookies: Cookie = None, files: Dict = None,
            ignore_auth: bool = False, **kwargs) -> requests.Response:
        """
        Constructs a requests PUT call with specified url and kwargs to process the result.

        Args:
            url: URL path or absolute URL to which the request will be made. Depending on the value of
                `is_absolute_path`, the value will be either appended to self.base_url, or used as an absolute URL.
            params: Dictionary to send in the query string for the request.
            headers: Dictionary of HTTP Headers to send with the request.
            data: Dictionary to send in the body of the request.
            json: A JSON serializable Python object to send in the body of the request.
            is_absolute_path: A boolean value specifying, whether the URL specified in `url` parameter is absolute or
                not. If set to False, the value of `url` will be appended to `self.base_url` using
                `urllib.parse.urljoin()` function. If set to True, base url will be overriden and value of `url` wills
                accessed instead.
            cookies: Dict or CookieJar object of cookies to send with the request
            files: Dictionary of 'name': file-like-objects (or {'name': file-tuple}) for multipart encoding upload.
            ignore_auth: Boolean marking, whether the `self._auth_header` should be ignored.
            **kwargs: All other keyword arguments supported by requests.request function.

        Returns:
            A JSON-encoded response of the request.

        Raises:
            requests.HTTPError: If the API request fails.
        """

        return self.put_raw(*endpoint_path, params=params, headers=headers, data=data, json=json, cookies=cookies,
                            is_absolute_path=is_absolute_path, files=files, ignore_auth=ignore_auth, **kwargs)

    def delete_raw(self, *endpoint_path: str, params: Dict = None, headers: Dict = None, data: Dict = None,
                   json: Dict = None, is_absolute_path: bool = False, cookies: Cookie = None, files: Dict = None,
                   ignore_auth: bool = False, **kwargs) -> requests.Response:
        """
        Constructs a requests DELETE call with specified url and kwargs to process the result.

        Args:
            url: URL path or absolute URL to which the request will be made. Depending on the value of
                `is_absolute_path`, the value will be either appended to self.base_url, or used as an absolute URL.
            params: Dictionary to send in the query string for the request.
            headers: Dictionary of HTTP Headers to send with the request.
            data: Dictionary to send in the body of the request.
            json: A JSON serializable Python object to send in the body of the request.
            is_absolute_path: A boolean value specifying, whether the URL specified in `url` parameter is absolute or
                not. If set to False, the value of `url` will be appended to `self.base_url` using
                `urllib.parse.urljoin()` function. If set to True, base url will be overriden and value of `url` wills
                accessed instead.
            cookies: Dict or CookieJar object of cookies to send with the request
            files: Dictionary of 'name': file-like-objects (or {'name': file-tuple}) for multipart encoding upload.
            ignore_auth: Boolean marking, whether the `self._auth_header` should be ignored.
            **kwargs: All other keyword arguments supported by requests.request function.

        Returns:
            A requests.Response object.
        """

        method = 'DELETE'
        return self._request_raw(method, *endpoint_path, params=params, headers=headers, data=data, json=json,
                                 cookies=cookies, is_absolute_path=is_absolute_path, files=files,
                                 ignore_auth=ignore_auth, **kwargs)

    @response_error_handling
    def delete(self, *endpoint_path: str, params: Dict = None, headers: Dict = None, data: Dict = None,
               json: Dict = None, is_absolute_path: bool = False, cookies: Cookie = None, files: Dict = None,
               ignore_auth: bool = False, **kwargs) -> requests.Response:
        """
        Constructs a requests DELETE call with specified url and kwargs to process the result.

        Args:
            url: URL path or absolute URL to which the request will be made. Depending on the value of
                `is_absolute_path`, the value will be either appended to self.base_url, or used as an absolute URL.
            params: Dictionary to send in the query string for the request.
            headers: Dictionary of HTTP Headers to send with the request.
            data: Dictionary to send in the body of the request.
            json: A JSON serializable Python object to send in the body of the request.
            is_absolute_path: A boolean value specifying, whether the URL specified in `url` parameter is absolute or
                not. If set to False, the value of `url` will be appended to `self.base_url` using
                `urllib.parse.urljoin()` function. If set to True, base url will be overriden and value of `url` wills
                accessed instead.
            cookies: Dict or CookieJar object of cookies to send with the request
            files: Dictionary of 'name': file-like-objects (or {'name': file-tuple}) for multipart encoding upload.
            ignore_auth: Boolean marking, whether the `self._auth_header` should be ignored.
            **kwargs: All other keyword arguments supported by requests.request function.

        Returns:
            A JSON-encoded response of the request.

        Raises:
            requests.HTTPError: If the API request fails.
        """

        return self.delete_raw(*endpoint_path, params=params, headers=headers, data=data, json=json, cookies=cookies,
                               is_absolute_path=is_absolute_path, files=files, ignore_auth=ignore_auth, **kwargs)
