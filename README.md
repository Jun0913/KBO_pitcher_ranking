### Flask + Elasticsearch 기반 KBO 투수 시즌별 랭킹 서비스

KBO(한국 프로야구) 투수의 시즌별 성적 데이터를 **Elasticsearch**에 저장하고,  
**시즌 / 팀 / 지표** 조건에 따라 **TOP 20 랭킹**을 제공하는 내부용 웹 서비스입니다.

- 지원 시즌: **2024, 2025**
- 대상: 내부 사용자 (5명 이하)
- 인증: 없음 (로그인/회원가입 미구현)
- 목적: 지표 기반 투수 랭킹 조회 및 데이터 분석

---

## 📌 주요 기능 (Features)

- 시즌 선택: **2024 / 2025**
- 팀 선택:
  - **전체(All)**: 리그 전체 기준 TOP 20
  - **특정 팀**: 해당 팀 내부 기준 TOP 20
- 다양한 투수 지표 기반 랭킹 제공  
  (ERA, WHIP, SO, WPCT, AVG 등)
- 테이블 헤더 클릭 정렬
  - 클릭 시 오름차순 / 내림차순 토글
  - 현재 정렬 지표에 ▲/▼ 표시
  - 정렬 중인 컬럼 하이라이트
- 컬럼 좌/우 전환 버튼
  - 화면에 표시되지 않는 지표를 화살표 버튼으로 전환
- 지표 툴팁
  - 지표에 마우스를 올리면 **한글 설명 표시**
- 순위 계산 방식
  - **RANK 방식**
  - 동점 처리 예: `1, 2, 2, 4, 5, 5, 7 ...`
- Elasticsearch 오류 / 데이터 없음 상황 처리
  - 서비스 중단 없이 사용자에게 안내 메시지 출력

---

## ⚾ 규정 이닝 (IP ≥ 100) 적용 규칙

특정 지표는 **규정이닝(100이닝 이상)** 기준으로 랭킹을 계산합니다.

### 적용 지표
- `ERA`
- `WPCT`
- `WHIP`
- `AVG`

### 적용 조건
- **팀 = 전체(All)**  
  → 위 지표 조회 시 **IP ≥ 100** 투수만 포함
- **팀 = 특정 팀 선택 시**  
  → 규정이닝 제한 없이 해당 팀 투수 전체 포함

### 기본 첫 화면
- `/` 접속 시 자동 적용 조건:
  - 시즌: **2025**
  - 팀: **전체(All)**
  - 지표: **ERA**
  - 정렬: **오름차순**
  - 규정이닝: **IP ≥ 100**

---

## 🛠 기술 스택 (Tech Stack)

- Backend: **Flask (Python)**
- Search / Storage: **Elasticsearch 7.10.1**
- Dashboard (선택): **Kibana 7.10.1**
- Deployment: **Docker / Docker Compose**
- Python ES Client: `elasticsearch-py` (low-level)

---

## 📁 프로젝트 구조

kbo_pitcher_ranking/
├─ app.py
├─ config.py
├─ requirements.txt
├─ services/
│ └─ es_service.py
├─ templates/
│ └─ rankings.html
├─ static/
│ ├─ css/
│ └─ js/
└─ docker/
├─ Dockerfile
└─ docker-compose.yml

---

## 📦 Requirements

`requirements.txt`

Flask==3.0.3
elasticsearch==7.10.1
gunicorn==21.2.0
python-dotenv==1.0.1
pandas==2.2.3
openpyxl==3.1.5

---

## ⚙️ Environment Variables

`.env`

```env
ES_HOSTS=http://elasticsearch:9200
ES_INDEX=kbo_pitcher_stats

🚀 실행 방법 (Docker 권장)
1️⃣ 컨테이너 실행
cd docker
docker compose up -d --build
2️⃣ 접속 정보
Flask Web: http://localhost:9941

Elasticsearch: http://localhost:9200

Kibana: http://localhost:5602

📊 데이터 적재 (Excel → Elasticsearch)
투수 성적 데이터는 엑셀 파일 KBO_pitcher.xlsx 를 사용합니다.

엑셀 구조
2024 시트 → 2024 시즌 투수 성적

2025 시트 → 2025 시즌 투수 성적

엑셀 데이터를 pandas + openpyxl로 읽어
Elasticsearch 인덱스 kbo_pitcher_stats 에 적재합니다.

🔗 주요 라우트
GET /
기본 랭킹 페이지

기본 조건(2025 / 전체 / ERA / 규정이닝) 자동 조회

GET /rankings
쿼리 파라미터 예시:

/rankings?season=2025&team=all&metric=era&sort_dir=asc
sort_dir 미지정 시 지표 특성에 따른 기본 방향 적용

ERA / WHIP / AVG → 오름차순

그 외 지표 → 내림차순

⚠️ 에러 처리
Elasticsearch 연결 오류 발생 시

서버 중단 없이 에러 메시지 UI 표시

조회 결과가 없는 경우

“해당 조건에 맞는 데이터가 없습니다” 안내 메시지 표시

📈 확장 아이디어 (Roadmap)
JSON API 제공 (/api/rankings)

선수명 검색 기능

Kibana 대시보드 기반 시즌/팀별 통계 시각화

자주 사용되는 쿼리 캐싱

랭킹/정렬 로직 단위 테스트 추가
