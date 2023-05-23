import time
import asyncio
from keboola.http_client import AsyncHttpClient
import csv
import httpx

async def fetch_pokemon_details_async(client: AsyncHttpClient, endpoint: str):
    r = await client.get(endpoint)
    return r

async def main_async():
    base_url = "https://pokeapi.co/api/v2/pokemon/"
    start_time = time.time()
    client = AsyncHttpClient(base_url=base_url)

    async def fetch_pokemon(client, poke_id):
        try:
            r = await fetch_pokemon_details_async(client, str(poke_id))
            return r
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            else:
                raise

    async with client as c:
        pokemon_details = []
        poke_id = 1

        while True:
            details = await fetch_pokemon(c, poke_id)
            if details is None:
                break
            pokemon_details.append(details)
            poke_id += 1

    # Save details to CSV
    filename = "pokemon_details.csv"
    fieldnames = ["name", "height", "weight"]  # Define the fields you want to store

    with open(filename, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for details in pokemon_details:
            writer.writerow({
                "name": details["name"],
                "height": details["height"],
                "weight": details["weight"]
            })

    end_time = time.time()
    print(f"Async: Fetched details for {len(pokemon_details)} Pokémon in {end_time - start_time:.2f} seconds.")

if __name__ == "__main__":
    asyncio.run(main_async())
