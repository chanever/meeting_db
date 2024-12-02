from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

from connectdb import SessionLocal, test_connection
from createtable import create_tables, Meeting

import boto3, os

ALLOWED_AUDIO_TYPES = {"audio/wav", "audio/x-wav"}
ALLOWED_TEXT_TYPES = {"text/plain"}

@asynccontextmanager
async def lifespan(app: FastAPI):
    test_connection()
    create_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        return {
            "status_code": 500,
            "message": "데이터베이스 연결 오류"
        }
    finally:
        db.close()

@app.get("/")
async def root():
    return {"message": "FastAPI 서버가 실행 중입니다"}

# 회의 정보 저장
@app.post("/meetings/save-record/")
async def insert_meeting_data(
    company_name: str = Form(...),
    meeting_name: str = Form(...),
    meeting_datetime: str = Form(...),
    wav_file: UploadFile = File(...),
    summary_txt_file: UploadFile = File(...),
    whole_meeting_txt_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    print("=" * 50)
    print("Request received:")
    print(f"Company Name: {company_name}")
    print(f"Meeting Name: {meeting_name}")
    print(f"Meeting Datetime: {meeting_datetime}")
    print(f"WAV file: {wav_file.filename} ({wav_file.content_type})")
    print(f"Summary TXT file: {summary_txt_file.filename} ({summary_txt_file.content_type})")
    print(f"Whole Meeting TXT file: {whole_meeting_txt_file.filename} ({whole_meeting_txt_file.content_type})")
    print("=" * 50)

    # 파일 타입 검증
    if wav_file.content_type not in ALLOWED_AUDIO_TYPES:
        return {
            "status_code": 400,
            "message": "WAV 파일만 업로드 가능합니다."
        }
    
    if summary_txt_file.content_type not in ALLOWED_TEXT_TYPES:
        return {
            "status_code": 400,
            "message": "요약 텍스트 파일만 업로드 가능합니다."
        }
    
    if whole_meeting_txt_file.content_type not in ALLOWED_TEXT_TYPES:
        return {
            "status_code": 400,
            "message": "전체 회의 텍스트 파일만 업로드 가능합니다."
        }

    try:
        meeting_datetime_obj = datetime.fromisoformat(meeting_datetime.replace('Z', '+00:00'))

        s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_DEFAULT_REGION')
        )
        bucket_name = os.getenv('AWS_S3_BUCKET_NAME')

        try:
            # WAV 파일 업로드
            wav_object = f'wav_files/{wav_file.filename}'
            wav_content = await wav_file.read()
            s3.put_object(Bucket=bucket_name, Key=wav_object, Body=wav_content)
            wav_url = f"https://{bucket_name}.s3.{os.getenv('AWS_DEFAULT_REGION')}.amazonaws.com/{wav_object}"

            # 요약 TXT 파일 업로드
            summary_txt_object = f'txt_files/summary_{summary_txt_file.filename}'
            summary_txt_content = await summary_txt_file.read()
            s3.put_object(Bucket=bucket_name, Key=summary_txt_object, Body=summary_txt_content)
            summary_txt_url = f"https://{bucket_name}.s3.{os.getenv('AWS_DEFAULT_REGION')}.amazonaws.com/{summary_txt_object}"

            # 전체 회의 TXT 파일 업로드
            whole_txt_object = f'txt_files/whole_{whole_meeting_txt_file.filename}'
            whole_txt_content = await whole_meeting_txt_file.read()
            s3.put_object(Bucket=bucket_name, Key=whole_txt_object, Body=whole_txt_content)
            whole_meeting_txt_url = f"https://{bucket_name}.s3.{os.getenv('AWS_DEFAULT_REGION')}.amazonaws.com/{whole_txt_object}"

        except boto3.exceptions.S3UploadFailedError as e:
            return {
                "status_code": 500,
                "message": f"S3 파일 업로드 중 오류가 발생했습니다: {str(e)}"
            }
        except boto3.exceptions.Boto3Error as e:
            return {
                "status_code": 500,
                "message": f"AWS S3 연결 중 오류가 발생했습니다: {str(e)}"
            }

        # DB에 저장
        meeting = Meeting(
            company_name=company_name,
            meeting_name=meeting_name,
            meeting_datetime=meeting_datetime_obj,
            wav_url=wav_url,
            summary_txt_url=summary_txt_url,
            whole_meeting_txt_url=whole_meeting_txt_url
        )
        
        db.add(meeting)
        db.commit()
        db.refresh(meeting)
        
        return {
            "message": "회의 정보가 성공적으로 저장되었습니다.",
        }
        
    except ValueError as e:
        return {
            "status_code": 400,
            "message": "잘못된 날짜 형식입니다. ISO 형식(YYYY-MM-DDTHH:MM:SS)으로 입력해주세요."
        }
    except SQLAlchemyError as e:
        db.rollback()
        return {
            "status_code": 500,
            "message": "데이터베이스 저장 중 오류가 발생했습니다."
        }
    except Exception as e:
        return {
            "status_code": 500,
            "message": f"파일 업로드 중 오류가 발생했습니다: {str(e)}"
        }

