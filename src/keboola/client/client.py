import logging
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

METHOD_RETRY_WHITELIST = ('GET', 'POST', 'PATCH', 'UPDATE', 'PUT', 'DELETE')


class HttpClientBase:
    """
    Base class for implementing a single Http client related to some REST API.

    """

    def __init__(self, base_url, max_retries=10, backoff_factor=0.3,
                 status_forcelist=(500, 502, 504), default_http_header=None, auth_header=None, auth=None,
                 default_params=None,
                 method_whitelist=METHOD_RETRY_WHITELIST):
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
        self.base_url = base_url
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
            method_whitelist=self.method_whitelist
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    def get_raw(self, *args, **kwargs):
        """
        Construct a requests GET call with args and kwargs and process the
        results.


        Args:
            url (str): requested url
            params (dict): additional url params to be passed to the underlying
                requests.get
            **kwargs: Key word arguments to pass to the get requests.get
                      ignore_auth: True to skip authentication

        Returns:
            r (requests.Response): :class:`Response <Response>` object.

        Raises:
            requests.HTTPError: If the API request fails.
        """
        method = 'GET'

        r = self._request_raw(method, *args, **kwargs)
        return r

    def get(self, url, params=None, ignore_auth=False, **kwargs):
        """
        Construct a requests GET call with args and kwargs and process the
        results.

        Args:
            *args: Positional arguments to pass to the post request.
                Accepts supported params in requests.sessions.Session#request
            **kwargs: Key word arguments to pass to the post request.
                Accepts supported params in requests.sessions.Session#request
                eg. params = {'locId':'1'}, header = {some additional header}
                parameters and headers are appended to the default ones
            ignore_auth: True to skip authentication


        Returns:
            body: json reposonse json-encoded content of a response

        Raises:
            requests.HTTPError: If the API request fails.
        """
        kwargs['ignore_auth'] = ignore_auth
        if params:
            kwargs['params'] = params
        kwargs['url'] = url
        r = self.get_raw(**kwargs)
        return r.json()

    def post_raw(self, *args, **kwargs):
        """
        Construct a requests POST call with args and kwargs and process the
        results.

        Args:
            *args: Positional arguments to pass to the post request.
               Accepts supported params in requests.sessions.Session#request
            **kwargs: Key word arguments to pass to the post request.
               Accepts supported params in requests.sessions.Session#request
               eg. params = {'locId':'1'}, header = {some additional header}
               parameters and headers are appended to the default ones
               ignore_auth: True to skip authentication

        Returns:
            Response: Returns :class:`Response <Response>` object.

        """
        method = 'POST'

        r = self._request_raw(method, *args, **kwargs)
        return r

    def post(self, *args, ignore_auth=False, **kwargs):
        """
        Construct a requests POST call with args and kwargs and process the
        results.

        Args:
            *args: Positional arguments to pass to the post request.
               Accepts supported params in requests.sessions.Session#request
            **kwargs: Key word arguments to pass to the post request.
               Accepts supported params in requests.sessions.Session#request
               eg. params = {'locId':'1'}, header = {some additional header}
               parameters and headers are appended to the default ones
            ignore_auth: True to skip authentication


        Returns:
            body: json reposonse json-encoded content of a response

        Raises:
            requests.HTTPError: If the API request fails.
        """

        try:
            kwargs['ignore_auth'] = ignore_auth
            r = self.post_raw(*args, **kwargs)
            r.raise_for_status()
        except requests.HTTPError as e:
            logging.warning(e, exc_info=True)
            # Handle different error codes
            raise
        else:
            return r.json()

    def patch_raw(self, *args, **kwargs):
        """
        Construct a requests PATCH call with args and kwargs and process the
        results.

        Args:
            *args: Positional arguments to pass to the post request.
               Accepts supported params in requests.sessions.Session#request
            **kwargs: Key word arguments to pass to the post request.
               Accepts supported params in requests.sessions.Session#request
               eg. params = {'locId':'1'}, header = {some additional header}
               parameters and headers are appended to the default ones
               ignore_auth: True to skip authentication

        Returns:
            Response: Returns :class:`Response <Response>` object.

        """
        method = 'PATCH'

        r = self._request_raw(method, *args, **kwargs)
        return r

    def patch(self, *args, ignore_auth=False, **kwargs):
        """
        Construct a requests PATCH call with args and kwargs and process the
        results.

        Args:
            *args: Positional arguments to pass to the post request.
               Accepts supported params in requests.sessions.Session#request
            **kwargs: Key word arguments to pass to the post request.
               Accepts supported params in requests.sessions.Session#request
               eg. params = {'locId':'1'}, header = {some additional header}
               parameters and headers are appended to the default ones
            ignore_auth: True to skip authentication


        Returns:
            body: json reposonse json-encoded content of a response

        Raises:
            requests.HTTPError: If the API request fails.
        """

        try:
            kwargs['ignore_auth'] = ignore_auth
            r = self.patch_raw(*args, **kwargs)
            r.raise_for_status()
        except requests.HTTPError as e:
            logging.warning(e, exc_info=True)
            # Handle different error codes
            raise
        else:
            return r.json()

    def update_raw(self, *args, **kwargs):
        """
        Construct a requests UPDATE call with args and kwargs and process the
        results.

        Args:
            *args: Positional arguments to pass to the post request.
               Accepts supported params in requests.sessions.Session#request
            **kwargs: Key word arguments to pass to the post request.
               Accepts supported params in requests.sessions.Session#request
               eg. params = {'locId':'1'}, header = {some additional header}
               parameters and headers are appended to the default ones
               ignore_auth: True to skip authentication

        Returns:
            Response: Returns :class:`Response <Response>` object.

        """
        method = 'UPDATE'

        r = self._request_raw(method, *args, **kwargs)
        return r

    def update(self, *args, ignore_auth=False, **kwargs):
        """
        Construct a requests UPDATE call with args and kwargs and process the
        results.

        Args:
            *args: Positional arguments to pass to the post request.
               Accepts supported params in requests.sessions.Session#request
            **kwargs: Key word arguments to pass to the post request.
               Accepts supported params in requests.sessions.Session#request
               eg. params = {'locId':'1'}, header = {some additional header}
               parameters and headers are appended to the default ones
            ignore_auth: True to skip authentication


        Returns:
            body: json reposonse json-encoded content of a response

        Raises:
            requests.HTTPError: If the API request fails.
        """

        try:
            kwargs['ignore_auth'] = ignore_auth
            r = self.update_raw(*args, **kwargs)
            r.raise_for_status()
        except requests.HTTPError as e:
            logging.warning(e, exc_info=True)
            # Handle different error codes
            raise
        else:
            return r.json()

    def put_raw(self, *args, **kwargs):
        """
        Construct a requests PUT call with args and kwargs and process the
        results.

        Args:
            *args: Positional arguments to pass to the post request.
               Accepts supported params in requests.sessions.Session#request
            **kwargs: Key word arguments to pass to the post request.
               Accepts supported params in requests.sessions.Session#request
               eg. params = {'locId':'1'}, header = {some additional header}
               parameters and headers are appended to the default ones
                ignore_auth: True to skip authentication

        Returns:
            Response: Returns :class:`Response <Response>` object.

        Raises:
            requests.HTTPError: If the API request fails.
        """
        method = 'PUT'

        r = self._request_raw(method, *args, **kwargs)
        return r

    def put(self, *args, ignore_auth=False, **kwargs):
        """
        Construct a requests PUT call with args and kwargs and process the
        results.

        Args:
            *args: Positional arguments to pass to the post request.
               Accepts supported params in requests.sessions.Session#request
            ignore_auth: True to skip authentication
            **kwargs: Key word arguments to pass to the post request.
               Accepts supported params in requests.sessions.Session#request
               eg. params = {'locId':'1'}, header = {some additional header}
               parameters and headers are appended to the default ones


        Returns:
            body: json reposonse json-encoded content of a response

        Raises:
            requests.HTTPError: If the API request fails.
        """

        try:
            kwargs['ignore_auth'] = ignore_auth
            r = self.put_raw(*args, **kwargs)
            r.raise_for_status()
        except requests.HTTPError as e:
            logging.warning(e, exc_info=True)
            # Handle different error codes
            raise
        else:
            return r.json()

    def _request_raw(self, method, *args, **kwargs):
        """
        Construct a requests call with args and kwargs and process the
        results.

        Args:
            method: (PUT/POST/PATCH/GET/UPDATE/DELETE)
            *args: Positional arguments to pass to the post request.
                Accepts supported params in requests.sessions.Session#request
            **kwargs: Key word arguments to pass to the post request.
                Accepts supported params in requests.sessions.Session#request
                eg. params = {'locId':'1'}, header = {some additional header}
                parameters and headers are appended to the default ones
                ignore_auth  - True to skip authentication



        Returns:
            Response: Returns :class:`Response <Response>` object.

        Raises:
            requests.HTTPError: If the API request fails.
        """
        s = requests.Session()
        headers = kwargs.pop('headers', {})
        headers.update(self._default_header)
        if not kwargs.pop('ignore_auth', False):
            headers.update(self._auth_header)
            s.headers.update(headers)
            s.auth = self._auth
        s.headers.update(headers)

        # set default params
        params = kwargs.pop('params', {})

        if params is None:
            params = {}

        if self._default_params:

            all_pars = {**params, **self._default_params}
            kwargs.update({'params': all_pars})

        else:
            kwargs.update({'params': params})

        r = self.requests_retry_session(session=s).request(method, *args, **kwargs)
        return r

    def delete_raw(self, *args, **kwargs):
        """
        Construct a requests DELETE call with args and kwargs and process the
        results.

        Args:
            *args: Positional arguments to pass to the post request.
               Accepts supported params in requests.sessions.Session#request
            **kwargs: Key word arguments to pass to the post request.
               Accepts supported params in requests.sessions.Session#request
               eg. params = {'locId':'1'}, header = {some additional header}
               parameters and headers are appended to the default ones
                ignore_auth: True to skip authentication

        Returns:
            Response: Returns :class:`Response <Response>` object.

        Raises:
            requests.HTTPError: If the API request fails.
        """
        method = 'DELETE'

        r = self._request_raw(method, *args, **kwargs)
        return r

    def delete(self, *args, ignore_auth=False, **kwargs):
        """
        Construct a requests DELETE call with args and kwargs and process the
        results.

        Args:
            *args: Positional arguments to pass to the post request.
               Accepts supported params in requests.sessions.Session#request
            ignore_auth: True to skip authentication
            **kwargs: Key word arguments to pass to the post request.
               Accepts supported params in requests.sessions.Session#request
               eg. params = {'locId':'1'}, header = {some additional header}
               parameters and headers are appended to the default ones


        Returns:
            body: json reposonse json-encoded content of a response

        Raises:
            requests.HTTPError: If the API request fails.
        """

        try:
            kwargs['ignore_auth'] = ignore_auth
            r = self.delete_raw(*args, **kwargs)
            r.raise_for_status()
        except requests.HTTPError as e:
            logging.warning(e, exc_info=True)
            # Handle different error codes
            raise
        else:
            return r.json()
