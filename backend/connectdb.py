from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from os import environ
from dotenv import load_dotenv

load_dotenv()

HOST = environ.get('DB_HOST')
USER = environ.get('DB_USER')
PASSWORD = environ.get('DB_PASSWORD')
DATABASE = environ.get('DB_DATABASE')
PORT = int(environ.get('DB_PORT', 3306))

engine = create_engine(
    f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}",
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=3600,
    pool_pre_ping=True,
)

SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

def test_connection():
    try:
        with engine.connect() as connection:
            print("데이터베이스 연결 성공!")
    except Exception as e:
        print("데이터베이스 연결 실패:", str(e))
