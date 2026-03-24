from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import settings

# [Engine] 실제 데이터베이스 파일이나 서버에 연결하는 물리적인 통로입니다.
# check_same_thread=False: SQLite 사용 시 멀티스레드 환경에서 발생할 수 있는 충돌을 방지합니다.
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False}
)

# [SessionLocal] 데이터베이스와의 '대화 창구'인 세션을 생성하는 공장입니다.
# 하나하나의 요청(Request)마다 이 공장에서 세션을 하나씩 뽑아서 사용합니다.
SessionLocal = sessionmaker(
    autocommit=False,  # 데이터를 명시적으로 commit() 할 때만 실제 저장
    autoflush=False,   # 쿼리 실행 전 변경사항을 자동으로 DB에 반영하지 않음
    bind=engine        # 앞서 만든 엔진과 연결
)

# [Base] 모든 데이터베이스 모델(Review 등)의 조상 클래스입니다.
# 이 클래스를 상속받아 테이블 구조를 정의하면 SQLAlchemy가 인식합니다.
Base = declarative_base()

def get_db():
    """
    FastAPI 의존성 주입(Dependency Injection)을 위한 데이터베이스 세션 생성기입니다.
    
    - 요청이 들어오면 세션을 생성하고(yield), 
    - 처리가 끝나면 에러 발생 여부와 상관없이 세션을 안전하게 닫습니다(close).
    
    Yields:
        Session: SQLAlchemy 데이터베이스 세션 객체
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        # 응답이 클라이언트에게 전달된 후 마지막에 반드시 실행되어 연결을 해제합니다.
        db.close()