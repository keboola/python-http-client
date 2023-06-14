import httpx
import asyncio
from typing import Optional, Dict, Any, List
from urllib.parse import urljoin
from aiolimiter import AsyncLimiter


class AsyncHttpClient:
    """
    An asynchronous HTTP client that simplifies making requests to a specific API.
    """
    ALLOWED_METHODS = ['GET', 'POST', 'PATCH', 'UPDATE', 'PUT', 'DELETE']
    def __init__(
            self,
            base_url: str,
            retries: int = 3,
            timeout: Optional[float] = None,
            verify_ssl: bool = True,
            retry_status_codes: Optional[List[int]] = None,
            max_requests_per_second: Optional[int] = None,
            default_params: Optional[Dict[str, str]] = None,
            auth: Optional[tuple] = None,
            auth_header: Optional[Dict[str, str]] = None,
            default_headers: Optional[Dict[str, str]] = None,
            backoff_factor: float = 2.0
    ):
        """
        Initialize the AsyncHttpClient instance.

        Args:
            base_url (str): The base URL for the API.
            retries (int, optional): The maximum number of retries for failed requests. Defaults to 3.
            timeout (Optional[float], optional): The request timeout in seconds. Defaults to None.
            verify_ssl (bool, optional): Enable or disable SSL verification. Defaults to True.
            retry_status_codes (Optional[List[int]], optional): List of status codes to retry on. Defaults to None.
            max_requests_per_second (Optional[int], optional): Maximum number of requests per second. Defaults to None.
            default_params (Optional[Dict[str, str]], optional): Default query parameters for each request.
            auth (Optional[tuple], optional): Authentication credentials for each request. Defaults to None.
            auth_header (Optional[Dict[str, str]], optional): Authentication header for each request. Defaults to None.
            backoff_factor (float, optional): The backoff factor for retries. Defaults to 2.0.
        """
        self.base_url = base_url if base_url.endswith("/") else base_url + "/"
        self.retries = retries
        self.timeout = httpx.Timeout(timeout) if timeout else None
        self.verify_ssl = verify_ssl
        self.retry_status_codes = retry_status_codes or []
        self.default_params = default_params or {}
        self.auth = auth
        self._auth_header = auth_header or {}

        self.limiter = None
        if max_requests_per_second:
            one_reqeust_per_second_amount = float(1/int(max_requests_per_second))
            self.limiter = AsyncLimiter(1, one_reqeust_per_second_amount)

        self.default_headers = default_headers or {}
        self.backoff_factor = backoff_factor

        self.client = httpx.AsyncClient(timeout=self.timeout, verify=self.verify_ssl, headers=self.default_headers,
                                        auth=self.auth)

    async def _build_url(self, endpoint_path: Optional[str] = None, is_absolute_path=False) -> str:
        # build URL Specification
        url_path = str(endpoint_path).strip() if endpoint_path is not None else ''

        if not url_path:
            url = self.base_url
        elif not is_absolute_path:
            url = urljoin(self.base_url, endpoint_path)
        else:
            url = endpoint_path

        return url

    async def update_auth_header(self, updated_header: Dict, overwrite: bool = False):
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

    async def __aenter__(self):
        await self.client.__aenter__()
        return self

    async def __aexit__(self, *args):
        await self.client.__aexit__(*args)

    async def close(self):
        await self.client.aclose()

    async def _request(
            self,
            method: str,
            endpoint: Optional[str] = None,
            params: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
            **kwargs
    ) -> httpx.Response:


        is_absolute_path = kwargs.pop('is_absolute_path', False)
        url = await self._build_url(endpoint, is_absolute_path)

        all_params = {**self.default_params, **(params or {})}

        ignore_auth = kwargs.pop('ignore_auth', False)
        if ignore_auth:
            all_headers = {**self.default_headers, **(headers or {})}
        else:
            all_headers = {**self._auth_header, **self.default_headers, **(headers or {})}
            if self.auth:
                kwargs.update({'auth': self.auth})

        if all_params:
            kwargs.update({'params': all_params})
        if all_headers:
            kwargs.update({'headers': all_headers})

        response = None

        for retry_attempt in range(self.retries + 1):
            try:
                if self.limiter:
                    async with self.limiter:
                        response = await self.client.request(method, url=url, **kwargs)
                else:
                    response = await self.client.request(method, url=url, **kwargs)

                response.raise_for_status()

                return response

            except httpx.HTTPError:
                if response:
                    if response.status_code not in self.retry_status_codes:
                        raise

                if retry_attempt == self.retries:
                    raise
                backoff = self.backoff_factor ** retry_attempt
                await asyncio.sleep(backoff)

    async def get(self, endpoint: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        response = await self.get_raw(endpoint, **kwargs)
        return response.json()

    async def get_raw(self, endpoint: Optional[str] = None, **kwargs) -> httpx.Response:
        return await self._request("GET", endpoint, **kwargs)

    async def post(self, endpoint: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        response = await self.post_raw(endpoint, **kwargs)
        return response.json()

    async def post_raw(self, endpoint: Optional[str] = None, **kwargs) -> httpx.Response:
        return await self._request("POST", endpoint, **kwargs)

    async def put(self, endpoint: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        response = await self.put_raw(endpoint, **kwargs)
        return response.json()

    async def put_raw(self, endpoint: Optional[str] = None, **kwargs) -> httpx.Response:
        return await self._request("PUT", endpoint, **kwargs)

    async def patch(self, endpoint: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        response = await self.patch_raw(endpoint, **kwargs)
        return response.json()

    async def patch_raw(self, endpoint: Optional[str] = None, **kwargs) -> httpx.Response:
        return await self._request("PATCH", endpoint, **kwargs)

    async def delete(self, endpoint: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        response = await self.delete_raw(endpoint, **kwargs)
        return response.json()

    async def delete_raw(self, endpoint: Optional[str] = None, **kwargs) -> httpx.Response:
        return await self._request("DELETE", endpoint, **kwargs)

    async def process_multiple(self, jobs: List[Dict[str, Any]]):
        tasks = []

        for job in jobs:
            method = job['method']
            endpoint = job['endpoint']
            params = job.get('params')
            headers = job.get('headers')
            raw = job.get('raw', False)

            if method == 'GET':
                if raw:
                    task = self.get_raw(endpoint, params=params, headers=headers)
                else:
                    task = self.get(endpoint, params=params, headers=headers)
            elif method == 'POST':
                if raw:
                    task = self.post_raw(endpoint, params=params, headers=headers)
                else:
                    task = self.post(endpoint, params=params, headers=headers)
            elif method == 'PUT':
                if raw:
                    task = self.put_raw(endpoint, params=params, headers=headers)
                else:
                    task = self.put(endpoint, params=params, headers=headers)
            elif method == 'PATCH':
                if raw:
                    task = self.patch_raw(endpoint, params=params, headers=headers)
                else:
                    task = self.patch(endpoint, params=params, headers=headers)
            elif method == 'DELETE':
                if raw:
                    task = self.delete_raw(endpoint, params=params, headers=headers)
                else:
                    task = self.delete(endpoint, params=params, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")

            tasks.append(task)

        responses = await asyncio.gather(*tasks)
        return responses
