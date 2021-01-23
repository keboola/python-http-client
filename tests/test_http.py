import unittest
from unittest.mock import patch
import keboola.client.http as client


class TestClientBase(unittest.TestCase):

    @patch.object(client.requests.Session, 'request')
    def test_post_raw_default_pars_with_none_custom_pars_passes(self, mock_post):
        url = 'http://example.com/'
        test_def_par = {"default_par": "test"}
        cl = client.HttpClient(url, default_params=test_def_par)

        # post raw
        cl.post_raw()
        mock_post.assert_called_with('POST', url, params=test_def_par, cookies=None, data=None, json=None, files=None)

    @patch.object(client.requests.Session, 'request')
    def test_post_default_pars_with_none_custom_pars_passes(self, mock_post):
        url = 'http://example.com/'
        test_def_par = {"default_par": "test"}
        cl = client.HttpClient(url, default_params=test_def_par)

        # post
        cl.post()
        mock_post.assert_called_with('POST', url, params=test_def_par, cookies=None, data=None, json=None, files=None)

    @patch.object(client.requests.Session, 'request')
    def test_post_raw_default_pars_with_custom_pars_passes(self, mock_post):
        url = 'http://example.com/'
        test_def_par = {"default_par": "test"}
        cl = client.HttpClient(url, default_params=test_def_par)

        # post_raw
        cust_par = {"custom_par": "custom_par_value"}
        cl.post_raw(params=cust_par)

        test_cust_def_par = {**test_def_par, **cust_par}
        mock_post.assert_called_with('POST', url, params=test_cust_def_par, cookies=None,
                                     data=None, json=None, files=None)

    @patch.object(client.requests.Session, 'request')
    def test_post_default_pars_with_custom_pars_passes(self, mock_post):
        url = 'http://example.com/'
        test_def_par = {"default_par": "test"}
        cl = client.HttpClient(url, default_params=test_def_par)

        # post
        cust_par = {"custom_par": "custom_par_value"}
        cl.post(params=cust_par)

        test_cust_def_par = {**test_def_par, **cust_par}
        mock_post.assert_called_with('POST', url, params=test_cust_def_par, cookies=None,
                                     data=None, json=None, files=None)

    @patch.object(client.requests.Session, 'request')
    def test_post_raw_default_pars_with_custom_pars_to_None_passes(self, mock_post):
        url = 'http://example.com/'
        test_def_par = {"default_par": "test"}
        cl = client.HttpClient(url, default_params=test_def_par)

        # post_raw
        cust_par = None
        cl.post_raw(params=cust_par)

        # post_raw changes None to empty dict
        _cust_par_transformed = {}
        test_cust_def_par = {**test_def_par, **_cust_par_transformed}
        mock_post.assert_called_with('POST', url, params=test_cust_def_par, cookies=None,
                                     data=None, json=None, files=None)

    @patch.object(client.requests.Session, 'request')
    def test_post_default_pars_with_custom_pars_to_None_passes(self, mock_post):
        url = 'http://example.com/'
        test_def_par = {"default_par": "test"}
        cl = client.HttpClient(url, default_params=test_def_par)

        # post_raw
        cust_par = None
        cl.post(params=cust_par)

        # post_raw changes None to empty dict
        _cust_par_transformed = {}
        test_cust_def_par = {**test_def_par, **_cust_par_transformed}
        mock_post.assert_called_with('POST', url, params=test_cust_def_par, cookies=None,
                                     data=None, json=None, files=None)

    @patch.object(client.requests.Session, 'request')
    def test_post_raw_with_custom_pars_passes(self, mock_post):
        url = 'http://example.com/'
        cl = client.HttpClient(url)

        # post_raw
        cust_par = {"custom_par": "custom_par_value"}
        cl.post_raw(params=cust_par)

        mock_post.assert_called_with('POST', url, params=cust_par, cookies=None, data=None, json=None, files=None)

    @patch.object(client.requests.Session, 'request')
    def test_post_with_custom_pars_passes(self, mock_post):
        url = 'http://example.com/'
        cl = client.HttpClient(url)

        # post_raw
        cust_par = {"custom_par": "custom_par_value"}
        cl.post(params=cust_par)

        mock_post.assert_called_with('POST', url, params=cust_par, cookies=None, data=None, json=None, files=None)

    @patch.object(client.requests.Session, 'request')
    def test_all_methods_requests_raw_with_custom_pars_passes(self, mock_request):
        url = 'http://example.com/'
        cl = client.HttpClient(url)

        # post_raw
        cust_par = {"custom_par": "custom_par_value"}

        for met in ['GET', 'POST', 'PATCH', 'UPDATE', 'PUT']:
            cl._request_raw(met, ignore_auth=False, params=cust_par)
            mock_request.assert_called_with(met, url, params=cust_par)

        cl.requests_retry_session().close()

    @patch.object(client.HttpClient, '_request_raw')
    def test_all_methods_skip_auth(self, mock_post):
        url = 'http://example.com/'
        cl = client.HttpClient(url)

        for m in ['POST', 'PATCH', 'UPDATE', 'PUT', 'DELETE']:
            method_to_call = getattr(cl, m.lower())
            method_to_call(ignore_auth=True, is_absolute_path=False)
            mock_post.assert_called_with(m, ignore_auth=True, params=None, headers=None,
                                         is_absolute_path=False, cookies=None, data=None, files=None, json=None)

        for m in ['GET']:
            method_to_call = getattr(cl, m.lower())
            method_to_call(ignore_auth=True, is_absolute_path=False)
            mock_post.assert_called_with(m, ignore_auth=True, params=None, headers=None,
                                         is_absolute_path=False, cookies=None)

    def test_request_skip_auth_header(self):
        cl = client.HttpClient('http://example.com', default_http_header={"defheader": "test"},
                               auth_header={"Authorization": "test"})
        res = cl._request_raw('POST', 'abc', ignore_auth=True)
        cl.requests_retry_session().close()
        self.assertEqual(res.request.url, 'http://example.com/abc')
        self.assertEqual(res.request.headers.get('defheader'), 'test')
        self.assertEqual(res.request.headers.get('Authorization'), None)

    def test_all_methods_raw(self):
        sapi_index = 'https://connection.keboola.com/v2/'
        cl = client.HttpClient(sapi_index, default_http_header={'api_token': 'abdc1234'})

        TARGET_URL = 'https://connection.keboola.com/v2/storage?exclude=componentDetails'

        for m in ['GET', 'POST', 'PATCH', 'UPDATE', 'PUT', 'DELETE']:
            method_to_call = getattr(cl, m.lower() + '_raw')
            res = method_to_call('storage', params={'exclude': 'componentDetails'}, headers={'abc': '123'})
            self.assertEqual(res.request.url, TARGET_URL)
            self.assertEqual(res.request.headers.get('api_token'), 'abdc1234')
            self.assertEqual(res.request.headers.get('abc'), '123')

        cl.requests_retry_session().close()

    @patch.object(client.requests.Session, 'request')
    def test_all_methods_requests_raw_with_is_absolute_path_true(self, mock_request):
        url = 'http://example.com/'
        cl = client.HttpClient(url)

        for met in ['GET', 'POST', 'PATCH', 'UPDATE', 'PUT']:
            cl._request_raw(met, 'http://example2.com/v1/', ignore_auth=False, is_absolute_path=True)
            mock_request.assert_called_with(met, 'http://example2.com/v1/')

        cl.requests_retry_session().close()

    @patch.object(client.requests.Session, 'request')
    def test_all_methods_requests_raw_with_is_absolute_path_false(self, mock_request):
        url = 'http://example.com/api/v1'
        cl = client.HttpClient(url)

        for met in ['GET', 'POST', 'PATCH', 'UPDATE', 'PUT']:
            cl._request_raw(met, 'events', ignore_auth=False, is_absolute_path=False)
            mock_request.assert_called_with(met, 'http://example.com/api/v1/events')

        cl.requests_retry_session().close()
