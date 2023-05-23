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

    # Fetch Pokemon Details

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
        poke_id = 1

        # Check if the file exists and write the header if it doesn't
        filename = "pokemon_details.csv"
        fieldnames = ["name", "height", "weight"]

        try:
            with open(filename, "x", newline="") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
        except FileExistsError:
            pass

        while True:
            details = await fetch_pokemon(c, poke_id)
            if details is None:
                break

            await save_to_csv(details)

            poke_id += 1

    end_time = time.time()
    print(f"Async: Fetched details for {poke_id - 1} Pokémon in {end_time - start_time:.2f} seconds.")

async def save_to_csv(details):
    filename = "pokemon_details.csv"
    fieldnames = ["name", "height", "weight"]

    with open(filename, "a", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writerow({
            "name": details["name"],
            "height": details["height"],
            "weight": details["weight"]
        })

if __name__ == "__main__":
    asyncio.run(main_async())
