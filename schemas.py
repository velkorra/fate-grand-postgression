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