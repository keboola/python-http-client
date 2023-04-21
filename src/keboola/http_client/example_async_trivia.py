import asyncio
from async_client import AsyncHttpClient


async def fetch_trivia_questions(client: AsyncHttpClient, category_id: int, amount: int = 10) -> dict:
    response = await client.get("api.php", params={"amount": amount, "category": category_id, "type": "multiple"})
    data = response.json()
    return data["results"]


async def main():
    base_url = "https://opentdb.com/"
    client = AsyncHttpClient(base_url)

    # Category IDs for General Knowledge, Science & Nature, and Sports
    categories = [9, 17, 21]

    tasks = [fetch_trivia_questions(client, category_id) for category_id in categories]
    trivia_questions = await asyncio.gather(*tasks)

    for idx, questions in enumerate(trivia_questions):
        print(f"Category {categories[idx]}:")
        for q in questions:
            print(f"  - {q['question']}")

if __name__ == "__main__":
    asyncio.run(main())
