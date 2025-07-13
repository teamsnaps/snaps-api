# Snaps API

Snaps 소셜 네트워킹 서비스를 위한 RESTful API 백엔드입니다. Django REST Framework를 기반으로 구축된 확장 가능하고 모듈화된 백엔드 시스템입니다.

## 🚀 개요

Snaps API는 이미지 중심의 소셜 네트워킹 서비스를 위한 강력하고 확장 가능한 백엔드 시스템입니다. 사용자 관리, 게시물, 댓글, 좋아요, 팔로우 등 소셜 미디어 애플리케이션의 핵심 기능을 모두 제공합니다.

## ✨ 주요 기능

- **사용자 관리**: 인증, 회원가입, 프로필 관리
- **게시물**: 이미지 업로드, 편집, 삭제, 조회
- **소셜 기능**: 댓글, 좋아요, 팔로우, 컬렉션
- **알림**: 실시간 사용자 알림 시스템
- **검색**: 사용자, 태그, 게시물 검색

## 🔧 기술 스택

- **Django & Django REST Framework**: RESTful API 구현
- **PostgreSQL**: 주 데이터베이스
- **Redis**: 캐싱 및 비동기 작업
- **Celery**: 백그라운드 작업 처리
- **AWS S3**: 미디어 파일 저장
- **JWT**: 사용자 인증

## 📋 API 엔드포인트

API는 다음과 같은 주요 리소스를 제공합니다:

- `/api/users/` - 사용자 관리
- `/api/posts/` - 게시물 관리
- `/api/comments/` - 댓글 관리
- `/api/likes/` - 좋아요 기능
- `/api/notifications/` - 알림 관리
- `/api/follows/` - 팔로우 관계 관리
- `/api/collections/` - 게시물 컬렉션 관리

## 📦 앱 구조
```
snapsapi/ 
├── apps/ # Django 앱 모듈 
│ ├── users/ # 사용자 관리 
│ ├── posts/ # 게시물 관리 
│ ├── comments/ # 댓글 기능 
│ ├── likes/ # 좋아요 기능 
│ ├── notifications/ # 알림 시스템 
│ └── core/ # 공통 기능 
├── config/ # 설정 파일 
│ ├── settings/ # 환경별 설정 
│ ├── urls.py # URL 라우팅 
│ └── wsgi.py # WSGI 설정 
├── utils/ # 유틸리티 모듈 
├── manage.py # Django 관리 스크립트 
└── requirements/ # 환경별 의존성 패키지 
├── base.txt # 공통 패키지 
├── dev.txt # 개발용 패키지 
└── prod.txt # 프로덕션용 패키지
```

## 🛠️ 개발 환경 설정

### 사전 요구사항

- Python 3.8+
- PostgreSQL
- Redis
- 가상 환경 관리 도구 (venv, pyenv, pipenv 등)

### 설치 방법
bash
# 저장소 클론
git clone [https://github.com/your-organization/snaps-api.git](https://github.com/your-organization/snaps-api.git) cd snaps-api
# 가상 환경 생성 및 활성화
python -m venv venv source venv/bin/activate # Windows: venv\Scripts\activate
# 의존성 패키지 설치
pip install -r requirements/dev.txt
# 환경 변수 설정
cp .env.example .env
# .env 파일을 편집하여 필요한 환경 변수 설정
# 데이터베이스 마이그레이션
python manage.py migrate
# 개발 서버 실행
python manage.py runserver


## 🔌 외부 서비스 연동

Snaps API는 다음과 같은 외부 서비스와 연동됩니다:

- **Snaps Media Processor**: 이미지 처리 및 최적화
- **AWS S3**: 원본 이미지 저장
- **AWS CloudFront**: 최적화된 이미지 배포

## 🧪 테스트
bash
# 전체 테스트 실행
python manage.py test
# 특정 앱 테스트
python manage.py test apps.posts
# 커버리지 확인
coverage run --source='.' manage.py test coverage report


## 🚀 배포

프로젝트는 다음과 같은 환경에 배포할 수 있습니다:

- **개발 환경**: 로컬 개발 및 테스트
- **스테이징 환경**: 통합 테스트 및 QA
- **프로덕션 환경**: 실제 서비스 운영

각 환경에 대한 배포 스크립트와 설정은 `deployment/` 디렉토리에서 관리됩니다.

## 📈 모니터링 및 로깅

- **Sentry**: 오류 추적
- **Prometheus**: 메트릭 수집
- **Grafana**: 모니터링 대시보드
- **ELK Stack**: 로그 관리 (선택 사항)

## 🔒 보안

- JWT 기반 인증
- HTTPS 강제 적용
- CORS 설정
- 요청 속도 제한
- 민감한 데이터 암호화

## 📄 API 문서

API 문서는 Swagger UI를 통해 제공됩니다:

- 개발 환경: `http://localhost:8000/api/docs/`
- 스테이징 환경: `https://staging-api.snaps.example.com/api/docs/`
- 프로덕션 환경: `https://api.snaps.example.com/api/docs/`

## 📝 코드 스타일 및 품질

- **Black**: 코드 포맷팅
- **isort**: 임포트 정렬
- **Flake8**: 린팅
- **pre-commit**: 자동 코드 품질 검사

## 📊 데이터베이스 다이어그램

프로젝트의 데이터베이스 구조는 [여기](docs/database-diagram.png)에서 확인할 수 있습니다.

## 📜 라이센스

[MIT 라이센스](LICENSE)

## 🤝 기여하기

1. 이슈 생성 또는 기존 이슈 확인
2. 피처 브랜치 생성 (`git checkout -b feature/amazing-feature`)
3. 변경사항 커밋 (`git commit -m 'Add amazing feature'`)
4. 브랜치에 푸시 (`git push origin feature/amazing-feature`)
5. Pull Request 제출

## 📞 연락처

프로젝트 관리자: [ask4git@gmail.com]
