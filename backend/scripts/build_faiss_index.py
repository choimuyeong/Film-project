import json
import argparse
import re
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


def load_movies(input_path: Path):
    with input_path.open("r", encoding="utf-8") as f:
        movies = json.load(f)

    cleaned = []
    seen = set()

    for m in movies:
        movie_id = m.get("id")
        overview = (m.get("overview") or "").strip()
        title = (m.get("title") or "").strip()

        if not movie_id or movie_id in seen:
            continue
        if not overview or len(overview) < 10:
            continue

        seen.add(movie_id)
        cleaned.append(
            {
                "id": movie_id,
                "title": title,
                "overview": overview,
                "release_date": m.get("release_date"),
                "vote_average": m.get("vote_average", 0.0),
                "poster_path": m.get("poster_path"),
            }
        )

    return cleaned


def normalize_key(text: str) -> str:
    return re.sub(r"\W+", "", (text or "").lower(), flags=re.UNICODE)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, default="data/tmdb_movies.json")
    parser.add_argument("--index-out", type=str, default="data/faiss.index")
    parser.add_argument("--meta-out", type=str, default="data/metadata.json")
    parser.add_argument(
        "--model",
        type=str,
        default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    )
    parser.add_argument("--batch-size", type=int, default=128)
    args = parser.parse_args()

    input_path = Path(args.input)
    index_out = Path(args.index_out)
    meta_out = Path(args.meta_out)

    raw_movies = load_movies(input_path)

    # 의미 검색 품질을 해치는 항목 제거 및 임베딩 텍스트 구성
    movies = []
    for m in raw_movies:
        title = (m.get("title") or "").strip()
        overview = (m.get("overview") or "").strip()

        if len(overview) < 20:
            continue
        if normalize_key(title) and normalize_key(title) == normalize_key(overview):
            continue

        m["search_text"] = f"{title}. {overview}" if title else overview
        movies.append(m)

    print(f"[INFO] cleaned movies: {len(movies)}")

    texts = [m["search_text"] for m in movies]

    model = SentenceTransformer(args.model)
    emb = model.encode(
        texts,
        batch_size=args.batch_size,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True,
    )

    emb = emb.astype("float32")
    dim = emb.shape[1]

    index = faiss.IndexFlatIP(dim)  # cosine(sim) == inner product (normalized)
    index.add(emb)

    index_out.parent.mkdir(parents=True, exist_ok=True)
    meta_out.parent.mkdir(parents=True, exist_ok=True)

    faiss.write_index(index, str(index_out))

    metadata = [{k: v for k, v in m.items() if k != "search_text"} for m in movies]
    with meta_out.open("w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False)

    print(f"[DONE] index saved: {index_out} (ntotal={index.ntotal}, dim={dim})")
    print(f"[DONE] meta saved: {meta_out}")


if __name__ == "__main__":
    main()
