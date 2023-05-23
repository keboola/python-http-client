import random
import httpx
import asyncio
from typing import Optional, Dict, Any, List
from urllib.parse import urljoin


class AsyncHttpClient:
    """
    An asynchronous HTTP client that simplifies making requests to a specific API.
    """

    def __init__(
            self,
            base_url: str,
            retries: int = 3,
            timeout: Optional[float] = None,
            verify_ssl: bool = True,
            retry_status_codes: Optional[List[int]] = None,
            rate_limit: Optional[int] = None,
            default_params: Optional[Dict[str, str]] = None,
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
            rate_limit (Optional[int], optional): Maximum number of concurrent requests. Defaults to None.
            default_params (Optional[Dict[str, str]], optional): Default query parameters for each request.
            auth_header (Optional[Dict[str, str]], optional): Authentication header for each request. Defaults to None.
            backoff_factor (float, optional): The backoff factor for retries. Defaults to 2.0.
        """
        self.base_url = base_url if base_url.endswith("/") else base_url + "/"
        self.retries = retries
        self.timeout = httpx.Timeout(timeout) if timeout else None
        self.verify_ssl = verify_ssl
        self.retry_status_codes = retry_status_codes or []
        self.rate_limit = rate_limit
        self.default_params = default_params or {}
        self.auth_header = auth_header or {}
        self.semaphore = asyncio.Semaphore(rate_limit) if rate_limit else None
        self.default_headers = default_headers or {}
        self.backoff_factor = backoff_factor

        self.client = httpx.AsyncClient(timeout=self.timeout, verify=self.verify_ssl, headers=self.default_headers)

    async def _build_url(self, endpoint_path: Optional[str] = None, is_absolute_path=False):
        # build URL Specification
        url_path = str(endpoint_path).strip() if endpoint_path is not None else ''

        if not url_path:
            url = self.base_url
        elif not is_absolute_path:
            url = urljoin(self.base_url, endpoint_path)
        else:
            url = endpoint_path

        return url

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
            json: Optional[Dict[str, Any]] = None,
            **kwargs
    ) -> httpx.Response:
        # build URL Specification
        is_absolute_path = kwargs.pop('is_absolute_path', False)
        url = await self._build_url(endpoint, is_absolute_path)

        all_params = {**self.default_params, **(params or {})}
        all_headers = {**self.auth_header, **self.default_headers, **(headers or {})}  # include default headers

        for retry_attempt in range(self.retries + 1):
            try:
                if self.semaphore:
                    async with self.semaphore:
                        response = await self.client.request(
                            method,
                            url,
                            params=all_params,
                            headers=all_headers,
                            json=json,
                        )
                else:
                    response = await self.client.request(
                        method,
                        url,
                        params=all_params,
                        headers=all_headers,
                        json=json,
                    )
                if response.status_code not in self.retry_status_codes:
                    response.raise_for_status()
                return response
            except httpx.HTTPError:
                if retry_attempt == self.retries:
                    raise
                backoff_factor = 2 ** retry_attempt
                await asyncio.sleep(random.uniform(0, backoff_factor))

    async def get(self, endpoint: Optional[str] = None, **kwargs) -> Any:
        response = await self._get_raw(endpoint, **kwargs)
        return response.json()

    async def _get_raw(self, endpoint: Optional[str] = None, **kwargs) -> httpx.Response:
        return await self._request("GET", endpoint, **kwargs)

    async def post(self, endpoint: Optional[str] = None, **kwargs) -> Any:
        response = await self._post_raw(endpoint, **kwargs)
        return response.json()

    async def _post_raw(self, endpoint: Optional[str] = None, **kwargs) -> httpx.Response:
        return await self._request("POST", endpoint, **kwargs)

    async def put(self, endpoint: Optional[str] = None, **kwargs) -> Any:
        response = await self._put_raw(endpoint, **kwargs)
        return response.json()

    async def _put_raw(self, endpoint: Optional[str] = None, **kwargs) -> httpx.Response:
        return await self._request("PUT", endpoint, **kwargs)

    async def patch(self, endpoint: Optional[str] = None, **kwargs) -> Any:
        response = await self._patch_raw(endpoint, **kwargs)
        return response.json()

    async def _patch_raw(self, endpoint: Optional[str] = None, **kwargs) -> httpx.Response:
        return await self._request("PATCH", endpoint, **kwargs)

    async def delete(self, endpoint: Optional[str] = None, **kwargs) -> Any:
        response = await self._delete_raw(endpoint, **kwargs)
        return response.json()

    async def _delete_raw(self, endpoint: Optional[str] = None, **kwargs) -> httpx.Response:
        return await self._request("DELETE", endpoint, **kwargs)
