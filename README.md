# Synergy FastAPI Server

이 프로젝트는 Synergy 서비스의 추천 로직을 위한 FastAPI 서버입니다.

## 프로젝트 개요

Synergy는 팀 프로젝트 소셜 네트워크 서비스입니다. 본 서버는 Synergy 서비스 내에서 추천 시스템을 처리하며, 사용자에게 가장 관련성 있는 콘텐츠를 제공합니다.

## 추천 과정

### 1. 데이터 모델 ([models.py](https://github.com/TeamSynergyy/synergy-backend-fastapi/blob/main/app/models.py))

- `User`: 사용자를 나타내며, 사용자의 포스트, 댓글, 좋아요를 관계로 가지고 있습니다.
- `Post`: 포스트를 나타내며, 포스트를 작성한 사용자, 포스트에 달린 댓글, 포스트에 달린 좋아요를 관계로 가지고 있습니다.
- `Comment`: 댓글을 나타내며, 댓글을 작성한 사용자와 댓글이 달린 포스트를 관계로 가지고 있습니다.
- `PostLike`: 포스트 좋아요를 나타내며, 좋아요를 누른 사용자와 좋아요가 달린 포스트를 관계로 가지고 있습니다.

### 2. 데이터베이스 상호작용 ([crud.py](https://github.com/TeamSynergyy/synergy-backend-fastapi/blob/main/app/crud.py))

- `get_new_creates`: 새로 생성된 포스트를 데이터베이스에서 가져옵니다.
- `get_new_commented`: 새로 달린 댓글을 데이터베이스에서 가져옵니다.
- `get_new_liked`: 새로 달린 좋아요를 데이터베이스에서 가져옵니다.

### 3. 추천 모델 ([main.py](https://github.com/TeamSynergyy/synergy-backend-fastapi/blob/main/app/main.py))

- LightFM 모델을 사용하여 추천을 수행합니다.
- `fit_model`: 새로운 상호작용 데이터를 모델에 학습시킵니다.
- `recommend_to_user`: 주어진 사용자에게 포스트를 추천합니다.

### 추천 과정

1. 새로운 포스트, 댓글, 좋아요 데이터를 데이터베이스에서 가져옵니다.
2. 가져온 데이터를 바탕으로 LightFM 모델을 학습시킵니다.
3. 사용자에게 포스트를 추천합니다. 이때, 사용자와 포스트 간의 상호작용 점수를 계산하여 가장 높은 점수를 가진 포스트를 추천합니다.

현재는 협업 필터링 방식만 적용되어 있으며, 사용자와 포스트 간의 상호작용 데이터만을 사용하여 추천을 수행합니다. 다음 단계로는 사용자 특성을 모델에 포함시켜 추천 결과의 향상을 도모하고, 비슷한 사용자 목록을 추출할 수 있도록 개선할 계획입니다. 최종적으로는 한국어 포스트의 형태소 분석 결과를 사용하여 포스트의 특성을 추출하고, 이를 바탕으로 추천 모델을 학습시킬 예정입니다.

현재 사용하고 계신 플랜은 무료 플랜으로, 요청 횟수에 제한이 있습니다. 요청 횟수를 늘리려면 [여기](https://c7d59216ee8ec59bda5e51ffc17a994d.auth.portal-pluginlab.ai/pricing)에서 유료 플랜을 확인해보세요.

## 기술 스택

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
