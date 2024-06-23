from pydantic import BaseModel
from typing import Optional

class ServantUpdate(BaseModel):
    name : Optional[str] = None
    class_name : Optional[str] = None
    ascension_level : Optional[int] = None
    level : Optional[int] = None
    gender : Optional[str] = None
    alignment : Optional[str] = None
    class Config:
        from_attributes = True
    
    
class ServantCreate(BaseModel):
    name : str
    class_name : str
    gender : str
    alignment : str