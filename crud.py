from sqlalchemy.orm import Session, aliased
from sqlalchemy.exc import IntegrityError, DataError, InternalError
from psycopg2.errors import CheckViolation, UniqueViolation, RaiseException, ForeignKeyViolation
from .models import *
from .schemas import *

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
        
        
    def create(self, servant : ServantCreate):
        servant = Servant(name=servant.name, class_name=servant.class_name, alignment=servant.alignment, gender=servant.gender)
        try:
            self.db.add(servant)
            self.db.commit()
            self.db.refresh(servant)
            return servant
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(str(e))
        except DataError as e:
            self.db.rollback()
            raise ValueError("Invalid data: " + str(e.orig)) from e

    def update(self, id: int, s: ServantUpdate):
        servant = self.get(id)
        if s.name:
            servant.name = s.name
        if s.class_name:
            servant.class_name = s.class_name
        if s.ascension_level:
            servant.ascension_level = s.ascension_level
        if s.level:
            servant.level = s.level
        if s.alignment:
            servant.alignment = s.alignment
        if s.gender:
            servant.gender = s.gender
        try:
            self.db.commit()
            self.db.refresh(servant)
            return servant
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(str(e))
        except Exception as e:
            self.db.rollback()
            raise ValueError(str(e))
    
    def delete(self, id : int):
        servant = self.get(id)
        if servant:
            self.db.delete(servant)
            self.db.commit()
        else:
            raise ValueError("Servant does not exist")
        
        
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
        
class MasterService:
    def __init__(self, db : Session):
        self.db = db
    
    def get(self, id) -> Master | None:
        return self.db.query(Master).get(id)
    
    def get_all(self):
        return self.db.query(Master).all()    

    def create(self, master : MasterCreate):
        new_master = Master(nickname=master.nickname, display_name=(master.display_name if master.display_name else master.nickname))
        self.db.add(new_master)
        try:
            self.db.commit()
            self.db.refresh(new_master)
            return new_master
        except IntegrityError as e:
            self.db.rollback()
            if isinstance(e.orig, UniqueViolation):
                raise ValueError("Master with this nickname already exists")

        except Exception as e:
            self.db.rollback()
            raise Exception(str(e))

    def update(self, id : int, master : MasterUpdate):
        m = self.get(id)
        if not m:
            raise ValueError("master does not exist")
        if master.nickname:
            m.nickname = master.nickname
        if master.level:
            m.level = master.level
        if master.display_name:
            m.display_name = master.display_name
        try:
            self.db.commit()
            self.db.refresh(m)
            return m
        except IntegrityError as e:
            self.db.rollback()
            if isinstance(e.orig, UniqueViolation):
                raise ValueError("Master with this nickname already exists")
            if isinstance(e.orig, CheckViolation):
                raise ValueError("Level must be positive")
                
    def delete(self, id : int):
        m = self.get(id)
        if not m:
            raise ValueError("master does not exist")
        self.db.delete(m)
        self.db.commit()
    
class ContractService:
    def __init__(self, db : Session):
        self.db = db
    
    def get(self, servant_id, master_id):
        return self.db.query(Contract).filter(Contract.servant_id == servant_id and Contract.master_id == master_id)
    
    def get_all(self):
        return self.db.query(Contract).all()
    
    def create(self, contract_create : ContractCreate):
        contract = Contract(servant_id = contract_create.servant_id, master_id = contract_create.master_id)
        self.db.add(contract)
        try:    
            self.db.commit()
            self.db.refresh(contract)
            return contract
        except IntegrityError as e:
            self.db.rollback()
            if isinstance(e.orig, UniqueViolation):
                raise ValueError("Contract already exist")
            if isinstance(e.orig, ForeignKeyViolation):
                if "contract_master_id_fkey" in str(e):
                    raise ValueError("Master does not exist")
                else:
                    raise ValueError("Servant does not exist")
        except InternalError as e:
            self.db.rollback()
            if isinstance(e.orig, RaiseException):
                raise ValueError("Servant already has an active contract")
                

    
    
