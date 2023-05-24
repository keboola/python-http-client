import unittest
from unittest.mock import patch
import httpx
from keboola.http_client import AsyncHttpClient

class TestAsyncHttpClient(unittest.IsolatedAsyncioTestCase):
    base_url = "https://api.example.com"
    retries = 3

    async def test_get(self):
        expected_response = {"message": "Success"}
        mock_response = httpx.Response(200, json=expected_response)
        mock_response._request = httpx.Request("GET", "https://api.example.com/endpoint")

        client = AsyncHttpClient(self.base_url, retries=self.retries)

        with patch.object(httpx.AsyncClient, 'request', return_value=mock_response) as mock_request:
            response = await client.get("/endpoint")
            self.assertEqual(response, expected_response)
            mock_request.assert_called_once_with(method="GET", url="https://api.example.com/endpoint", params={},
                                                 headers={})

    async def test_post(self):
        expected_response = {"message": "Success"}
        mock_response = httpx.Response(200, json=expected_response)
        mock_response._request = httpx.Request("POST", "https://api.example.com/endpoint")

        client = AsyncHttpClient(self.base_url, retries=self.retries)

        with patch.object(httpx.AsyncClient, 'request', return_value=mock_response) as mock_request:
            response = await client.post("/endpoint", json={"data": "example"})
            self.assertEqual(response, expected_response)
            mock_request.assert_called_once_with(method="POST", url="https://api.example.com/endpoint", params={},
                                                 headers={}, json={"data": "example"})

    async def test_handle_success_response(self):
        expected_response = {"message": "Success"}
        mock_response = httpx.Response(200, json=expected_response)
        mock_response._request = httpx.Request("GET", "https://api.example.com/endpoint")

        client = AsyncHttpClient(self.base_url, retries=self.retries)

        with patch.object(httpx.AsyncClient, 'request', return_value=mock_response) as mock_request:
            response = await client.get("/endpoint")
            self.assertEqual(response, expected_response)
            mock_request.assert_called_once_with(method="GET", url="https://api.example.com/endpoint", params={},
                                                 headers={})

    async def test_handle_client_error_response(self):
        mock_response = httpx.Response(404)
        mock_response._request = httpx.Request("GET", "https://api.example.com/endpoint")

        client = AsyncHttpClient(self.base_url, retries=self.retries)

        with patch.object(httpx.AsyncClient, 'request', return_value=mock_response) as mock_request:
            with self.assertRaises(httpx.HTTPStatusError):
                await client.get("/endpoint")

            assert mock_request.call_count == self.retries + 1

            mock_request.assert_called_with(method="GET", url="https://api.example.com/endpoint", params={}, headers={})

    async def test_handle_server_error_response(self):
        mock_response = httpx.Response(500)
        mock_response._request = httpx.Request("GET", "https://api.example.com/endpoint")

        client = AsyncHttpClient(self.base_url, retries=self.retries)

        with patch.object(httpx.AsyncClient, 'request', return_value=mock_response) as mock_request:
            with self.assertRaises(httpx.HTTPStatusError):
                await client.get("/endpoint")

            assert mock_request.call_count == self.retries + 1

            mock_request.assert_called_with(method="GET", url="https://api.example.com/endpoint", params={}, headers={})

    @patch.object(httpx.AsyncClient, 'request')
    async def test_post_raw_default_pars_with_none_custom_pars_passes(self, mock_request):
        url = f"{self.base_url}/endpoint"
        test_def_par = {"default_par": "test"}

        client = AsyncHttpClient(self.base_url, retries=self.retries)

        await client.post_raw("/endpoint", params=test_def_par)

        mock_request.assert_called_once_with(method="POST", url=url, params=test_def_par, headers={})

    @patch.object(httpx.AsyncClient, 'request')
    async def test_post_default_pars_with_none_custom_pars_passes(self, mock_request):
        url = f"{self.base_url}/endpoint"
        test_def_par = {"default_par": "test"}

        client = AsyncHttpClient(self.base_url, retries=self.retries)

        await client.post("/endpoint", params=test_def_par)

        mock_request.assert_called_once_with(method="POST", url=url, params=test_def_par, headers={})

    @patch.object(httpx.AsyncClient, 'request')
    async def test_post_raw_default_pars_with_custom_pars_passes(self, mock_request):
        url = f"{self.base_url}/endpoint"
        test_def_par = {"default_par": "test"}
        cust_par = {"custom_par": "custom_par_value"}

        client = AsyncHttpClient(self.base_url, retries=self.retries, default_params=test_def_par)

        await client.post_raw("/endpoint", params=cust_par)

        test_cust_def_par = {**test_def_par, **cust_par}
        mock_request.assert_called_once_with(method="POST", url=url, params=test_cust_def_par, headers={})

    @patch.object(httpx.AsyncClient, 'request')
    async def test_post_default_pars_with_custom_pars_passes(self, mock_request):
        url = f"{self.base_url}/endpoint"
        test_def_par = {"default_par": "test"}
        cust_par = {"custom_par": "custom_par_value"}

        client = AsyncHttpClient(self.base_url, retries=self.retries, default_params=test_def_par)

        await client.post("/endpoint", params=cust_par)

        test_cust_def_par = {**test_def_par, **cust_par}
        mock_request.assert_called_once_with(method="POST", url=url, params=test_cust_def_par, headers={})

    @patch.object(httpx.AsyncClient, 'request')
    async def test_post_raw_default_pars_with_custom_pars_to_None_passes(self, mock_request):
        url = f"{self.base_url}/endpoint"
        test_def_par = {"default_par": "test"}
        cust_par = None

        client = AsyncHttpClient(self.base_url, retries=self.retries, default_params=test_def_par)

        await client.post_raw("/endpoint", params=cust_par)

        # post_raw changes None to empty dict
        _cust_par_transformed = {}
        test_cust_def_par = {**test_def_par, **_cust_par_transformed}
        mock_request.assert_called_once_with(method="POST", url=url, params=test_cust_def_par, headers={})

    @patch.object(httpx.AsyncClient, 'request')
    async def test_post_default_pars_with_custom_pars_to_None_passes(self, mock_request):
        url = f"{self.base_url}/endpoint"
        test_def_par = {"default_par": "test"}
        cust_par = None

        client = AsyncHttpClient(self.base_url, retries=self.retries, default_params=test_def_par)

        await client.post("/endpoint", params=cust_par)

        # post_raw changes None to empty dict
        _cust_par_transformed = {}
        test_cust_def_par = {**test_def_par, **_cust_par_transformed}
        mock_request.assert_called_once_with(method="POST", url=url, params=test_cust_def_par, headers={})

    @patch.object(httpx.AsyncClient, 'request')
    async def test_all_methods_requests_raw_with_custom_pars_passes(self, mock_request):
        client = AsyncHttpClient(self.base_url, retries=self.retries)

        cust_par = {"custom_par": "custom_par_value"}

        for met in ['GET', 'POST', 'PATCH', 'UPDATE', 'PUT']:
            await client._request(met, ignore_auth=False, params=cust_par)
            mock_request.assert_called_with(method=met, url=self.base_url, params=cust_par, headers={})


if __name__ == "__main__":
    unittest.main()
