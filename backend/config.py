from pydantic_settings import BaseSettings


#########################
### 환경변수 관리 클래스 ###
#########################

class Settings(BaseSettings):
    tmdb_api_key: str = ""   # TMDB API 키 (기본값 : 빈 문자열)
    database_url: str = "sqlite:///./movie_review.db"  # DB 파일 경로

    class Config:
        env_file = ".env"  # 읽어올 환경변수 파일 지정.


settings = Settings()