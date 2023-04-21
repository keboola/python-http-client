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
            user_agent: Optional[str] = None,
    ):
        """
        Initialize the AsyncHttpClientV2 instance.

        Args:
            base_url (str): The base URL for the API.
            retries (int, optional): The maximum number of retries for failed requests. Defaults to 3.
            timeout (Optional[float], optional): The request timeout in seconds. Defaults to None.
            verify_ssl (bool, optional): Enable or disable SSL verification. Defaults to True.
            retry_status_codes (Optional[List[int]], optional): List of status codes to retry on. Defaults to None.
            rate_limit (Optional[int], optional): Maximum number of concurrent requests. Defaults to None.
            default_params (Optional[Dict[str, str]], optional): Default query parameters for each request.
            Defaults to None.
            auth_header (Optional[Dict[str, str]], optional): Authentication header for each request. Defaults to None.
            user_agent (Optional[str], optional): Custom user-agent string for each request. Defaults to None.
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
        self.client = httpx.AsyncClient(timeout=self.timeout, verify=self.verify_ssl,
                                        headers={"User-Agent": user_agent} if user_agent else None)

    async def __aenter__(self):
        await self.client.__aenter__()
        return self

    async def __aexit__(self, *args):
        await self.client.__aexit__(*args)

    async def _request(
            self,
            method: str,
            endpoint: Optional[str] = None,
            params: Optional[Dict[str, str]] = None,
            headers: Optional[Dict[str, str]] = None,
            json: Optional[Dict[str, Any]] = None,
    ) -> httpx.Response:
        url = urljoin(self.base_url, endpoint or "")
        all_params = {**self.default_params, **(params or {})}
        all_headers = {**self.auth_header, **(headers or {})}

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
                await asyncio.sleep(2 ** retry_attempt)

    async def get(self, endpoint: Optional[str] = None, **kwargs) -> Any:
        response = await self._get_raw(endpoint, **kwargs)
        response.raise_for_status()
        return response.json()

    async def _get_raw(self, endpoint: Optional[str] = None, **kwargs) -> httpx.Response:
        return await self._request("GET", endpoint, **kwargs)

    async def post(self, endpoint: Optional[str] = None, **kwargs) -> Any:
        response = await self._post_raw(endpoint, **kwargs)
        response.raise_for_status()
        return response.json()

    async def _post_raw(self, endpoint: Optional[str] = None, **kwargs) -> httpx.Response:
        return await self._request("POST", endpoint, **kwargs)

    async def put(self, endpoint: Optional[str] = None, **kwargs) -> Any:
        response = await self._put_raw(endpoint, **kwargs)
        response.raise_for_status()
        return response.json()

    async def _put_raw(self, endpoint: Optional[str] = None, **kwargs) -> httpx.Response:
        return await self._request("PUT", endpoint, **kwargs)

    async def patch(self, endpoint: Optional[str] = None, **kwargs) -> Any:
        response = await self._patch_raw(endpoint, **kwargs)
        response.raise_for_status()
        return response.json()

    async def _patch_raw(self, endpoint: Optional[str] = None, **kwargs) -> httpx.Response:
        return await self._request("PATCH", endpoint, **kwargs)

    async def delete(self, endpoint: Optional[str] = None, **kwargs) -> Any:
        response = await self._delete_raw(endpoint, **kwargs)
        response.raise_for_status()
        return response.json()

    async def _delete_raw(self, endpoint: Optional[str] = None, **kwargs) -> httpx.Response:
        return await self._request("DELETE", endpoint, **kwargs)