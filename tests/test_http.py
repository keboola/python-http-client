import unittest
from urllib.parse import urlparse, urljoin
from unittest.mock import patch

import keboola.http_client.http as client


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

        cl._requests_retry_session().close()

    @patch.object(client.HttpClient, '_request_raw')
    def test_all_methods_skip_auth(self, mock_post):
        url = 'http://example.com/'
        cl = client.HttpClient(url, auth_header={"authorization": "xxx"})

        for m in ['POST', 'PATCH', 'UPDATE', 'PUT', 'DELETE']:
            method_to_call = getattr(cl, m.lower())
            method_to_call(ignore_auth=True, is_absolute_path=False)
            mock_post.assert_called_with(m, None, ignore_auth=True, params=None, headers=None,
                                         is_absolute_path=False, cookies=None, data=None, files=None, json=None)

        for m in ['GET']:
            method_to_call = getattr(cl, m.lower())
            method_to_call(ignore_auth=True, is_absolute_path=False)
            mock_post.assert_called_with(m, None, ignore_auth=True, params=None, headers=None,
                                         is_absolute_path=False, cookies=None)

    def test_request_skip_auth_header(self):
        cl = client.HttpClient('http://example.com', default_http_header={"defheader": "test"},
                               auth_header={"Authorization": "test"})
        res = cl._request_raw('POST', 'abc', ignore_auth=True)
        cl._requests_retry_session().close()
        self.assertEqual(res.request.url, 'http://example.com/abc')
        self.assertEqual(res.request.headers.get('defheader'), 'test')
        self.assertEqual(res.request.headers.get('Authorization'), None)

    def test_all_methods_raw(self):
        url = 'http://example.com'
        cl = client.HttpClient(url, default_http_header={'header1': 'headerval'},
                               auth_header={'api_token': 'abdc1234'})

        TARGET_URL = 'http://example.com/storage?exclude=componentDetails'

        for m in ['GET', 'POST']:
            method_to_call = getattr(cl, m.lower() + '_raw')
            res = method_to_call('storage', params={'exclude': 'componentDetails'},
                                 headers={'abc': '123'}, data={'attr1': 'val1'})
            self.assertEqual(res.request.url, TARGET_URL)
            self.assertEqual(res.request.headers.get('api_token'), 'abdc1234')
            self.assertEqual(res.request.headers.get('abc'), '123')
            self.assertEqual(res.request.headers.get('header1'), 'headerval')
            self.assertEqual(res.request.body, 'attr1=val1')

        cl._requests_retry_session().close()

    @patch.object(client.requests.Session, 'request')
    def test_all_methods_requests_raw_with_is_absolute_path_true(self, mock_request):
        url = 'http://example.com/'
        cl = client.HttpClient(url)

        for met in client.ALLOWED_METHODS:
            cl._request_raw(met, 'http://example2.com/v1/', ignore_auth=False, is_absolute_path=True)
            mock_request.assert_called_with(met, 'http://example2.com/v1/', params={})

        cl._requests_retry_session().close()

    @patch.object(client.requests.Session, 'request')
    def test_all_methods_requests_raw_with_is_absolute_path_false(self, mock_request):
        url = 'http://example.com/api/v1'
        cl = client.HttpClient(url)

        for met in ['GET', 'POST', 'PATCH', 'UPDATE', 'PUT']:
            cl._request_raw(met, 'events', ignore_auth=False, is_absolute_path=False)
            mock_request.assert_called_with(met, 'http://example.com/api/v1/events', params={})

        cl._requests_retry_session().close()

    @patch.object(client.requests.Session, 'request')
    def test_all_methods_kwargs(self, mock_request):
        url = 'http://example.com/api/v1'
        cl = client.HttpClient(url)

        for met in ['GET', 'POST', 'PATCH', 'UPDATE', 'PUT']:
            method_to_call = getattr(cl, met.lower())
            method_to_call(params={'par1': 'val1'}, verify=False, data={'data': '123'},
                           files={'a': '/path/to/file'}, cert='/path/to/cert', json=None)
            mock_request.assert_called_with(met, 'http://example.com/api/v1/', verify=False, data={'data': '123'},
                                            files={'a': '/path/to/file'}, cookies=None, cert='/path/to/cert',
                                            params={'par1': 'val1'}, json=None)

        cl._requests_retry_session().close()

    def test_update_auth_header_None(self):
        existing_header = None
        new_header = {'api_token': 'token_value'}

        cl = client.HttpClient('https://example.com', auth_header=existing_header)
        cl.update_auth_header(new_header, overwrite=False)
        self.assertDictEqual(cl._auth_header, new_header)

        new_header_2 = {'password': '123'}
        cl.update_auth_header(new_header_2, overwrite=True)
        self.assertDictEqual(cl._auth_header, new_header_2)

    def test_update_existing_auth_header(self):
        existing_header = {'authorization': 'value'}
        new_header = {'api_token': 'token_value'}

        cl = client.HttpClient('https://example.com', auth_header=existing_header)
        cl.update_auth_header(new_header, overwrite=False)
        self.assertDictEqual(cl._auth_header, {**existing_header, **new_header})

    def test_build_url_rel_path(self):
        url = 'https://example.com/'
        cl = client.HttpClient(url)
        self.assertEqual(urljoin(url, 'storage'), cl._build_url('storage'))

    def test_build_url_abs_path(self):
        url = 'https://example.com/'
        cl = client.HttpClient(url)
        self.assertEqual('https://example2.com/storage', cl._build_url('https://example2.com/storage', True))

    def test_build_url_empty_endpoint_path_leads_to_base_url(self):
        url = 'https://example.com/'
        cl = client.HttpClient(url)
        self.assertEqual(url, cl._build_url())
        self.assertEqual(url, cl._build_url(''))
        self.assertEqual(url, cl._build_url(None))
        self.assertEqual(url, cl._build_url('', True))
        self.assertEqual(url, cl._build_url(None, True))

    def test_build_url_base_url_appends_slash(self):
        url = 'https://example.com'
        cl = client.HttpClient(url)
        self.assertEqual('https://example.com/', cl.base_url)

    def test_build_url_with_spaces(self):
        base_url = "http://example.com/"
        cl = client.HttpClient(base_url)

        result = cl._build_url("path/with spaces")
        expected_path = "path/with%20spaces"
        parsed = urlparse(result)
        self.assertEqual(parsed.path, f"/{expected_path}")
        self.assertEqual(parsed.netloc, "example.com")
        self.assertEqual(parsed.scheme, "http")

        result = cl._build_url("path?param=space test")
        expected_query = "param=space test"
        parsed = urlparse(result)
        self.assertEqual(parsed.query, expected_query)
        self.assertEqual(parsed.path, "/path")
        self.assertEqual(parsed.netloc, "example.com")
        self.assertEqual(parsed.scheme, "http")

        absolute_result = cl._build_url("http://example.com/absolute path", is_absolute_path=True)
        expected_absolute = "http://example.com/absolute path"
        self.assertEqual(absolute_result, expected_absolute)
