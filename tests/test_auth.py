import base64
import unittest

import responses

from keboola.http_client.auth import AuthMethodBuilder, AuthBuilderError, BasicHttp
from keboola.http_client.http import HttpClient


class TestConfiguration(unittest.TestCase):

    def test_convert_private(self):
        params = {'#password': 'test'}
        new_args = AuthMethodBuilder._convert_secret_parameters(BasicHttp, **params)
        self.assertDictEqual(new_args, {'secret__password': 'test'})

    def test_invalid_method_params_fail(self):
        params = {'#password': 'test'}
        with self.assertRaises(AuthBuilderError):
            AuthMethodBuilder.build('BasicHttp', **params)

    def test_invalid_method_fail(self):
        with self.assertRaises(AuthBuilderError):
            AuthMethodBuilder.build('INVALID', **{})

    def test_valid_method_params_pass(self):
        params = {'username': "usr", '#password': 'test'}
        expected = BasicHttp(username='usr', secret__password='test')
        auth_method = AuthMethodBuilder.build('BasicHttp', **params)
        self.assertEqual(expected, auth_method)


class TestAuthorisation(unittest.TestCase):

    @responses.activate
    def test_basic_auth(self):
        auth_method = BasicHttp('user', 'password')

        client = HttpClient(base_url="http://functional/", auth_method=auth_method)
        client.login()

        # expected
        token = base64.b64encode('user:password'.encode('utf-8')).decode('utf-8')
        responses.add(
            responses.GET,
            url="http://functional/test",
            match=[responses.matchers.header_matcher({"Authorization": f"Basic {token}"})],
            json={'status': 'success'}

        )

        client.get('test')
