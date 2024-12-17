from keboola.http_client import HttpClient

BASE_URL = 'https://connection.keboola.com/v2/storage'
MAX_RETRIES = 3


class KBCStorageClient(HttpClient):

    def __init__(self, storage_token):
        HttpClient.__init__(self, base_url=BASE_URL, max_retries=MAX_RETRIES, backoff_factor=0.3,
                            status_forcelist=(429, 500, 502, 504),
                            default_http_header={"X-StorageApi-Token": storage_token})

    def get_files(self, show_expired=None):
        params = {"include": show_expired}
        return self.get('tables', params=params, timeout=5)

cl = KBCStorageClient("my_token")

print(cl.get_files())