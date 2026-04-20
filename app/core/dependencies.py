from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.services import Services


def get_services(db: Session = Depends(get_db)):
    return Services(db)