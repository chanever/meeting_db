import os, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from main import app
from dotenv import load_dotenv

load_dotenv()

client = TestClient(app)

meeting_id = 1

response = client.get(
    f"http://{os.getenv('API_HOST')}:{os.getenv('API_PORT')}/meetings/get-record/{meeting_id}"
)

print("\n=== 회의 정보 조회 결과 ===")
print(f"상태 코드: {response.status_code}")

response_data = response.json()
print(f"\n메시지: {response_data['message']}")

if response_data['data'] is None:
    print("\n=== 회의 상세 정보 ===")
    print(response_data['message'])
else:
    print("\n=== 회의 상세 정보 ===")
    record = response_data['data']
    print(f"회의 ID: {record['id']}")
    print(f"회사명: {record['company_name']}")
    print(f"회의명: {record['meeting_name']}")
    print(f"회의 일시: {record['meeting_datetime']}")
    print(f"WAV 파일: {record['wav_url']}")
    print(f"회의 요약 텍스트: {record['summary_txt_url']}")
    print(f"전체 회의 텍스트: {record['whole_meeting_txt_url']}")
    print(f"생성일: {record['created_at']}")
    print(f"수정일: {record['updated_at']}")
    print("=" * 50)
