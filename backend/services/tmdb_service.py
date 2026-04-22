from typing import Optional
import httpx
from config import settings
from schemas.movie import MovieDetail, MovieSummary

TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

class TMDBService:
    """
    TMDB(The Movie Database) 외부 API와 통신하여 영화 정보를 가져오는 서비스 클래스입니다.
    비동기 HTTP 클라이언트를 사용하여 영화 검색, 상세 조회, 인기 목록 조회를 수행합니다.
    """

    def __init__(self):
        """
        API 호출 시 공통으로 사용되는 인증 키와 언어 설정을 초기화합니다.
        """
        self.params = {
            "api_key": settings.tmdb_api_key,
            "language": "ko-KR"
        }

    async def search(self, query: str, page: int = 1) -> list[MovieSummary]:
        """
        영화 제목 키워드를 기반으로 영화 목록을 검색합니다.

        Args:
            query (str): 검색할 영화 제목 키워드
            page (int): 검색 결과 페이지 번호 (기본값: 1)

        Returns:
            list[MovieSummary]: 검색된 영화들의 요약 정보 리스트
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{TMDB_BASE_URL}/search/movie",
                params={**self.params, "query": query, "page": page}
            )
            data = response.json()

        return [
            MovieSummary(
                id=movie["id"],
                title=movie["title"],
                overview=movie["overview"],
                poster_url=f"{TMDB_IMAGE_BASE}{movie['poster_path']}" if movie.get("poster_path") else None,
                release_date=movie.get("release_date"),
                vote_average=movie.get("vote_average", 0.0),
            )
            for movie in data.get("results", [])
        ]

    async def get_detail(self, movie_id: int) -> Optional[MovieDetail]:
        """
        특정 영화의 고유 ID를 사용하여 상세 정보를 조회합니다.

        Args:
            movie_id (int): 조회할 영화의 TMDB 고유 ID

        Returns:
            Optional[MovieDetail]: 장르, 런타임 등이 포함된 상세 정보 객체
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{TMDB_BASE_URL}/movie/{movie_id}",
                params=self.params
            )
            movie = response.json()

        return MovieDetail(
            id=movie["id"],
            title=movie["title"],
            overview=movie["overview"],
            poster_url=f"{TMDB_IMAGE_BASE}{movie['poster_path']}" if movie.get("poster_path") else None,
            release_date=movie.get("release_date"),
            vote_average=movie.get("vote_average", 0.0),
            genres=[g["name"] for g in movie.get("genres", [])],
            runtime=movie.get("runtime"),
            tagline=movie.get("tagline"),
        )
    


    async def get_semantic_candidates(self, pages: int = 2) -> list[MovieSummary]:
        """
        시맨틱 재정렬을 위한 풍부한 후보군 데이터를 수집합니다.
        
        단일 엔드포인트가 아닌 '현재 상영 중', '인기 영화', '높은 평점' 세 곳에서 
        데이터를 수집하여 더 넓은 범위의 시맨틱 매칭을 가능하게 합니다.
        
        - 중복 제거: 여러 카테고리에 중복 포함된 영화는 movie_id를 기준으로 하나만 유지합니다.
        - 수집 범위: 각 카테고리당 지정된 페이지 수만큼 수집 (기본 2페이지 시 최대 120개 내외)

        Args:
            pages (int): 카테고리별로 가져올 페이지 수 (기본값: 2)

        Returns:
            list[MovieSummary]: 중복이 제거된 영화 요약 정보 리스트
        """
        endpoints = [
            "movie/now_playing",
            "movie/popular",
            "movie/top_rated",
        ]

        candidates: list[MovieSummary] = []
        seen_ids: set[int] = set()

        async with httpx.AsyncClient() as client:
            for endpoint in endpoints:
                for p in range(1, pages + 1):
                    response = await client.get(
                        f"{TMDB_BASE_URL}/{endpoint}",
                        params={**self.params, "page": p},
                    )
                    data = response.json()

                    for movie in data.get("results", []):
                        movie_id = movie["id"]
                        if movie_id in seen_ids:
                            continue
                        seen_ids.add(movie_id)

                        candidates.append(
                            MovieSummary(
                                id=movie_id,
                                title=movie["title"],
                                overview=movie.get("overview", ""),
                                poster_url=f"{TMDB_IMAGE_BASE}{movie['poster_path']}" if movie.get("poster_path") else None,
                                release_date=movie.get("release_date"),
                                vote_average=movie.get("vote_average", 0.0),
                            )
                        )

        return candidates


    # async def get_popular_candidates(self, pages: int = 3) -> list[MovieSummary]:
    #     """
    #     시맨틱 재정렬 등을 위한 후보군으로 쓰일 인기 영화 목록을 여러 페이지에 걸쳐 가져옵니다.

    #     Args:
    #         pages (int): 가져올 페이지 수 (기본값: 3, 약 60개 영화)

    #     Returns:
    #         list[MovieSummary]: 수집된 인기 영화 요약 정보 리스트
    #     """
    #     results: list[MovieSummary] = []

    #     async with httpx.AsyncClient() as client:
    #         for p in range(1, pages + 1):
    #             response = await client.get(
    #                 f"{TMDB_BASE_URL}/movie/popular",
    #                 params={**self.params, "page": p}
    #             )
    #             data = response.json()

    #             for movie in data.get("results", []):
    #                 results.append(
    #                     MovieSummary(
    #                         id=movie["id"],
    #                         title=movie["title"],
    #                         overview=movie.get("overview", ""),
    #                         poster_url=f"{TMDB_IMAGE_BASE}{movie['poster_path']}" if movie.get("poster_path") else None,
    #                         release_date=movie.get("release_date"),
    #                         vote_average=movie.get("vote_average", 0.0),
    #                     )
    #                 )
    #     return results