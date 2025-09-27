from fastapi import APIRouter, Depends, HTTPException, Query
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
    # Validate coordinates
    if not (-90 <= lat <= 90):
        raise HTTPException(
            status_code=400, detail="Latitude must be between -90 and 90"
        )
    if not (-180 <= lon <= 180):
        raise HTTPException(
            status_code=400, detail="Longitude must be between -180 and 180"
        )

    # Create a POINT as a Geography object (longitude first, then latitude)
    current_user.location = from_shape(Point(lon, lat), srid=4326)  # PostGIS Geography

    db.commit()
    db.refresh(current_user)  # Ensure the updated object is loaded

    return {
        "msg": "Location updated",
        "location": {
            "lat": lat,
            "lon": lon,
        },
    }


@router.get("/nearby", response_model=list[schemas.NearbyUser])
def get_nearby(
    radius_km: float = Query(50, ge=1, le=500),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db),
):
    if not current_user.location:
        raise HTTPException(status_code=400, detail="Set your location first")

    radius_m = radius_km * 1000  # convert km -> meters

    # Compute distance column (meters)
    distance_col = func.ST_Distance(models.User.location, current_user.location).label(
        "distance_m"
    )

    # Query nearby users with GIST index efficiency, limit + offset
    users_with_dist = (
        db.query(models.User, distance_col)
        .filter(
            models.User.id != current_user.id,
            func.ST_DWithin(models.User.location, current_user.location, radius_m),
        )
        .order_by(distance_col)
        .limit(limit)
        .offset(offset)
        .all()
    )

    results: list[schemas.NearbyUser] = []
    for user, distance_m in users_with_dist:
        user_out = schemas.UserOut.model_validate(user, from_attributes=True)
        nearby_user = schemas.NearbyUser(
            **user_out.model_dump(), distance_km=distance_m / 1000
        )
        results.append(nearby_user)

    return results
