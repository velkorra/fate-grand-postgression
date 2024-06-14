from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .models import *

class ServantService:
    def __init__(self, db : Session):
        self.db = db
    
    def get(self, id):
        return self.db.query(Servant).get(id)
    
    def get_all(self):
        return self.db.query(Servant).all()

    def create(self, name : str, class_name : str):
        servant = Servant(name=name, class_name=class_name)
        try:
            self.db.add(servant)
            self.db.commit()
            self.db.refresh(servant)
            return servant
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError("Servant with such class and name already exists")

    def update(self, id : int, name : str = None, class_name : str = None, ascension_level : int = None, level : int = None):
        servant : Servant = self.db.query(Servant).get(id)
        if name:
            servant.name = name
        if class_name:
            servant.class_name = class_name
        if ascension_level:
            servant.ascension_level = ascension_level
        if level:
            servant.level = level
        try:
            self.db.commit()
            self.db.refresh(servant)
            return servant
        except Exception as e:
            raise ValueError(str(e))
        
class ContractService:
    def __init__(self, db : Session):
        self.db = db
    
    def get(self, id):
        return self.db.query(Contract).get(id)
    
    def get_all(self):
        return self.db.query(Contract).all()