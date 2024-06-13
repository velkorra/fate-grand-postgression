from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .models import *


def get_servants(db: Session):
    servants = db.query(Servant).all()
    return [{
        "name": servant.name,
        "class": servant.class_name}
    for servant in servants]

def create_servant(db: Session, name : str, class_name : str):
    servant = Servant(name=name, class_name=class_name)
    try:
        db.add(servant)
        db.commit()
        db.refresh(servant)
        return servant
    except IntegrityError as e:
        db.rollback()
        raise ValueError("Servant with such class and name already exists")