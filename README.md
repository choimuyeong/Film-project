# Film Project

영화 검색, 리뷰 작성, AI 감성 분석을 제공하는 풀스택 프로젝트입니다.

- Frontend: React + TypeScript + TailwindCSS
- Backend: FastAPI + SQLAlchemy + Transformers + PyTorch
- External API: TMDB API
- Database: SQLite (기본 설정)

## 1. 프로젝트 구조

```text
Film-project/
├─ backend/
│  ├─ main.py
│  ├─ requirements.txt
│  ├─ routers/
│  ├─ services/
│  ├─ models/
│  └─ schemas/
└─ frontend/
   ├─ src/
   ├─ package.json
   ├─ requirements.txt
   └─ requirements-dev.txt
```

## 2. 사전 준비

1. Python 3.10 이상
2. Node.js 18 이상 + npm
3. TMDB API Key

## 3. Backend 실행 방법

### 3-1. 가상환경 생성 및 활성화

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3-2. 의존성 설치

```powershell
pip install -r requirements.txt
```

### 3-3. 환경변수 설정 (`backend/.env`)

```env
TMDB_API_KEY=your_tmdb_api_key
DATABASE_URL=sqlite:///./movie_review.db
```

### 3-4. 서버 실행

```powershell
uvicorn main:app --reload --port 8000
```

API 문서:
- Swagger UI: `http://localhost:8000/docs`

## 4. Frontend 실행 방법

### 4-1. 의존성 설치 (권장)

```powershell
cd ../frontend
npm install
```

### 4-2. requirements 파일로 설치 (선택)

런타임 패키지:

```powershell
Get-Content .\requirements.txt | ForEach-Object { npm install $_ }
```

개발 패키지:

```powershell
Get-Content .\requirements-dev.txt | ForEach-Object { npm install -D $_ }
```

### 4-3. 환경변수 설정 (`frontend/.env`)

```env
REACT_APP_API_URL=http://localhost:8000
```

### 4-4. 프론트 서버 실행

```powershell
npm start
```

접속 주소:
- Frontend: `http://localhost:3000`

## 5. 주요 API 엔드포인트

- `GET /movies/search?q={query}`: 영화 검색
- `GET /movies/{movie_id}`: 영화 상세 조회
- `GET /reviews/{movie_id}`: 리뷰 목록 조회
- `POST /reviews/`: 리뷰 생성 + 감성 분석 결과 저장
- `DELETE /reviews/{review_id}`: 리뷰 삭제
- `POST /sentiment/analyze`: 텍스트 감성 분석

## 6. GitHub 업로드 전 체크리스트

1. `node_modules`, `.venv`, DB 파일이 `.gitignore`에 포함되어 있는지 확인
2. `frontend/.env`, `backend/.env` 같은 민감정보 파일이 커밋되지 않았는지 확인
3. 아래 명령으로 동작 확인

```powershell
# backend
cd backend
uvicorn main:app --reload --port 8000

# frontend (새 터미널)
cd frontend
npm start
```

## 7. Docker 배포 (Vultr)

프로젝트는 `backend`와 `frontend`를 각각 이미지로 빌드한 뒤 `docker-compose`로 함께 구동합니다.

### 7-1. 서버에서 환경변수 파일 준비

`backend/.env.example`을 참고해 `backend/.env`를 생성하세요.

```env
TMDB_API_KEY=your_real_tmdb_key
DATABASE_URL=sqlite:///./movie_review.db
```

중요:
- `TMDB_API_KEY`는 절대 GitHub에 커밋하지 마세요.
- 실제 키는 서버(`Vultr`)의 `backend/.env`에만 저장하세요.

### 7-2. 빌드 및 실행

```bash
docker compose up -d --build
```

### 7-3. 상태 확인

```bash
docker compose ps
docker compose logs -f backend
docker compose logs -f frontend
```

접속:
- 웹 앱: `http://서버IP`

### 7-4. 중지/재시작

```bash
docker compose down
docker compose up -d
```

## 8. 라이선스

개인/학습용 프로젝트 기준으로 작성되었습니다. 필요 시 LICENSE 파일을 추가해 사용하세요.