# 회의 정보 조회
@app.get("/meetings/get-record/{meeting_id}")
async def get_meeting(meeting_id: int, db: Session = Depends(get_db)):
    try:
        meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
        
        if not meeting:
            return {
                "message": "해당 ID의 회의 정보를 찾을 수 없습니다.",
                "data": None
            }
            
        meeting_data = {
            "id": meeting.id,
            "company_name": meeting.company_name,
            "meeting_name": meeting.meeting_name,
            "meeting_datetime": meeting.meeting_datetime.isoformat(),
            "wav_url": meeting.wav_url,
            "summary_txt_url": meeting.summary_txt_url,
            "whole_meeting_txt_url": meeting.whole_meeting_txt_url,
            "created_at": meeting.created_at.isoformat(),
            "updated_at": meeting.updated_at.isoformat()
        }
            
        return {
            "message": "회의 정보를 성공적으로 조회했습니다.",
            "data": meeting_data
        }
        
    except SQLAlchemyError as e:
        return {
            "status_code": 500,
            "message": "데이터베이스 조회 중 오류가 발생했습니다."
        }
    except Exception as e:
        return {
            "status_code": 500, 
            "message": f"회의 정보 조회 중 오류가 발생했습니다: {str(e)}"
        }

# 모든 회의 정보 조회
@app.get("/meetings/get-all-records/")
async def get_all_meetings(db: Session = Depends(get_db)):
    try:
        meetings = db.query(Meeting).all()
        
        meetings_list = []
        for meeting in meetings:
            meetings_list.append({
                "id": meeting.id,
                "company_name": meeting.company_name,
                "meeting_name": meeting.meeting_name,
                "meeting_datetime": meeting.meeting_datetime.isoformat(),
                "wav_url": meeting.wav_url,
                "summary_txt_url": meeting.summary_txt_url,
                "whole_meeting_txt_url": meeting.whole_meeting_txt_url,
                "created_at": meeting.created_at.isoformat(),
                "updated_at": meeting.updated_at.isoformat()
            })
            
        return {
            "message": "회의 정보를 성공적으로 조회했습니다.",
            "data": meetings_list
        }
        
    except SQLAlchemyError as e:
        return {
            "status_code": 500,
            "message": "데이터베이스 조회 중 오류가 발생했습니다."
        }
    except Exception as e:
        return {
            "status_code": 500,
            "message": f"회의 정보 조회 중 오류가 발생했습니다: {str(e)}"
        }

