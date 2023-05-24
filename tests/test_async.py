import unittest
from unittest.mock import patch
import httpx
from keboola.http_client import AsyncHttpClient

class TestAsyncHttpClient(unittest.IsolatedAsyncioTestCase):
    base_url = "https://api.example.com"

    def setUp(self):
        self.client = AsyncHttpClient(self.base_url)

    async def tearDown(self):
        await self.client.close()

    async def test_get(self):
        expected_response = {"message": "Success"}
        mock_response = httpx.Response(200, json=expected_response)
        mock_response._request = httpx.Request("GET", "https://api.example.com/endpoint")

        with patch.object(httpx.AsyncClient, 'request', return_value=mock_response) as mock_request:
            response = await self.client.get("/endpoint")
            self.assertEqual(response, expected_response)
            mock_request.assert_called_once_with("GET", "https://api.example.com/endpoint", params={}, headers={}, json=None)

    async def test_post(self):
        expected_response = {"message": "Success"}
        mock_response = httpx.Response(200, json=expected_response)
        mock_response._request = httpx.Request("POST", "https://api.example.com/endpoint")

        with patch.object(httpx.AsyncClient, 'request', return_value=mock_response) as mock_request:
            response = await self.client.post("/endpoint", json={"data": "example"})
            self.assertEqual(response, expected_response)
            mock_request.assert_called_once_with("POST", "https://api.example.com/endpoint", params={}, headers={}, json={"data": "example"})

    async def test_handle_success_response(self):
        expected_response = {"message": "Success"}
        mock_response = httpx.Response(200, json=expected_response)
        mock_response._request = httpx.Request("GET", "https://api.example.com/endpoint")

        with patch.object(httpx.AsyncClient, 'request', return_value=mock_response) as mock_request:
            response = await self.client.get("/endpoint")
            self.assertEqual(response, expected_response)
            mock_request.assert_called_once_with("GET", "https://api.example.com/endpoint", params={}, headers={}, json=None)

    async def test_handle_client_error_response(self):
        mock_response = httpx.Response(404)
        mock_response._request = httpx.Request("GET", "https://api.example.com/endpoint")

        with patch.object(httpx.AsyncClient, 'request', return_value=mock_response) as mock_request:
            with self.assertRaises(httpx.HTTPStatusError):
                await self.client.get("/endpoint")
            mock_request.assert_called_with("GET", "https://api.example.com/endpoint", params={}, headers={}, json=None)

    async def test_handle_server_error_response(self):
        mock_response = httpx.Response(500)
        mock_response._request = httpx.Request("GET", "https://api.example.com/endpoint")

        with patch.object(httpx.AsyncClient, 'request', return_value=mock_response) as mock_request:
            with self.assertRaises(httpx.HTTPStatusError):
                await self.client.get("/endpoint")
            mock_request.assert_called_with("GET", "https://api.example.com/endpoint", params={}, headers={}, json=None)

    @patch.object(httpx.AsyncClient, 'request')
    async def test_post_raw_default_pars_with_none_custom_pars_passes(self, mock_request):
        url = f"{self.base_url}/endpoint"
        test_def_par = {"default_par": "test"}

        await self.client.post_raw("/endpoint", params=test_def_par)

        mock_request.assert_called_once_with(
            "POST",
            url,
            params=test_def_par,
            headers={},
            json=None
        )



if __name__ == "__main__":
    unittest.main()
