from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
from database import Base


class Review(Base):
    """
    영화 리뷰 데이터를 저장하고 감성 분석 결과를 관리하는 ORM 모델입니다.

    `__tablename__` : 실제 DB에 생성될 테이블 이름.
    `Column` : 테이블의 컬럼(열)을 정의. 엑셀로 치면 각 열 제목.

    Attributes:
        id (Integer): 기본키 (Primary Key)
        movie_id (Integer): 영화 고유 식별 번호
        movie_title (String): 영화 제목
        author (String): 리뷰 작성자 이름
        content (Text): 리뷰 본문 내용
        rating (Float): 사용자 별점 (1.0 ~ 5.0)
        sentiment (String): 감성 분석 결과 (positive / negative)
        sentiment_score (Float): 감성 분석 확신도 점수 (0.0 ~ 1.0)
        created_at (DateTime): 데이터 생성 일시 (자동 생성)
    """

    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)

    # 영화 정보
    movie_id = Column(Integer, nullable=False, index=True)
    movie_title = Column(String(200), nullable=False)

    # 리뷰 내용
    author = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    rating = Column(Float, nullable=False)  # 1.0 ~ 5.0

    # 감성 분석 결과 (4단계에서 채워짐)
    sentiment = Column(String(20), nullable=True)   # "positive" / "negative"
    sentiment_score = Column(Float, nullable=True)  # 0.0 ~ 1.0

    # 자동 타임스탬프
    created_at = Column(DateTime(timezone=True), server_default=func.now())