import requests
import time
import asyncio
from async_client import AsyncHttpClient


def fetch_pokemon_details_sync(url: str):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


async def fetch_pokemon_details_async(client: AsyncHttpClient, endpoint: str):
    response = await client.get(endpoint)
    return response


def main_sync():
    base_url = "https://pokeapi.co/api/v2/pokemon/"
    start_time = time.time()

    pokemon_details = []
    for i in range(1, 152):
        url = f"{base_url}{i}"
        details = fetch_pokemon_details_sync(url)
        pokemon_details.append(details)

    end_time = time.time()
    print(f"Sync: Fetched details for {len(pokemon_details)} Pokémon in {end_time - start_time:.2f} seconds.")


async def main_async():
    base_url = "https://pokeapi.co/api/v2/pokemon/"
    start_time = time.time()
    client = AsyncHttpClient(base_url=base_url)


    async def fetch_pokemon(client, i):
        endpoint = f"{i}"
        details = await fetch_pokemon_details_async(client, endpoint)
        return details

    async with client as c:
        pokemon_details = await asyncio.gather(*(fetch_pokemon(c, poke_id) for poke_id in range(1, 152)))

    end_time = time.time()
    print(f"Async: Fetched details for {len(pokemon_details)} Pokémon in {end_time - start_time:.2f} seconds.")


if __name__ == "__main__":
    main_sync()
    asyncio.run(main_async())
