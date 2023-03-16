from async_client import AsyncHttpClient
import requests
import asyncio
import time

common_url = "https://pokeapi.co/api/v2/"
nr_of_pokemons = 202


async def async_get(url, nr_of_pokemons):
    pokemons = []
    client = AsyncHttpClient(url)
    with client:
        for n in range(1, nr_of_pokemons):
            r = await client.get(f"pokemon/{str(n)}")
            pokemons.append(r.json()['name'])


def normal_get(url, nr_of_pokemons):
    pokemons = []
    for n in range(1, nr_of_pokemons):
        r = requests.get(url + f"pokemon/{str(n)}")
        pokemons.append(r.json()['name'])


start_time = time.time()
asyncio.run(async_get(common_url, nr_of_pokemons))
print(f"Async took {time.time() - start_time} seconds.")

start_time = time.time()
normal_get(common_url, nr_of_pokemons)
print(f"Normal took {time.time() - start_time} seconds.")
