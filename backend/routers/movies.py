from fastapi import APIRouter, HTTPException, Query
from schemas.movie import MovieSummary, MovieDetail
from services.tmdb_service import TMDBService

# API 경로의 공통 접두사(/movies)와 문서화를 위한 태그 설정
router = APIRouter(prefix="/movies", tags=["movies"])
tmdb = TMDBService()

@router.get("/search", response_model=list[MovieSummary])
async def search_movies(
    q: str = Query(..., min_length=1, description="검색할 영화 제목"),
    page: int = Query(default=1, ge=1, description="페이지 번호"),
):
    """
    영화 제목 키워드로 검색을 수행합니다.
    
    - q : 검색할 영화 제목 (최소 1글자 이상 필수)
    - page : 결과 페이지 번호 (1 이상)
    - 반환값 : 검색된 영화 요약 정보 리스트
    """
    results = await tmdb.search(query=q, page=page)
    
    if not results:
        # 오타 수정: drtail -> detail
        raise HTTPException(status_code=404, detail="검색 결과가 없습니다.")
    return results


@router.get("/{movie_id}", response_model=MovieDetail)
async def get_movie(movie_id: int):
    """
    특정 영화의 상세 정보를 조회합니다.
    
    - movie_id : 조회할 영화의 고유 식별자 (ID)
    - 반환값 : 영화 상세 정보 (장르, 런타임 등 포함)
    """
    movie = await tmdb.get_detail(movie_id=movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="영화를 찾을 수 없습니다.")
    return movie

