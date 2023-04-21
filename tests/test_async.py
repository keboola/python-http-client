import pytest
from unittest.mock import AsyncMock, MagicMock
from keboola.http_client.async_client import AsyncHttpClient


@pytest.mark.asyncio
async def test_post_raw_default_pars_with_none_custom_pars_passes():
    url = 'http://example.com/'
    test_def_par = {"default_par": "test"}
    cl = AsyncHttpClient(url, default_params=test_def_par)

    cl.client.request = AsyncMock()
    await cl._post_raw()

    cl.client.request.assert_called_with('POST', url, params=test_def_par, headers=None, json=None, content=None)

    await cl.client.aclose()


@pytest.mark.asyncio
async def test_post_default_pars_with_none_custom_pars_passes():
    url = 'http://example.com/'
    test_def_par = {"default_par": "test"}
    cl = AsyncHttpClient(url, default_params=test_def_par)

    cl.client.request = AsyncMock()
    await cl.post()

    cl.client.request.assert_called_with('POST', url, params=test_def_par, headers=None, json=None, content=None)

    await cl.client.aclose()


@pytest.mark.asyncio
async def test_post_raw_default_pars_with_custom_pars_passes():
    url = 'http://example.com/'
    test_def_par = {"default_par": "test"}
    cl = AsyncHttpClient(url, default_params=test_def_par)

    cust_par = {"custom_par": "custom_par_value"}
    cl.client.request = AsyncMock()
    await cl.client.post_raw(params=cust_par)

    test_cust_def_par = {**test_def_par, **cust_par}
    cl.client.request.assert_called_with('POST', url, params=test_cust_def_par, headers=None, json=None, content=None)

    await cl.client.aclose()


@pytest.mark.asyncio
async def test_post_default_pars_with_custom_pars_passes():
    url = 'http://example.com/'
    test_def_par = {"default_par": "test"}
    cl = AsyncHttpClient(url, default_params=test_def_par)

    cust_par = {"custom_par": "custom_par_value"}
    cl.client.request = AsyncMock()
    await cl.post(params=cust_par)

    test_cust_def_par = {**test_def_par, **cust_par}
    cl.client.request.assert_called_with('POST', url, params=test_cust_def_par, headers=None, json=None, content=None)

    await cl.client.aclose()


@pytest.mark.asyncio
async def test_post_raw_default_pars_with_custom_pars_to_None_passes():
    url = 'http://example.com/'
    test_def_par = {"default_par": "test"}
    cl = AsyncHttpClient(url, default_params=test_def_par)

    cust_par = None
    cl.client.request = AsyncMock()
    await cl.client.post_raw(params=cust_par)

    _cust_par_transformed = {}
    test_cust_def_par = {**test_def_par, **_cust_par_transformed}
    cl.client.request.assert_called_with('POST', url, params=test_cust_def_par, headers=None, json=None, content=None)

    await cl.client.aclose()
