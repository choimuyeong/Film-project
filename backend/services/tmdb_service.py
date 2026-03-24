from typing import Optional
import httpx
from config import settings
from schemas.movie import MovieDetail, MovieSummary

TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"


class TMDBService:
    """
    TMDB(The Movie Database) 외부 API와 통신하여 영화 정보를 가져오는 서비스 클래스입니다.
    검색 및 상세 정보 조회를 담당하며, 결과를 Pydantic 스키마 형태로 반환합니다.
    """

    def __init__(self):
        """
        API 호출에 필요한 공통 파라미터(API 키, 언어 설정)를 초기화합니다.
        """
        self.params = {
            "api_key": settings.tmdb_api_key,
            "language": "ko-KR"
        }

    async def search(self, query: str, page: int = 1) -> list[MovieSummary]:
        """
        영화 제목 키워드를 사용하여 영화 목록을 검색합니다.

        Args:
            query (str): 검색할 영화 제목 키워드
            page (int, optional): 검색 결과 페이지 번호. 기본값은 1.

        Returns:
            list[MovieSummary]: 검색 결과 리스트 (MovieSummary 객체 목록)
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
        특정 영화의 ID를 사용하여 상세 정보를 조회합니다.

        Args:
            movie_id (int): 조회할 영화의 TMDB 고유 ID

        Returns:
            Optional[MovieDetail]: 영화 상세 정보 객체. 데이터가 없을 경우 None을 반환할 수 있음.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{TMDB_BASE_URL}/movie/{movie_id}",
                params=self.params
            )
            movie = response.json()

        # 응답 받은 데이터를 MovieDetail 스키마에 맞게 매핑하여 반환
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