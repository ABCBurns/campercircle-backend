# CamperCircle - Backend


## build

```bash
docker-compose up --build
```

clean
```bash
docker-compose down -v
```

## Test
MinIO WebUI = http://localhost:9001 (Login: minio/minio123)
FastAPI API = http://localhost:8000/docs

## API Tests
```bash
curl -X 'POST' \
  'http://localhost:8000/auth/register' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "email": "christoph.perick@gmail.com",
  "password": "123",
  "name": "Burns"
}'
```

## Source Tree

```
database.py - DB Verbindung + Session
models.py - User + Message + PostGIS Location
schemas.py - Pydantic Modelle
auth.py - JWT + Passwort Hashing + Token Verification
deps.py - Dependency Injection
utils.py -  MinIO Bucket & Client
main.py - FastAPI Endpoints: Profilbild, Location, Nearby, Chat
```
