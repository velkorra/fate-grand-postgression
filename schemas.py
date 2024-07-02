from fastapi import File, Form, UploadFile
from pydantic import BaseModel
from typing import Optional

class ServantUpdate(BaseModel):
    name : Optional[str] = None
    class_name : Optional[str] = None
    ascension_level : Optional[int] = None
    level : Optional[int] = None
    gender : Optional[str] = None
    alignment : Optional[str] = None

    
class ServantCreate(BaseModel):
    name : str
    class_name : str
    gender : str
    alignment : str
    
class MasterCreate(BaseModel):
    nickname : str
    display_name : str = None

class MasterUpdate(BaseModel):
    nickname : str = None
    display_name : str = None
    level : int = None
    
class ContractCreate(BaseModel):
    master_id : int
    servant_id : int
    
class ContractUpdate(BaseModel):
    master_id : int
    servant_id : int
    add_spells : int = 0
    
    
class CreatePicture(BaseModel):
    grade : int
    picture : UploadFile
    
class ServantWithPicture(BaseModel):
    name : str = Form(...)
    class_name : str = Form(...)
    gender : str = Form(...)
    alignment : str = Form(...)
    file : UploadFile = File(...)
    

class NoblePhantasmUpdate(BaseModel):
    servant_id: int
    rank: str
    activation_type: str
    name: str
    description: str
    
class SkillSchema(BaseModel):
    id : int
    skill_type: str
    rank: str
    name: str
    description: str

class ClassLevelStats(BaseModel):
    class_name: str
    max_level: int
    min_level: int
    avg_level: float
    
    
class Localization(BaseModel):
    language: str
    name: str
    description: str

class ServantLocalizationResponse(BaseModel):
    servant_name: str
    localization_language: str
    localization_name: str
    localization_description: str
    
class ServantMasterResponse(BaseModel):
    servant_name: str
    localization_name: str
    master_nickname: str
    
class ServantDescriptionResponse(BaseModel):
    servant_name: str
    language: str
    description: str
    
class TopServantResponse(BaseModel):
    master_nickname: str
    servant_name: str
    servant_level: int
