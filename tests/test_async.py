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
            mock_request.assert_called_once_with("GET", url="https://api.example.com/endpoint")

    async def test_post(self):
        expected_response = {"message": "Success"}
        mock_response = httpx.Response(200, json=expected_response)
        mock_response._request = httpx.Request("POST", "https://api.example.com/endpoint")

        client = AsyncHttpClient(self.base_url, retries=self.retries)

        with patch.object(httpx.AsyncClient, 'request', return_value=mock_response) as mock_request:
            response = await client.post("/endpoint", json={"data": "example"})
            self.assertEqual(response, expected_response)
            mock_request.assert_called_once_with("POST", url="https://api.example.com/endpoint",
                                                 json={"data": "example"})

    async def test_handle_success_response(self):
        expected_response = {"message": "Success"}
        mock_response = httpx.Response(200, json=expected_response)
        mock_response._request = httpx.Request("GET", "https://api.example.com/endpoint")

        client = AsyncHttpClient(self.base_url, retries=self.retries)

        with patch.object(httpx.AsyncClient, 'request', return_value=mock_response) as mock_request:
            response = await client.get("/endpoint")
            self.assertEqual(response, expected_response)
            mock_request.assert_called_once_with("GET", url="https://api.example.com/endpoint")

    async def test_handle_client_error_response(self):
        mock_response = httpx.Response(404)
        mock_response._request = httpx.Request("GET", "https://api.example.com/endpoint")

        client = AsyncHttpClient(self.base_url, retries=self.retries)

        with patch.object(httpx.AsyncClient, 'request', return_value=mock_response) as mock_request:
            with self.assertRaises(httpx.HTTPStatusError):
                await client.get("/endpoint")

            assert mock_request.call_count == self.retries + 1

            mock_request.assert_called_with("GET", url="https://api.example.com/endpoint")

    async def test_handle_server_error_response(self):
        mock_response = httpx.Response(500)
        mock_response._request = httpx.Request("GET", "https://api.example.com/endpoint")

        client = AsyncHttpClient(self.base_url, retries=self.retries)

        with patch.object(httpx.AsyncClient, 'request', return_value=mock_response) as mock_request:
            with self.assertRaises(httpx.HTTPStatusError):
                await client.get("/endpoint")

            assert mock_request.call_count == self.retries + 1

            mock_request.assert_called_with("GET", url="https://api.example.com/endpoint")

    @patch.object(httpx.AsyncClient, 'request')
    async def test_post_raw_default_pars_with_none_custom_pars_passes(self, mock_request):
        url = f"{self.base_url}/endpoint"
        test_def_par = {"default_par": "test"}

        client = AsyncHttpClient(self.base_url, retries=self.retries)

        await client.post_raw("/endpoint", params=test_def_par)

        mock_request.assert_called_once_with("POST", url=url, params=test_def_par)

    @patch.object(httpx.AsyncClient, 'request')
    async def test_post_default_pars_with_none_custom_pars_passes(self, mock_request):
        url = f"{self.base_url}/endpoint"
        test_def_par = {"default_par": "test"}

        client = AsyncHttpClient(self.base_url, retries=self.retries)

        await client.post("/endpoint", params=test_def_par)

        mock_request.assert_called_once_with("POST", url=url, params=test_def_par)

    @patch.object(httpx.AsyncClient, 'request')
    async def test_post_raw_default_pars_with_custom_pars_passes(self, mock_request):
        url = f"{self.base_url}/endpoint"
        test_def_par = {"default_par": "test"}
        cust_par = {"custom_par": "custom_par_value"}

        client = AsyncHttpClient(self.base_url, retries=self.retries, default_params=test_def_par)

        await client.post_raw("/endpoint", params=cust_par)

        test_cust_def_par = {**test_def_par, **cust_par}
        mock_request.assert_called_once_with("POST", url=url, params=test_cust_def_par)

    @patch.object(httpx.AsyncClient, 'request')
    async def test_post_default_pars_with_custom_pars_passes(self, mock_request):
        url = f"{self.base_url}/endpoint"
        test_def_par = {"default_par": "test"}
        cust_par = {"custom_par": "custom_par_value"}

        client = AsyncHttpClient(self.base_url, retries=self.retries, default_params=test_def_par)

        await client.post("/endpoint", params=cust_par)

        test_cust_def_par = {**test_def_par, **cust_par}
        mock_request.assert_called_once_with("POST", url=url, params=test_cust_def_par)

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
        mock_request.assert_called_once_with("POST", url=url, params=test_cust_def_par)

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
        mock_request.assert_called_once_with("POST", url=url, params=test_cust_def_par)

    @patch.object(httpx.AsyncClient, 'request')
    async def test_all_methods_requests_raw_with_custom_pars_passes(self, mock_request):
        client = AsyncHttpClient(self.base_url)

        cust_par = {"custom_par": "custom_par_value"}

        for m in client.ALLOWED_METHODS:
            await client._request(m, ignore_auth=False, params=cust_par)
            mock_request.assert_called_with(m, url=self.base_url+"/", params=cust_par)

    @patch.object(httpx.AsyncClient, 'request')
    async def test_all_methods_skip_auth(self, mock_request):
        client = AsyncHttpClient(self.base_url, auth=("my_user", "password123"))

        for m in ['GET', 'POST', 'PATCH', 'UPDATE', 'PUT', 'DELETE']:
            await client._request(m, ignore_auth=True)
            mock_request.assert_called_with(m, url=self.base_url+"/")

    @patch.object(httpx.AsyncClient, 'request')
    async def test_request_skip_auth_header(self, mock_request):
        def_header = {"def_header": "test"}
        client = AsyncHttpClient('http://example.com', default_headers=def_header,
                               auth_header={"Authorization": "test"})

        await client._request('POST', 'abc', ignore_auth=True)
        mock_request.assert_called_with('POST', url="http://example.com/abc", headers=def_header)

    @patch.object(httpx.AsyncClient, 'request')
    async def test_request_auth(self, mock_request):
        def_header = {"def_header": "test"}
        auth = ("my_user", "password123")
        client = AsyncHttpClient(self.base_url, auth=auth, default_headers=def_header)

        await client._request('POST', 'abc')
        mock_request.assert_called_with('POST', url=self.base_url+"/abc", headers=def_header,
                                        auth=auth)

    @patch.object(httpx.AsyncClient, 'request')
    async def test_all_methods(self, mock_request):
        client = AsyncHttpClient(self.base_url, default_headers={'header1': 'headerval'},
                                auth_header={'api_token': 'abdc1234'})

        target_url = f'{self.base_url}/abc'

        for m in client.ALLOWED_METHODS:
            await client._request(m, 'abc', params={'exclude': 'componentDetails'}, headers={'abc': '123'},
                                  data={'attr1': 'val1'})
            mock_request.assert_called_with(m, url=target_url,
                                            params={'exclude': 'componentDetails'},
                                            headers={'api_token': 'abdc1234', 'header1': 'headerval', 'abc': '123'},
                                            data={'attr1': 'val1'})

    @patch.object(httpx.AsyncClient, 'request')
    async def test_all_methods_requests_raw_with_is_absolute_path_true(self, mock_request):
        def_header = {"def_header": "test"}
        client = AsyncHttpClient(self.base_url, default_headers=def_header)

        for m in client.ALLOWED_METHODS:
            await client._request(m, 'http://example2.com/v1/', is_absolute_path=True)
            mock_request.assert_called_with(m, url='http://example2.com/v1/', headers=def_header)

    @patch.object(httpx.AsyncClient, 'request')
    async def test_all_methods_requests_raw_with_is_absolute_path_false(self, mock_request):
        def_header = {"def_header": "test"}
        client = AsyncHttpClient(self.base_url, default_headers=def_header)

        for m in client.ALLOWED_METHODS:
            await client._request(m, 'cars')
            mock_request.assert_called_with(m, url=self.base_url+"/cars", headers=def_header)

    @patch.object(httpx.AsyncClient, 'request')
    async def test_all_methods_kwargs(self, mock_request):
        client = AsyncHttpClient(self.base_url)

        for m in client.ALLOWED_METHODS:
            await client._request(m, 'cars', data={'data': '123'}, cert='/path/to/cert', files={'a': '/path/to/file'},
                                            params={'par1': 'val1'})

            mock_request.assert_called_with(m, url=self.base_url+"/cars", data={'data': '123'},
                                            cert='/path/to/cert', files={'a': '/path/to/file'},
                                            params={'par1': 'val1'})

    async def test_build_url_rel_path(self):
        url = 'https://example.com/'
        cl = AsyncHttpClient(url)
        expected_url = 'https://example.com/storage'
        actual_url = await cl._build_url('storage')
        self.assertEqual(expected_url, actual_url)

    async def test_build_url_abs_path(self):
        url = 'https://example.com/'
        cl = AsyncHttpClient(url)
        expected_url = 'https://example2.com/storage'
        actual_url = await cl._build_url('https://example2.com/storage', True)
        self.assertEqual(expected_url, actual_url)

    async def test_build_url_empty_endpoint_path_leads_to_base_url(self):
        url = 'https://example.com/'
        cl = AsyncHttpClient(url)
        expected_url = url

        actual_url = await cl._build_url()
        self.assertEqual(expected_url, actual_url)

        actual_url = await cl._build_url('')
        self.assertEqual(expected_url, actual_url)

        actual_url = await cl._build_url(None)
        self.assertEqual(expected_url, actual_url)

        actual_url = await cl._build_url('', is_absolute_path=True)
        self.assertEqual(expected_url, actual_url)

        actual_url = await cl._build_url(None, is_absolute_path=True)
        self.assertEqual(expected_url, actual_url)

    async def test_build_url_base_url_appends_slash(self):
        url = 'https://example.com'
        cl = AsyncHttpClient(url)
        expected_base_url = 'https://example.com/'

        self.assertEqual(expected_base_url, cl.base_url)


if __name__ == "__main__":
    unittest.main()
