import json
import re
from pathlib import Path

import faiss
import torch
import torch.nn.functional as F
from sentence_transformers import SentenceTransformer

from schemas.movie import MovieSummary

TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"


class SemanticService:
    """
    영화 시맨틱 검색 서비스입니다.

    1) `data/faiss.index` + `data/metadata.json`이 있으면 FAISS 기반 검색을 우선 사용합니다.
    2) FAISS 파일이 없으면 기존 임베딩 재정렬 방식으로 fallback 합니다.
    """

    def __init__(self):
        self.embedder = SentenceTransformer(
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
        self.index_path = Path("data/faiss.index")
        self.metadata_path = Path("data/metadata.json")
        self.index: faiss.Index | None = None
        self.metadata: list[dict] = []
        self.faiss_ready = False
        self._load_faiss_artifacts()

    def _load_faiss_artifacts(self) -> None:
        """
        런타임 시작 시 FAISS 인덱스/메타데이터를 로드합니다.
        파일이 없거나 로드 실패 시 faiss_ready=False 상태로 유지합니다.
        """
        if not self.index_path.exists() or not self.metadata_path.exists():
            return

        try:
            self.index = faiss.read_index(str(self.index_path))
            with self.metadata_path.open("r", encoding="utf-8") as f:
                loaded = json.load(f)
            if isinstance(loaded, list):
                self.metadata = loaded
                self.faiss_ready = True
        except Exception:
            self.index = None
            self.metadata = []
            self.faiss_ready = False

    def _to_movie_summary(self, movie: dict) -> MovieSummary:
        poster_path = movie.get("poster_path")
        poster_url = f"{TMDB_IMAGE_BASE}{poster_path}" if poster_path else None

        return MovieSummary(
            id=int(movie.get("id")),
            title=(movie.get("title") or "").strip(),
            overview=(movie.get("overview") or "").strip(),
            poster_url=poster_url,
            release_date=movie.get("release_date"),
            vote_average=float(movie.get("vote_average", 0.0) or 0.0),
        )

    def _title_key(self, title: str) -> str:
        # 공백/구두점을 제거해 "같은 제목" 중복을 줄입니다.
        normalized = re.sub(r"\W+", "", (title or "").lower(), flags=re.UNICODE)
        return normalized

    def _is_low_information(self, movie: MovieSummary) -> bool:
        """
        의미 검색 품질을 해치는 항목을 제외합니다.
        - 줄거리가 너무 짧음
        - 줄거리와 제목이 사실상 동일
        """
        overview = (movie.overview or "").strip()
        if len(overview) < 20:
            return True

        title_key = self._title_key(movie.title)
        overview_key = self._title_key(overview)
        return bool(title_key and overview_key and title_key == overview_key)

    def search_by_faiss(
        self,
        query: str,
        top_k: int = 10,
        min_score: float = 0.33,
    ) -> list[MovieSummary]:
        """
        FAISS 인덱스를 이용해 줄거리 유사도 상위 영화를 반환합니다.
        """
        if (
            not self.faiss_ready
            or self.index is None
            or not self.metadata
            or not query.strip()
        ):
            return []

        query_emb = self.embedder.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True,
        ).astype("float32")

        search_k = min(max(top_k * 30, top_k), len(self.metadata))
        scores, indices = self.index.search(query_emb, search_k)

        results: list[MovieSummary] = []
        seen_ids: set[int] = set()
        seen_title_keys: set[str] = set()

        for score, raw_idx in zip(scores[0], indices[0]):
            idx = int(raw_idx)
            if idx < 0 or idx >= len(self.metadata):
                continue
            if float(score) < min_score:
                continue

            movie = self._to_movie_summary(self.metadata[idx])
            if self._is_low_information(movie):
                continue
            title_key = self._title_key(movie.title)

            if movie.id in seen_ids:
                continue
            if title_key and title_key in seen_title_keys:
                continue

            seen_ids.add(movie.id)
            if title_key:
                seen_title_keys.add(title_key)
            results.append(movie)

            if len(results) >= top_k:
                break

        return results

    def rerank_by_overview_similarity(
        self,
        query: str,
        movies: list[MovieSummary],
        top_k: int = 10,
        min_score: float = 0.33,
        title_bonus: float = 0.05,
    ) -> list[MovieSummary]:
        """
        검색어와 영화 줄거리 간의 유사도를 계산하고 결과를 재정렬합니다.
        """
        candidates = [m for m in movies if m.overview and m.overview.strip()]
        if not candidates:
            return movies[:top_k]

        texts = [m.overview for m in candidates]

        query_emb = self.embedder.encode(query, convert_to_tensor=True)
        text_embs = self.embedder.encode(texts, convert_to_tensor=True)

        query_emb = F.normalize(query_emb, p=2, dim=0)
        text_embs = F.normalize(text_embs, p=2, dim=1)
        sim_scores = torch.matmul(text_embs, query_emb).tolist()

        q_tokens = [t for t in query.lower().split() if t]

        ranked_with_score = []
        for movie, sim in zip(candidates, sim_scores):
            score = sim

            title_lower = (movie.title or "").lower()
            if any(token in title_lower for token in q_tokens):
                score += title_bonus

            if score >= min_score:
                ranked_with_score.append((movie, score))

        if not ranked_with_score:
            ranked_with_score = list(zip(candidates, sim_scores))

        ranked_with_score.sort(key=lambda x: x[1], reverse=True)

        deduped: list[MovieSummary] = []
        seen_ids: set[int] = set()
        seen_title_keys: set[str] = set()

        for movie, _ in ranked_with_score:
            title_key = self._title_key(movie.title)

            if movie.id in seen_ids:
                continue
            if title_key and title_key in seen_title_keys:
                continue

            seen_ids.add(movie.id)
            if title_key:
                seen_title_keys.add(title_key)
            deduped.append(movie)

            if len(deduped) >= top_k:
                break

        return deduped
