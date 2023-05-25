import asyncio
from keboola.http_client import AsyncHttpClient

BASE_URL = 'https://connection.keboola.com/v2/storage'
MAX_RETRIES = 3

class KBCStorageClient(AsyncHttpClient):

    def __init__(self, storage_token):
        AsyncHttpClient.__init__(
            self,
            base_url=BASE_URL,
            retries=MAX_RETRIES,
            backoff_factor=0.3,
            retry_status_codes=[429, 500, 502, 504],
            auth_header={"X-StorageApi-Token": storage_token}
        )

    async def get_files(self, show_expired=False):
        params = {"showExpired": show_expired}
        response = await self.get('tables', params=params, timeout=5)
        return response

async def main():
    cl = KBCStorageClient("my_token")
    files = await cl.get_files(show_expired=False)
    print(files)

asyncio.run(main())