# 특정 회의 정보 수정
@app.put("/meetings/update-record/{meeting_id}")
async def update_meeting(
    meeting_id: int,
    company_name: str = Form(...),
    meeting_name: str = Form(...),
    meeting_datetime: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
        
        if not meeting:
            return {
                "status_code": 404,
                "message": "해당 ID의 회의 정보를 찾을 수 없습니다."
            }

        # 기본 정보 업데이트
        meeting.company_name = company_name
        meeting.meeting_name = meeting_name
        meeting.meeting_datetime = datetime.fromisoformat(meeting_datetime)
        meeting.updated_at = datetime.now()

        db.commit()

        return {
            "status_code": 200,
            "message": "회의 정보가 성공적으로 수정되었습니다."
        }

    except SQLAlchemyError as e:
        return {
            "status_code": 500,
            "message": f"데이터베이스 작업 중 오류가 발생했습니다: {str(e)}"
        }
    except Exception as e:
        return {
            "status_code": 500,
            "message": f"회의 정보 수정 중 오류가 발생했습니다: {str(e)}"
        }

# 특정 회의 정보 삭제
@app.delete("/meetings/delete-record/{meeting_id}")
async def delete_meeting(meeting_id: int, db: Session = Depends(get_db)):
    try:
        meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
        
        if not meeting:
            return {
                "status_code": 404,
                "message": "해당 ID의 회의 정보를 찾을 수 없습니다."
            }

        s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_DEFAULT_REGION')
        )
        bucket_name = os.getenv('AWS_S3_BUCKET_NAME')

        wav_key = meeting.wav_url.split(f"{bucket_name}.s3.{os.getenv('AWS_DEFAULT_REGION')}.amazonaws.com/")[1]
        s3.delete_object(Bucket=bucket_name, Key=wav_key)

        summary_txt_key = meeting.summary_txt_url.split(f"{bucket_name}.s3.{os.getenv('AWS_DEFAULT_REGION')}.amazonaws.com/")[1]
        s3.delete_object(Bucket=bucket_name, Key=summary_txt_key)

        whole_txt_key = meeting.whole_meeting_txt_url.split(f"{bucket_name}.s3.{os.getenv('AWS_DEFAULT_REGION')}.amazonaws.com/")[1]
        s3.delete_object(Bucket=bucket_name, Key=whole_txt_key)

        db.delete(meeting)
        db.commit()

        db.execute(text("ALTER TABLE meetings AUTO_INCREMENT = 1"))
        db.commit()

        return {
            "status_code": 200,
            "message": "회의 정보와 관련 파일들이 성공적으로 삭제되었습니다."
        }

    except SQLAlchemyError as e:
        return {
            "status_code": 500,
            "message": f"데이터베이스 작업 중 오류가 발생했습니다: {str(e)}"
        }
    except HTTPException as e:
        return {
            "status_code": e.status_code,
            "message": str(e.detail)
        }
    except Exception as e:
        return {
            "status_code": 500,
            "message": f"회의 정보 삭제 중 오류가 발생했습니다: {str(e)}"
        }

# 모든 회의 정보 삭제
@app.delete("/meetings/delete-all-records/")
async def delete_all_meetings(db: Session = Depends(get_db)):
    try:
        meetings = db.query(Meeting).all()
        
        if not meetings:
            return {"message": "삭제할 회의 정보가 없습니다."}

        s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_DEFAULT_REGION')
        )
        bucket_name = os.getenv('AWS_S3_BUCKET_NAME')

        for meeting in meetings:
            wav_key = meeting.wav_url.split(f"{bucket_name}.s3.{os.getenv('AWS_DEFAULT_REGION')}.amazonaws.com/")[1]
            s3.delete_object(Bucket=bucket_name, Key=wav_key)

            summary_txt_key = meeting.summary_txt_url.split(f"{bucket_name}.s3.{os.getenv('AWS_DEFAULT_REGION')}.amazonaws.com/")[1]
            s3.delete_object(Bucket=bucket_name, Key=summary_txt_key)

            whole_txt_key = meeting.whole_meeting_txt_url.split(f"{bucket_name}.s3.{os.getenv('AWS_DEFAULT_REGION')}.amazonaws.com/")[1]
            s3.delete_object(Bucket=bucket_name, Key=whole_txt_key)

        db.query(Meeting).delete()
        db.commit()

        db.execute(text("ALTER TABLE meetings AUTO_INCREMENT = 1"))
        db.commit()

        return {"message": "모든 회의 정보와 관련 파일들이 성공적으로 삭제되었습니다."}

    except SQLAlchemyError as e:
        return {
            "status_code": 500,
            "message": "데이터베이스 작업 중 오류가 발생했습니다."
        }
    except Exception as e:
        return {
            "status_code": 500,
            "message": f"회의 정보 삭제 중 오류가 발생했습니다: {str(e)}"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=3001, reload=True)