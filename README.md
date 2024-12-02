
# 회의 저장 시스템 (AWS EC2 + RDS + S3)

## 📌 프로젝트 개요
이 프로젝트는 FastAPI 프레임워크를 사용하여 구축되었으며, 다음과 같은 주요 기능을 제공합니다.

### ✨ 주요 기능
- 📝 회의 정보와 관련 파일(WAV 및 TXT 파일) 저장
- 🔍 저장된 회의 정보 및 파일 조회
- ✏️ 특정 회의 정보 수정 및 삭제
- 🗑️ 모든 회의 정보 삭제

### 서버주소
- 프론트엔드: ***

- 백엔드: ***


## 

## Backend API 목록

```http
GET /
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `none` | `none` | 서버 상태를 확인하는 기본 엔드포인트 |

### 회의 정보 저장

```http
POST /meetings/save-record/
```

| Parameter          | Type                   | Description                                  |
| :----------------- | :--------------------- | :------------------------------------------- |
| `company_name`     | `string`               | 회사 이름                                    |
| `meeting_name`     | `string`               | 회의 이름                                    |
| `meeting_datetime` | `string` (ISO 8601)    | 회의 날짜 및 시간 (예: `2023-01-01T12:00:00Z`) |
| `wav_file`         | `file`                 | 업로드할 WAV 형식의 오디오 파일               |
| `summary_txt_file` | `file`                 | 업로드할 텍스트 요약 파일                     |
| `whole_meeting_txt_file` | `file`           | 업로드할 전체 회의 텍스트 파일                |

`예제 코드: https://github.com/chanever/meeting_db/blob/master/backend/test/save_record_test.py`



### 회의 정보 조회

```http
GET /meetings/get-record/{meeting_id}
```

| Parameter    | Type      | Description                        |
| :----------- | :-------- | :--------------------------------- |
| `meeting_id` | `integer` | 특정 회의 정보를 조회하기 위한 ID  |

- **설명**: 특정 회의 정보를 조회합니다.
- **응답**: 요청한 회의 정보 레코드를 Json 형식으로 반환합니다.

### 전체 회의 정보 조회
```http
GET /meetings/get-all-records/
```

#### 
| Parameter | Type   | Description                |
| :-------- | :----- | :------------------------- |
| `none`    | `none` | 요청에 필요한 매개변수 없음 |

- **설명**: 저장된 모든 회의 정보를 조회합니다.
- **응답**: 모든 회의 정보를 리스트 형식으로 반환합니다.

### 회의 정보 수정

```http
PUT /meetings/update-record/{meeting_id}
```

| Parameter          | Type         | Description                 |
| :----------------- | :----------- | :-------------------------- |
| `meeting_id`       | `integer`    | 수정할 회의 정보를 식별하는 ID |
| `company_name`     | `string`     | 수정할 회사 이름            |
| `meeting_name`     | `string`     | 수정할 회의 이름            |
| `meeting_datetime` | `string` (ISO 8601) | 수정할 회의 날짜 및 시간 (예: `2023-01-01T12:00:00Z`) |

- **설명**: 특정 회의 정보를 수정합니다.
- **응답**: 수정 완료 메시지를 반환합니다.


### 회의 정보 삭제

```http
DELETE /meetings/delete-record/{meeting_id}
```

| Parameter    | Type      | Description                        |
| :----------- | :-------- | :--------------------------------- |
| `meeting_id` | `integer` | 삭제할 회의 정보를 식별하는 ID      |

- **설명**: 특정 회의 정보와 관련 파일을 삭제합니다.
- **응답**: 삭제 완료 메시지를 반환합니다.

```http
DELETE /meetings/delete-all-records/
```

| Parameter | Type   | Description                |
| :-------- | :----- | :------------------------- |
| `none`    | `none` | 요청에 필요한 매개변수 없음 |

- **설명**: 모든 회의 정보와 관련 파일을 삭제합니다.
- **응답**: 모든 데이터 삭제 완료 메시지를 반환합니다.
