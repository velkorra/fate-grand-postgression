from fastapi import File, Form, UploadFile
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from typing import Optional

class BaseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True
    )


class ServantResponse(BaseSchema):
    id: int
    name: str
    class_name: str
    ascension_level: int
    level: int
    alignment: str
    gender: str
    state: str


class ServantAndName(ServantResponse):
    true_name: Optional[str] = None

class ServantWithLocalization(ServantResponse):
    localizations : list["LocalizationResponse"]


class LocalizationResponse(BaseSchema):
    language: str
    name: Optional[str]
    description: Optional[str]
    history: Optional[str]
    prototype_person: Optional[str]
    illustrator: Optional[str]
    voice_actor: Optional[str]
    temper: Optional[str]
    intro: Optional[str]

class ServantUpdate(BaseSchema):
    name: Optional[str] = None
    class_name: Optional[str] = None
    ascension_level: Optional[int] = None
    level: Optional[int] = None
    gender: Optional[str] = None
    alignment: Optional[str] = None


class ServantCreate(BaseModel):
    name: str
    class_name: str
    gender: str
    alignment: str


class MasterCreate(BaseModel):
    nickname: str
    display_name: str = None


class MasterUpdate(BaseModel):
    nickname: str = None
    display_name: str = None
    level: int = None


class ContractCreate(BaseModel):
    master_id: int
    servant_id: int


class ContractUpdate(BaseModel):
    master_id: int
    servant_id: int
    add_spells: int = 0


class CreatePicture(BaseModel):
    grade: int
    picture: UploadFile


class NoblePhantasmUpdate(BaseModel):
    servant_id: int
    rank: str
    activation_type: str
    name: str
    description: str


class SkillSchema(BaseModel):
    id: int
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
