# Synergy FastAPI Server

이 프로젝트는 Synergy 서비스의 추천 로직을 위한 FastAPI 서버입니다.

## 프로젝트 개요

Synergy는 팀 프로젝트 소셜 네트워크 서비스입니다. 본 서버는 Synergy 서비스 내에서 추천 시스템을 처리하며, 사용자에게 가장 관련성 있는 콘텐츠를 제공합니다.

## 추천 로직 소개

이 서버는 LightFM을 기반으로 합니다. 실시간 데이터 업데이트를 통해 사용자의 활동에 따라 추천이 지속적으로 최신화됩니다.

## 테크놀로지 스택

- **FastAPI**: 웹 서버 및 API 구축.
- **LightFM**: 추천 알고리즘 구현.
- **SQLAlchemy**: 데이터베이스 ORM.

## API 엔드포인트 설명

- **/fit_model/**: 모델을 새로운 데이터로 학습시킵니다.
- **/recommend/{user_id}**: 특정 사용자에 대한 추천 콘텐츠를 제공합니다.

## 데이터베이스 스키마

## 로컬 환경 테스트 방법

### 로컬 MySQL 서버 시작

먼저, 로컬 MySQL 서버를 시작하세요.

### `.env` 파일 생성

프로젝트 루트에 `.env` 파일을 만듭니다. 파일 내용은 다음과 같습니다:

```
SQLALCHEMY_DATABASE_URL=mysql+pymysql://{user}:{password}@{host}:{port}/{database}
```

- `{user}`, `{password}`, `{port}`, `{database}`는 각각의 환경에 맞게 대체합니다.
- Mac 또는 Windows에서 로컬 환경의 MySQL에 연결하려면 `{host}`를 `host.docker.internal`로 설정합니다.

### Docker 이미지 빌드 및 컨테이너 실행

```bash
docker build -t myimage .
docker run -d --name mycontainer -p 80:80 myimage
```

**주의: .env 파일을 포함한 도커 이미지를 공개 저장소에 업로드하지 마세요. 내부 민감한 정보가 노출될 수 있습니다.**

이제 브라우저에서 [http://127.0.0.1/docs](http://127.0.0.1/docs) 주소로 접속하면 Swagger UI를 볼 수 있습니다.

## 라이센스
