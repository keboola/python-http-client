import time
import asyncio
from keboola.http_client import AsyncHttpClient
import csv
import httpx
import os


async def fetch_pokemon(client, poke_id):
    try:
        r = await client.get(str(poke_id))
        return r
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return None
        else:
            raise


async def save_to_csv(details):
    filename = "pokemon_details.csv"
    fieldnames = ["name", "height", "weight"]

    file_exists = os.path.isfile(filename)
    mode = "a" if file_exists else "w"

    with open(filename, mode, newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow({
            "name": details["name"],
            "height": details["height"],
            "weight": details["weight"]
        })


async def main_async():
    base_url = "https://pokeapi.co/api/v2/pokemon/"
    start_time = time.time()

    async with AsyncHttpClient(base_url=base_url, max_requests_per_second=20) as c:
        poke_id = 1

        while True:
            details = await fetch_pokemon(c, poke_id)
            if details is None:
                break

            await save_to_csv(details)

            poke_id += 1

    end_time = time.time()
    print(f"Async: Fetched details for {poke_id - 1} Pokémon in {end_time - start_time:.2f} seconds.")


if __name__ == "__main__":
    asyncio.run(main_async())
