from pydantic import BaseModel
from typing import Optional

class ServantUpdate(BaseModel):
    name : Optional[str]=None
    class_name : Optional[str] =None   
    ascension_level : Optional[int] =None   
    level : Optional[int]=None
