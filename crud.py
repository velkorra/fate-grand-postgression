from sqlalchemy.orm import Session, aliased
from sqlalchemy.exc import IntegrityError
from .models import *

class ServantService:
    def __init__(self, db : Session):
        self.db = db
    
    def get(self, id : int) -> Servant:
        return self.db.query(Servant).get(id)
    
    def get_all(self):
        return self.db.query(Servant).all()
    
    def get_details(self, id : int):
        localizations = self.get(id).localizations        
        return {localization.language: localization for localization in localizations}
    
    def get_aliases():
        pass
    
    def get_full_servant(self, id : int):
        servant = self.get(id)
        localizations = self.get_details(id)
    
    def add_localization(self):
        details = ServantLocalization(language='ru', description="_____---_____")
        s = self.get(8)
        s.localizations.append(details)
        self.db.commit()
        
        
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
        
    def join(self, id : int = None):
        ru_loc = aliased(ServantLocalization)
        en_loc = aliased(ServantLocalization)

        query = self.db.query(
            Servant.id,
            Servant.class_name,
            Servant.name,
            Servant.ascension_level,
            Servant.level,
            ru_loc.name.label('name_ru'),
            ru_loc.description.label('description_ru'),
            ru_loc.history.label('history_ru'),
            ru_loc.prototype_person.label('prototype_person_ru'),
            ru_loc.illustrator.label("illustrator_ru"),
	        ru_loc.voice_actor.label("voice_actor_ru"),
            en_loc.name.label('name_en'),
            en_loc.description.label('description_en'),
            en_loc.history.label('history_en'),
            en_loc.prototype_person.label('prototype_person_en'),
            en_loc.illustrator.label("illustrator_en"),
	        en_loc.voice_actor.label("voice_actor_en"),
        ).outerjoin(
            ru_loc, (Servant.id == ru_loc.servant_id) & (ru_loc.language == 'ru')
        ).outerjoin(
            en_loc, (Servant.id == en_loc.servant_id) & (en_loc.language == 'en')
        )
        if id == None:
            result = query.all()
        else:
            result = [query.filter(Servant.id == id).first()]
        # print(query.statement.compile(compile_kwargs={"literal_binds": True}))
        response =  [{"servant_id": q.id,
                "class": q.class_name,
                "name_ru": q.name_ru,
                "description_ru": q.description_ru,
                "history_ru": q.history_ru,
                "prototype_person_ru": q.prototype_person_ru,
                "illustrator_ru": q.illustrator_ru,
                "voice_actor_ru": q.voice_actor_ru,
                "name_en": q.name_en,
                "description_en": q.description_en,
                "history_en": q.history_en,
                "prototype_person_en": q.prototype_person_en,
                "illustrator_en": q.illustrator_en,
                "voice_actor_en": q.voice_actor_en,
                } for q in result]
        return response if id == None else response[0]
    
    def get_skills(self, id : int):
        servant = self.get(id)
        return servant.skills
        
    

        
class ContractService:
    def __init__(self, db : Session):
        self.db = db
    
    def get(self, id):
        return self.db.query(Contract).get(id)
    
    def get_all(self):
        return self.db.query(Contract).all()

class MasterService:
    def __init__(self, db : Session):
        self.db = db
    
    def get(self, id):
        return self.db.query(Master).get(id)
    
    def get_all(self):
        return self.db.query(Master).all()