# CamperCircle - Backend


## start
```
docker-compose up --build
```

## clean all volumes
```
docker-compose down -v
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
