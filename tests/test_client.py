import requests
import unittest
from unittest.mock import patch

import src.keboola.client as client


class TestClientBase(unittest.TestCase):

    @patch.object(requests.Session, 'request')
    def test_post_raw_default_pars_with_none_custom_pars_passes(self, mock_post):
        test_def_par = {"default_par": "test"}
        cl = client.HttpClientBase('http://example.com', default_params=test_def_par)

        # post raw
        cl.post_raw()
        mock_post.assert_called_with('POST', params=test_def_par)

    @patch.object(requests.Session, 'request')
    def test_post_default_pars_with_none_custom_pars_passes(self, mock_post):
        test_def_par = {"default_par": "test"}
        cl = client.HttpClientBase('http://example.com', default_params=test_def_par)

        # post
        cl.post()
        mock_post.assert_called_with('POST', params=test_def_par)

    @patch.object(requests.Session, 'request')
    def test_post_raw_default_pars_with_custom_pars_passes(self, mock_post):
        test_def_par = {"default_par": "test"}
        cl = client.HttpClientBase('http://example.com', default_params=test_def_par)

        # post_raw
        cust_par = {"custom_par": "custom_par_value"}
        cl.post_raw(params=cust_par)

        test_cust_def_par = {**test_def_par, **cust_par}
        mock_post.assert_called_with('POST', params=test_cust_def_par)

    @patch.object(requests.Session, 'request')
    def test_post_default_pars_with_custom_pars_passes(self, mock_post):
        test_def_par = {"default_par": "test"}
        cl = client.HttpClientBase('http://example.com', default_params=test_def_par)

        # post
        cust_par = {"custom_par": "custom_par_value"}
        cl.post(params=cust_par)

        test_cust_def_par = {**test_def_par, **cust_par}
        mock_post.assert_called_with('POST', params=test_cust_def_par)

    @patch.object(requests.Session, 'request')
    def test_post_raw_default_pars_with_custom_pars_to_None_passes(self, mock_post):
        test_def_par = {"default_par": "test"}
        cl = client.HttpClientBase('http://example.com', default_params=test_def_par)

        # post_raw
        cust_par = None
        cl.post_raw(params=cust_par)

        # post_raw changes None to empty dict
        _cust_par_transformed = {}
        test_cust_def_par = {**test_def_par, **_cust_par_transformed}
        mock_post.assert_called_with('POST', params=test_cust_def_par)

    @patch.object(requests.Session, 'request')
    def test_post_default_pars_with_custom_pars_to_None_passes(self, mock_post):
        test_def_par = {"default_par": "test"}
        cl = client.HttpClientBase('http://example.com', default_params=test_def_par)

        # post_raw
        cust_par = None
        cl.post(params=cust_par)

        # post_raw changes None to empty dict
        _cust_par_transformed = {}
        test_cust_def_par = {**test_def_par, **_cust_par_transformed}
        mock_post.assert_called_with('POST', params=test_cust_def_par)

    @patch.object(requests.Session, 'request')
    def test_post_raw_with_custom_pars_passes(self, mock_post):
        cl = client.HttpClientBase('http://example.com')

        # post_raw
        cust_par = {"custom_par": "custom_par_value"}
        cl.post_raw(params=cust_par)

        mock_post.assert_called_with('POST', params=cust_par)

    @patch.object(requests.Session, 'request')
    def test_post_with_custom_pars_passes(self, mock_post):
        cl = client.HttpClientBase('http://example.com')

        # post_raw
        cust_par = {"custom_par": "custom_par_value"}
        cl.post(params=cust_par)

        mock_post.assert_called_with('POST', params=cust_par)

    @patch.object(requests.Session, 'request')
    def test_all_methods_requests_raw_with_custom_pars_passes(self, mock_request):
        cl = client.HttpClientBase('http://example.com')

        # post_raw
        cust_par = {"custom_par": "custom_par_value"}

        for met in ['GET', 'POST', 'PATCH', 'UPDATE', 'PUT']:
            cl._request_raw(method=met, ignore_auth=False, params=cust_par)
            mock_request.assert_called_with(met, params=cust_par)

        cl.requests_retry_session().close()

    @patch.object(client.HttpClientBase, '_request_raw')
    def test_all_methods_skip_auth(self, mock_post):
        cl = client.HttpClientBase('http://example.com')

        for m in ['GET', 'POST', 'PATCH', 'UPDATE', 'PUT', 'DELETE']:
            method_to_call = getattr(cl, m.lower())
            method_to_call(url=cl.base_url, ignore_auth=True)
            mock_post.assert_called_with(m, ignore_auth=True, url='http://example.com')

    def test_request_skip_auth_header(self):
        cl = client.HttpClientBase('http://example.com', default_http_header={"defheader": "test"},
                                   auth_header={"Authorization": "test"})
        res = cl._request_raw(url=cl.base_url, method='POST', ignore_auth=True)
        cl.requests_retry_session().close()
        self.assertEqual(res.request.headers.get('defheader'), 'test')


if __name__ == '__main__':
    unittest.main()
