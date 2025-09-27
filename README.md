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

## Test Data

10 coordinates, 1 km apart eastward:

Latitude Longitude Email Password Name
52.5200	13.4050 aaa@gmail.com 123 Aaa
52.5200	13.4186 bbb@gmail.com 123 Bbb
52.5200	13.4322 ccc@gmail.com 123 Ccc
52.5200	13.4458
52.5200	13.4594
52.5200	13.4730
52.5200	13.4866
52.5200	13.5002
52.5200	13.5138
52.5200	13.5274
