# english learning backend

## 導入ライブラリー

- Django (Web アプリケーションフレームワーク)
- Django Rest Framework (RESTful API フレームワーク)
- psycopg2-binary (PostgreSQL を操作するためのドライバー)
- drf-spectacular (OpenAPI ドキュメントジェネレーター)
- mypy (静的型検査ツール)
- black (自動コード整形ツール)
- isort (import 文を自動整形するツール)
- flake8 (静的コード解析ツール)

## Run

### Docker Compose

```sh
$ docker compose up --build
```

## Endpoints

| URL                     |               Purpose |
| :---------------------- | --------------------: |
| /api/schema/swagger-ui/ | Swagger documentation |
