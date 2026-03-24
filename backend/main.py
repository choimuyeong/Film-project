from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from routers.movies import router as movies_router
from routers.reviews import router as reviews_router
from routers.sentiment import router as sentiment_router

# [DB 설정] 애플리케이션 시작 시, 정의된 모델을 바탕으로 DB 테이블을 자동 생성합니다.
Base.metadata.create_all(bind=engine)

"""
Movie Review API 서비스의 메인 진입점입니다.
FastAPI 설정, CORS 정책, 데이터베이스 초기화 및 라우터 등록을 수행합니다.
"""
app = FastAPI(
    title="Movie Review API",
    description="영화 정보 조회(TMDB), 리뷰 작성(CRUD), AI 감성 분석이 통합된 API 서비스",
    version="1.0.0",
)

# [CORS 설정] React 등 프론트엔드 프레임워크와의 원활한 통신을 위한 보안 설정입니다.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # 프론트엔드 주소 허용
        
        ], 
    allow_credentials=True,
    allow_methods=["*"], # GET, POST, DELETE 등 모든 메서드 허용
    allow_headers=["*"], # 모든 헤더 허용
)

# [라우터 등록] 각 기능별로 분리된 API 경로를 메인 앱에 포함시킵니다.
app.include_router(movies_router)
app.include_router(reviews_router)
app.include_router(sentiment_router)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Movie Review API 서버가 정상 실행 중입니다."}