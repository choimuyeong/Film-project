from typing import Optional
from pydantic import BaseModel, Field

class MovieSummary(BaseModel):
    """
    영화 검색 결과나 목록(List)에서 보여줄 핵심 요약 정보 스키마입니다.
    가벼운 데이터 전달을 목적으로 합니다.
    """
    id: int = Field(..., description="영화 고유 ID (TMDB 등 외부 API 식별자)")
    title: str = Field(..., description="영화 제목")
    overview: str = Field(..., description="영화 줄거리 요약")
    poster_url: Optional[str] = Field(None, description="포스터 이미지 전체 경로 URL")
    release_date: Optional[str] = Field(None, description="개봉일 (YYYY-MM-DD 형식)")
    vote_average: float = Field(0.0, description="사용자 평균 평점")


class MovieDetail(MovieSummary):
    """
    영화 상세 페이지(Detail)에서 보여줄 전체 정보 스키마입니다.
    MovieSummary의 모든 필드를 상속받으며, 상세 항목들을 추가로 포함합니다.
    """
    genres: list[str] = Field(default=[], description="영화 장르 목록 (예: ['액션', '스릴러'])")
    runtime: Optional[int] = Field(None, description="영화 상영 시간 (분 단위)")
    tagline: Optional[str] = Field(None, description="영화의 핵심 슬로건 또는 한 줄 소개")
    