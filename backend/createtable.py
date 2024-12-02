from sqlalchemy import Column, Integer, String, DateTime, Text, inspect
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
from connectdb import engine

Base = declarative_base()

class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(100), nullable=False, default="미등록 회사", comment='회사명')
    meeting_name = Column(String(200), nullable=False, default="미등록 회의", comment='회의명')
    meeting_datetime = Column(DateTime, nullable=False, default=func.now(), comment='회의일시')
    wav_url = Column(String(500), nullable=False, default="AWS S3 WAV URL", comment='WAV 파일 S3 URL')
    summary_txt_url = Column(String(500), nullable=False, default="AWS S3 Summary TXT URL", comment='회의 요약 텍스트 파일 S3 URL')
    whole_meeting_txt_url = Column(String(500), nullable=False, default="AWS S3 Full TXT URL", comment='전체 회의 텍스트 파일 S3 URL')
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment='생성일시')
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment='수정일시')

def create_tables():
    try:
        inspector = inspect(engine)
        if "meetings" in inspector.get_table_names():
            print("테이블이 이미 존재합니다.")
            return
        
        Base.metadata.create_all(bind=engine)
        print("테이블 생성 완료!")
    except Exception as e:
        print("테이블 생성 실패:", str(e))

if __name__ == "__main__":
    create_tables()