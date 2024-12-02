import os, sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from main import app
from dotenv import load_dotenv

load_dotenv()

client = TestClient(app)

meeting_id = 1
update_data = {
    "company_name": "Updated Company",
    "meeting_name": "Updated Meeting",
    "meeting_datetime": "2024-01-01T15:00:00"
}

print("=" * 50)
print("업데이트 요청 데이터:")
print(f"Meeting ID: {meeting_id}")
print(f"Update Data: {update_data}")

response = client.put(
    f"http://{os.getenv('API_HOST')}:{os.getenv('API_PORT')}/meetings/update-record/{meeting_id}",
    data=update_data
)

print("\n응답 결과:")
print(f"Status Code: {response.status_code}")
response_data = response.json()
print(f"\n메시지: {response_data['message']}")
print("=" * 50)
