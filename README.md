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
#	Latitude Longitude Email Password Name
1	52.5200	13.4050 aaa@gmail.com 123 Aaa
2	52.5200	13.4186 bbb@gmail.com 123 Bbb
3	52.5200	13.4322 ccc@gmail.com 123 Ccc
4	52.5200	13.4458
5	52.5200	13.4594
6	52.5200	13.4730
7	52.5200	13.4866
8	52.5200	13.5002
9	52.5200	13.5138
10	52.5200	13.5274
