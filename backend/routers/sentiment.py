from fastapi import APIRouter
from pydantic import BaseModel
from schemas.review import SentimentResponse
from services.sentiment_service import SentimentService

# 감성 분석 기능을 전담하는 라우터 설정
router = APIRouter(prefix="/sentiment", tags=["sentiment"])
sentiment_svc = SentimentService()


class AnalyzeRequest(BaseModel):
    text: str


@router.post("/analyze", response_model=SentimentResponse)
def analyze_sentiment(body: AnalyzeRequest):
    """
    입력된 텍스트에 대해 AI 감성 분석을 수행합니다.
    
    -  text : 분석하고자 하는 한국어 문장
    -  과정 : SentimentService를 통해 모델 추론 후, 결과를 SentimentResponse 형식으로 변환
    -  반환 : 분석된 감성(영어/한국어), 신뢰도 점수, 원문 텍스트
    """
    # 1. 서비스 레이어에서 AI 모델 추론 실행
    result = sentiment_svc.analyze(body.text)
    
    # 2. 분석 결과에 한국어 라벨을 추가하여 응답 모델 생성
    # Pydantic 모델(SentimentResponse)의 인스턴스를 직접 생성하여 반환합니다.
    return SentimentResponse(
        text=body.text,
        sentiment=result["sentiment"],
        score=result["score"],
        label_kor="긍정" if result["sentiment"] == "positive" else "부정",
    )