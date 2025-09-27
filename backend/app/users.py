from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from sqlalchemy import func
from . import schemas, database, models, auth

router = APIRouter(tags=["users"])
oauth2_scheme = auth.oauth2_scheme


@router.get("/me", response_model=schemas.UserOut)
def read_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user


@router.post("/location")
def update_location(
    lat: float,
    lon: float,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db),
):
    # Converts (lat, lon) into a PostGIS point (EPSG:4326, WGS84 GPS coordinates).
    current_user.location = from_shape(Point(lon, lat), srid=4326)
    db.commit()
    return {"msg": "Location updated"}


@router.get("/nearby", response_model=list[schemas.NearbyUser])
def get_nearby(
    radius_km: float = 50,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db),
):
    if not current_user.location:
        raise HTTPException(status_code=400, detail="Set your location first")
    radius_m = radius_km * 1000

    # Compute distance column in meters
    distance_col = func.ST_Distance(models.User.location, current_user.location).label(
        "distance"
    )

    # Query users within radius, exclude current user
    users_with_dist = (
        db.query(models.User, distance_col)
        .filter(
            models.User.id != current_user.id,
            func.ST_DWithin(models.User.location, current_user.location, radius_m),
        )
        .order_by(distance_col)
        .all()
    )

    # Build response list
    results: list[schemas.NearbyUser] = []
    for user, distance_m in users_with_dist:
        # Step 1: map SQLAlchemy User -> UserOut (from_attributes=True for Pydantic v2)
        user_out = schemas.UserOut.model_validate(user, from_attributes=True)
        # Step 2: build NearbyUser by adding distance_km
        nearby_user = schemas.NearbyUser(
            **user_out.model_dump(),  # dumps dictionary and unpacks (**) it
            distance_km=distance_m / 1000,
        )
        results.append(nearby_user)

    return results
