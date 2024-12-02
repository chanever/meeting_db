import os, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from main import app
from dotenv import load_dotenv

load_dotenv()

client = TestClient(app)

response = client.delete(
    f"http://{os.getenv('API_HOST')}:{os.getenv('API_PORT')}/meetings/delete-all-records/"
)

response_data = response.json()

print("\n=== 모든 회의 정보 삭제 결과 ===")
print(f"상태 코드: {response.status_code}")
print(f"\n메시지: {response_data['message']}")
print("=" * 50)
