from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.review import Review
from schemas.review import ReviewCreate, ReviewResponse
from services.sentiment_service import SentimentService

router = APIRouter(prefix="/reviews", tags=["reviews"])
sentiment_svc = SentimentService()

@router.get("/{movie_id}", response_model=list[ReviewResponse])
def get_reviews(movie_id: int, db: Session = Depends(get_db)):
    """
    특정 영화에 작성된 모든 리뷰 목록을 조회합니다.
    
    -  movie_id : 조회할 영화의 ID
    -  정렬 : 최신순 (created_at 내림차순)
    -  반환 : 해당 영화의 리뷰 리스트 (Sentiment 정보 포함)
    """
    reviews = (
        db.query(Review)
        .filter(Review.movie_id == movie_id)
        .order_by(Review.created_at.desc())
        .all()
    )
    return reviews


@router.post("/", response_model=ReviewResponse, status_code=201)
def create_review(body: ReviewCreate, db: Session = Depends(get_db)):
    """
    새로운 리뷰를 등록하고, AI 감성 분석 결과를 함께 저장합니다.
    
    1.  감성 분석 : 입력된 리뷰 본문을 AI 모델로 분석하여 긍정/부정 판단
    2.  DB 저장 : 분석 결과와 함께 리뷰 데이터를 데이터베이스에 영구 저장
    3.  반환 : 저장된 리뷰 객체 (ID 및 생성일자 포함)
    """
    # 1. 감성 분석 서비스 호출
    result = sentiment_svc.analyze(body.content)

    # 2. DB 모델 인스턴스 생성
    review = Review(
        movie_id=body.movie_id,
        movie_title=body.movie_title,
        author=body.author,
        content=body.content,
        rating=body.rating,
        sentiment=result["sentiment"],
        sentiment_score=result["score"],
    )

    # 3. 데이터베이스 트랜잭션 처리
    db.add(review)
    db.commit()      # DB에 반영
    db.refresh(review) # DB에서 생성된 ID, 날짜 등을 다시 불러옴
    return review


@router.delete("/{review_id}", status_code=204)
def delete_review(review_id: int, db: Session = Depends(get_db)):
    """
    작성된 리뷰를 삭제합니다.
    
    -  review_id : 삭제할 리뷰의 고유 ID
    -  에러 처리 : 리뷰가 존재하지 않을 경우 404 예외 발생
    -  상태 코드 : 성공 시 204 No Content 반환
    """
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="리뷰를 찾을 수 없습니다.")
    
    db.delete(review)
    db.commit()
    return None # 204 status_code는 본문을 반환하지 않음