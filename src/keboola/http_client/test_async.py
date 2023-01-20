from async_client import AsyncHttpClient
import requests
import asyncio
import time


async def get_pokemon(client, url):
    resp = await client.get(url)
    print(resp.json()['name'])


async def async_get():
    pokemons = []
    client = AsyncHttpClient("https://pokeapi.co/api/v2/")
    with client:
        for n in range(1, 151):
            r = await client.get(f"pokemon/{str(n)}")
            pokemons.append(r.json()['name'])


def normal_get():
    pokemons = []
    baseurl = "https://pokeapi.co/api/v2/pokemon/"
    for n in range(1, 151):
        url = baseurl + str(n)
        r = requests.get(url)
        pokemons.append(r.json()['name'])


start_time = time.time()
asyncio.run(async_get())
print(f"Async took {time.time() - start_time} seconds.")

start_time = time.time()
normal_get()
print(f"Normal took {time.time() - start_time} seconds.")
