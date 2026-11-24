# myAIEdu – 4050 AI 실전 입문

8주 커리큘럼 조회, 수강 신청 화면, API 문서 대시보드를 제공합니다.
백엔드(FastAPI)가 화면(`frontend/`)과 API를 **같은 주소**에서 함께 제공합니다.

## 폴더 구조

```
myAIEdu/
├── README.md
├── frontend/                 # 화면 (정적 HTML/CSS/JS)
│   ├── index.html
│   ├── css/style.css
│   └── js/
│       ├── app.js            # 과정·커리큘럼 조회, 입력 검사, 신청 API 호출
│       └── dashboard.js      # API 문서 & 실습 대시보드
└── backend/
    ├── run_practice.ps1      # 실습 모드 서버 실행 스크립트
    ├── requirements.txt
    ├── app/                  # FastAPI 앱 (routers → services → models)
    ├── scripts/seed_curriculum.py
    ├── tests/
    └── data/app.db           # SQLite (실습 모드에서는 쓰지 않음)
```

## 실습 모드로 실행 (팀원과 공유하는 서버)

실습 모드에서는 수강생 등록과 신청을 **검증만 하고 저장하지 않습니다.** 관리자의 상태 변경도 막힙니다.

```powershell
cd C:\Users\solli\Desktop\AI_myClaude\myReport\myAIEdu\backend
$env:PYTHON_EXE = "C:\Users\solli\AppData\Local\Programs\Python\Python312\python.exe"   # 필요할 때만
.\run_practice.ps1
```

- 이 PC에서 확인: `http://127.0.0.1:8000`
- 팀원 접속: `http://<이 PC의 IP>:8000` (같은 네트워크에서 접속)
- 공유 서버에 올릴 때도 같은 스크립트를 쓰면 `PRACTICE_MODE=1`이 항상 켜집니다.
- API 문서: `http://127.0.0.1:8000/docs`

## 개발 모드 (실제 저장)

```powershell
cd ...\myAIEdu\backend
py -3 -m uvicorn app.main:app --reload
```

이 모드에서는 신청이 `data/app.db`에 실제로 저장됩니다. 실습 공유 서버에는 쓰지 마세요.

## 테스트

```powershell
cd ...\myAIEdu\backend
py -3 -m pytest
```

## 설정 값 (환경 변수)

| 이름 | 기본값 | 설명 |
|---|---|---|
| `PRACTICE_MODE` | `0` | `1`이면 등록과 신청을 저장하지 않습니다. |
| `ADMIN_KEY` | (비어 있음) | 관리자 API 키. 비어 있으면 관리자 기능이 꺼집니다. |
| `CORS_ORIGINS` | (비어 있음) | 페이지를 다른 주소에서 따로 열 때만 출처를 쉼표로 적습니다. |
| `DATABASE_URL` | `data/app.db` | DB 주소. |

## 확인 필요 항목

- 커리큘럼과 수강료는 **백엔드 DB가 원본**입니다. 학습 목표와 수강료는 `backend/scripts/seed_curriculum.py`에 `[확인 필요]`로 표시되어 있고, 이미 입력된 DB는 스크립트를 다시 돌려도 바뀌지 않습니다. 확정 후에는 DB 값을 직접 고쳐야 합니다.
- `frontend/index.html`: 카카오톡 채널 주소
- 개인정보 수집 항목과 보관 기간(1년) 문구는 확정 후 다시 확인하세요.
