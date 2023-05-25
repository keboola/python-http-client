import requests
import time
import csv

def fetch_pokemon_details_sync(url: str):
    r = requests.get(url)
    r.raise_for_status()
    return r.json()

def main_sync():
    base_url = "https://pokeapi.co/api/v2/pokemon/"
    start_time = time.time()
    pokemon_details = []
    poke_id = 1

    while True:
        url = f"{base_url}{poke_id}"
        try:
            details = fetch_pokemon_details_sync(url)
            pokemon_details.append(details)
            poke_id += 1
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                break
            else:
                raise

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
    print(f"Fetched details for {len(pokemon_details)} Pokémon in {end_time - start_time:.2f} seconds.")

if __name__ == "__main__":
    main_sync()
