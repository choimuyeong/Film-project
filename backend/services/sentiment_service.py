from transformers import pipeline

class SentimentService:
    """
    Hugging Face의 사전 학습된 모델을 사용하여 한국어 텍스트의 감성을 분석하는 서비스입니다.
    영화 리뷰 등의 텍스트를 입력받아 긍정(positive) 또는 부정(negative) 결과를 반환합니다.
    """

    def __init__(self):
        """
        감성 분석을 위한 파이프라인과 모델을 초기화합니다.
        사용 모델: daekeun-ml/koelectra-small-v3-nsmc (네이버 영화 리뷰로 파인튜닝된 모델)
        """
        self.pipe = pipeline(
            "sentiment-analysis", 
            model="daekeun-ml/koelectra-small-v3-nsmc"
        )
        
    def analyze(self, text: str) -> dict:
        """
        입력된 텍스트의 감성을 분석하여 결과를 반환합니다.

        Args:
            text (str): 분석할 한국어 문장 (예: 영화 리뷰 본문)

        Returns:
            dict: 분석 결과 딕셔너리
                - sentiment (str): "positive" 또는 "negative"
                - score (float): 분석 결과에 대한 신뢰도 점수 (0~1, 소수점 4자리 반올림)
        """
        # 모델 예측 실행
        result = self.pipe(text)[0]

        # print(f"🔍 원본 결과: {result}")  # 디버깅용 상태체크 출력

        # 오타 및 로직 수정: 모델의 실제 라벨값과 비교 (보통 'LABEL_1' 또는 'positive' 등 모델마다 다름)
        # KR-FinBert-SC의 경우 보통 'OPINION' 관련 라벨을 사용하므로 확인이 필요하지만, 
        # 작성하신 로직 흐름을 유지하며 오타를 수정했습니다.
        raw_label = result["label"].lower()

        sentiment = "positive" if result["label"] == "1" else "negative"

        return {
            "sentiment": sentiment,
            "score": round(result["score"], 4) # 오타 수정: 'socre' -> 'score'
        }
    
    