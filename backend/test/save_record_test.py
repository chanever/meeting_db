import os, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from main import app
from dotenv import load_dotenv

load_dotenv()
client = TestClient(app)

def test_save_record():
    test_data = {
        "company_name": "테스트 회사",
        "meeting_name": "테스트 회의",
        "meeting_datetime": "2024-01-01T10:00:00"
    }
    wav_path = str(Path(__file__).parent / "test.wav")
    txt_path = str(Path(__file__).parent / "test.txt")
    
    with open(wav_path, "rb") as wav_file, \
         open(txt_path, "rb") as whole_meeting_txt_file, \
         open(txt_path, "rb") as summary_txt_file:
        response = client.post(
            f"http://{os.getenv('API_HOST')}:{os.getenv('API_PORT')}/meetings/save-record/",
            data=test_data,
            files={
                "wav_file": ("test.wav", wav_file, "audio/wav"),
                "whole_meeting_txt_file": ("test.txt", whole_meeting_txt_file, "text/plain"),
                "summary_txt_file": ("test.txt", summary_txt_file, "text/plain")
            }
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.json() if response.status_code != 422 else response.text}")
        
        if response.status_code == 200 and response.json() == {"message": "회의 정보가 성공적으로 저장되었습니다."}:
            print("테스트 성공!")
        else:
            print("테스트 실패!")

if __name__ == "__main__":
    test_save_record()
