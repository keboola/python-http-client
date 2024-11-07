import asyncio
import csv
import time
from typing import List

from keboola.http_client import AsyncHttpClient


def generate_jobs(nr_of_jobs):
    return [{'method': 'GET', 'endpoint': str(endpoint)} for endpoint in range(1, nr_of_jobs+1)]

def save_to_csv(results: List[dict]):
    filename = "pokemon_details.csv"
    fieldnames = ["name", "height", "weight"]  # Define the fields you want to store

    with open(filename, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow({
                "name": result["name"],
                "height": result["height"],
                "weight": result["weight"]
            })

async def main_async():
    base_url = "https://pokeapi.co/api/v2/pokemon/"
    start_time = time.time()

    client = AsyncHttpClient(base_url=base_url, max_requests_per_second=20)

    jobs = generate_jobs(1000)

    results = await client.process_multiple(jobs)
    await client.close()

    end_time = time.time()
    print(f"Fetched details for {len(results)} Pokémon in {end_time - start_time:.2f} seconds.")

    save_to_csv(results)


if __name__ == "__main__":
    asyncio.run(main_async())
