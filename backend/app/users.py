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
    current_user.location = from_shape(Point(lon, lat), srid=4326)
    db.commit()
    return {"msg": "Location updated"}


@router.get("/nearby", response_model=list[schemas.UserOut])
def get_nearby(
    radius_km: float = 50,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db),
):
    if not current_user.location:
        raise HTTPException(status_code=400, detail="Set your location first")
    radius_m = radius_km * 1000
    distance_col = func.ST_Distance(models.User.location, current_user.location).label(
        "distance"
    )
    users_with_dist = (
        db.query(models.User, distance_col)
        .filter(
            models.User.id != current_user.id,
            func.ST_DWithin(models.User.location, current_user.location, radius_m),
        )
        .order_by(distance_col)
        .all()
    )
    return [u for u, _ in users_with_dist]
