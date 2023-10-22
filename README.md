# Synergy FastAPI Server

이 프로젝트는 Synergy 서비스의 추천 로직을 위한 FastAPI 서버입니다.

## 로컬 도커 컨테이너 환경 설정

로컬 Docker 컨테이너 환경에서 MySQL과 연결하려면 다음 단계를 따르세요:

1. **로컬 MySQL 서버 시작**: 먼저, 로컬 MySQL 서버를 시작하세요.

2. **`.env` 파일 생성**: 프로젝트 루트에 `.env` 파일을 만듭니다. 파일 내용은 다음과 같습니다:

```
SQLALCHEMY_DATABASE_URL=mysql+pymysql://{user}:{password}@{host}:{port}/{database}
```

- `{user}`, `{password}`, `{port}`, `{database}`는 각각의 환경에 맞게 대체합니다.
- Mac 또는 Windows에서 로컬 환경의 MySQL에 연결하려면 `{host}`를 `host.docker.internal`로 설정합니다.

3. **Docker 이미지 빌드 및 컨테이너 실행**:

```bash
docker build -t myimage .
docker run -d --name mycontainer -p 80:80 myimage
```

**주의: .env 파일을 포함한 도커 이미지를 공개 저장소에 업로드하지 마세요. 내부 민감한 정보가 노출될 수 있습니다.**

이제 브라우저에서 [http://127.0.0.1/docs](http://127.0.0.1/docs) 주소로 접속하면 Swagger UI를 볼 수 있습니다.
