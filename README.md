# Synergy FastAPI Server

이 프로젝트는 Synergy 서비스의 추천 로직을 위한 FastAPI 서버입니다.

## 프로젝트 개요

Synergy는 팀 프로젝트 소셜 네트워크 서비스입니다. 본 서버는 Synergy 서비스 내에서 추천 시스템을 처리하며, 사용자에게 가장 관련성 있는 콘텐츠를 제공합니다.

## 추천 시스템

### 추천 모델: LightFM

LightFM은 협업 필터링과 콘텐츠 기반 필터링을 결합한 하이브리드 추천 모델입니다. 사용자와 아이템 간의 상호작용 데이터 뿐만 아니라, 사용자 및 아이템의 특성 데이터도 사용하여 추천을 수행합니다. 이를 통해 사용자가 아직 상호작용하지 않은 새로운 아이템에 대해서도 효과적으로 추천할 수 있습니다(콜드 스타트 대응).

### 학습 과정

1. 서버 시작 시 유저/아이템 특성 및 상호작용 데이터를 데이터베이스에서 가져옵니다.
2. 가져온 데이터를 바탕으로 LightFM 모델을 학습시킵니다.

### 학습 요청 시

- 마지막 학습한 이후 새 데이터를 DB에서 가져와 LightFM 모델을 이어서 학습시킵니다.

### 추천 요청 시

- 사용자에게 포스트를 추천합니다. 이때, 사용자와 포스트 간의 상호작용 점수를 계산하여 가장 높은 점수를 가진 포스트를 추천합니다.

### 목표

현재는 협업 필터링 방식만 적용되어 있으며, 사용자와 포스트 간의 상호작용 데이터만을 사용하여 추천을 수행합니다.

다음 단계로는 사용자 특성을 모델에 포함시켜 추천 결과의 향상 및 비슷한 사용자 목록을 추출할 수 있도록 개선할 계획입니다.

최종적으로는 포스트의 텍스트 임베딩 평균을 구해 이를 포스트 특성으로 하여 추천 모델을 학습시키고 비슷한 포스트 목록을 추출할 수 있도록 예정입니다.

## 기술 스택

- **FastAPI**: 웹 서버 및 API 구축
- **LightFM**: 추천 알고리즘 구현
- **SQLAlchemy**: 데이터베이스 ORM

## API 엔드포인트

- **/fit_model**: 모델을 새로운 데이터로 학습시킵니다.
- **/recommend/posts/{user_id}**: 특정 사용자에 대한 추천 포스트를 제공합니다.
- **/recommend/projects/{user_id}**: 특정 사용자에 대한 추천 프로젝트를 제공합니다.

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

MIT
