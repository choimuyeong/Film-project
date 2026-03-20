from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import settings

######################
### DB에 연결할 엔진 ###
######################

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False}
)
####################################
### engine을 통해 DB session 설정 ### 
####################################

SessionLocal = sessionmaker(
    autocommit=False,  # 자동 저장 안함
    autoflush=False,   # 자동 flush 안함
    bind=engine        # engine 연결   
    )

# 모든 ORM 모델의 부모 클래스
# 나중에 Review 같은 테이블을 정의할 때 Base를 상속받음

Base = declarative_base()