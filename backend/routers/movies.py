from fastapi import APIRouter, HTTPException, Query
from schemas.movie import MovieSummary, MovieDetail
from services.tmdb_service import TMDBService
from services.semantic_service import SemanticService

# 영화 관련 API를 담당하는 라우터 설정
router = APIRouter(prefix="/movies", tags=["movies"])
tmdb = TMDBService()
semantic = SemanticService()

@router.get("/search", response_model=list[MovieSummary])
async def search_movies(
    q: str = Query(..., min_length=1, description="검색할 영화 제목"),
    page: int = Query(default=1, ge=1, description="페이지 번호"),
    mode: str = Query(default="title", pattern="^(title|semantic)$", description="검색 모드: title | semantic"),
    top_k: int = Query(default=10, ge=1, le=20, description="semantic 모드 결과 개수"),
):
    """
    영화 제목 키워드 또는 줄거리 유사도(Semantic)를 기반으로 영화를 검색합니다.
    
    - **q**: 검색할 영화 키워드 (최소 1글자)
    - **page**: 검색 결과 페이지 번호
    - **mode**: 
        - `title`: TMDB 기본 검색 결과 반환
        - `semantic`: 줄거리 유사도 기반 상위 순위 재정렬 수행
    - **top_k**: 시맨틱 모드 시 반환할 결과의 개수 (최대 20개)
    """
    # 1. 검색 모드에 따른 처리
    if mode == "semantic":
        # FAISS 인덱스가 준비되어 있으면 우선 사용
        results = semantic.search_by_faiss(query=q, top_k=top_k)

        # FAISS 파일이 없거나 결과가 비어 있으면 기존 방식으로 fallback
        if not results:
            base_results = await tmdb.search(query=q, page=page)
            if not base_results:
                base_results = await tmdb.get_semantic_candidates(pages=5)

            results = semantic.rerank_by_overview_similarity(
                query=q,
                movies=base_results,
                top_k=top_k,
                min_score=0.33,
            )
    else:
        results = await tmdb.search(query=q, page=page)
    
    # 2. 결과 예외 처리
    if not results:
        raise HTTPException(status_code=404, detail="검색 결과가 없습니다.")
        
    return results

@router.get("/{movie_id}", response_model=MovieDetail)
async def get_movie(movie_id: int):
    """
    특정 영화의 상세 정보를 조회합니다.
    
    - **movie_id**: TMDB 영화 고유 식별자 (ID)
    - **반환값**: 상세 정보 (줄거리, 장르, 개봉일 등)
    """
    movie = await tmdb.get_detail(movie_id=movie_id)
    
    if not movie:
        raise HTTPException(status_code=404, detail="영화를 찾을 수 없습니다.")
        
    return movie

