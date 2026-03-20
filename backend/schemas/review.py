from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


#############################################
### Pydantic 파일. API 요청 데이터 형식 정의 ###
#############################################

class ReviewCreate(BaseModel):
    """
    사용자가 새로운 리뷰를 작성할 때(Request Body) 사용하는 스키마입니다.
    데이터 입력 시 유효성 검사(Validation)를 수행합니다.
    """
    movie_id: int
    movie_title: str
    author: str = Field(min_length=1, max_length=50, description="작성자 이름")
    content: str = Field(min_length=10, max_length=1000, description="리뷰 본문 (최소 10자)")
    rating: float = Field(ge=1.0, le=5.0, description="평점 (1.0~5.0)")

    @field_validator("rating")
    @classmethod
    def round_rating(cls, v: float) -> float:
        """입력받은 평점을 0.5 단위로 반올림합니다."""
        return round(v * 2) / 2


class ReviewResponse(BaseModel):
    """
    DB에서 조회한 리뷰 데이터를 클라이언트에게 응답(Response)할 때 사용하는 스키마입니다.
    ORM 모델 객체를 Pydantic 모델로 변환하여 전달합니다.
    """
    id: int
    movie_id: int
    movie_title: str
    author: str
    content: str
    rating: float
    sentiment: Optional[str] = None
    sentiment_score: Optional[float] = None
    created_at: datetime

    model_config = {
        "from_attributes": True, # SQLAlchemy 모델 객체를 바로 읽어올 수 있게 설정
    }


class SentimentResponse(BaseModel):
    """
    AI 모델을 통한 감성 분석 결과만을 단독으로 반환할 때 사용하는 스키마입니다.
    """
    text: str
    sentiment: str        # "positive" / "negative"
    score: float          # 0.0 ~ 1.0
    label_kor: str        # "긍정" / "부정"