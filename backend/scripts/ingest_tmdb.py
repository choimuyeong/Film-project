import os
import json
import time
import asyncio
import argparse
from pathlib import Path

import httpx
from dotenv import load_dotenv

TMDB_BASE_URL = "https://api.themoviedb.org/3"


async def fetch_page(
    client: httpx.AsyncClient,
    api_key: str,
    page: int,
    language: str,
    delay_sec: float,
    max_retries: int = 5,
) -> list[dict]:
    await asyncio.sleep(delay_sec)

    params = {
        "api_key": api_key,
        "language": language,
        "sort_by": "popularity.desc",
        "include_adult": "false",
        "include_video": "false",
        "page": page,
    }

    retry = 0
    while True:
        try:
            resp = await client.get(f"{TMDB_BASE_URL}/discover/movie", params=params, timeout=20.0)

            if resp.status_code == 429:
                wait = min(2 ** retry, 30)
                print(f"[WARN] 429 on page={page}, retry in {wait}s")
                await asyncio.sleep(wait)
                retry += 1
                if retry > max_retries:
                    print(f"[ERROR] page={page} max retries exceeded (429)")
                    return []
                continue

            resp.raise_for_status()
            data = resp.json()
            return data.get("results", [])

        except Exception as e:
            wait = min(2 ** retry, 30)
            print(f"[WARN] page={page} error={e}, retry in {wait}s")
            await asyncio.sleep(wait)
            retry += 1
            if retry > max_retries:
                print(f"[ERROR] page={page} max retries exceeded")
                return []


async def ingest(
    start_page: int,
    end_page: int,
    language: str,
    delay_sec: float,
    out_path: Path,
):
    load_dotenv()
    api_key = os.getenv("TMDB_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("TMDB_API_KEY is empty. Set it in backend/.env")

    all_movies: list[dict] = []
    seen_ids: set[int] = set()

    async with httpx.AsyncClient() as client:
        for page in range(start_page, end_page + 1):
            rows = await fetch_page(client, api_key, page, language, delay_sec)
            print(f"[INFO] page={page} fetched={len(rows)}")

            for m in rows:
                movie_id = m.get("id")
                if movie_id in seen_ids:
                    continue
                seen_ids.add(movie_id)

                all_movies.append(
                    {
                        "id": movie_id,
                        "title": m.get("title", ""),
                        "overview": m.get("overview", ""),
                        "release_date": m.get("release_date"),
                        "vote_average": m.get("vote_average", 0.0),
                        "poster_path": m.get("poster_path"),
                        "original_language": m.get("original_language"),
                        "popularity": m.get("popularity", 0.0),
                    }
                )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(all_movies, f, ensure_ascii=False, indent=2)

    print(f"[DONE] total={len(all_movies)} saved={out_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-page", type=int, default=1)
    parser.add_argument("--end-page", type=int, default=20)
    parser.add_argument("--language", type=str, default="ko-KR")
    parser.add_argument("--delay", type=float, default=0.25)
    parser.add_argument("--out", type=str, default="data/tmdb_movies.json")
    args = parser.parse_args()

    start = time.time()
    asyncio.run(
        ingest(
            start_page=args.start_page,
            end_page=args.end_page,
            language=args.language,
            delay_sec=args.delay,
            out_path=Path(args.out),
        )
    )
    print(f"[TIME] {time.time() - start:.1f}s")


if __name__ == "__main__":
    main()
