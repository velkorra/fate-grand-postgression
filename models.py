from typing import List
from sqlalchemy import Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .database import Base

class Master(Base):
    __tablename__ = "master"
    id : Mapped[int] = mapped_column(Integer, primary_key=True)
    nickname : Mapped[str] = mapped_column(String, nullable=False)
    level : Mapped[str] = mapped_column(Integer, nullable=False)
    date_registered : Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    display_name : Mapped[str] = mapped_column(String)
    contracts : Mapped[List["Contract"]] = relationship("Contract", back_populates="master")
    def __repr__(self):
        return f'<Master(id={self.id}, nickname={self.nickname})>'

class Servant(Base):
    __tablename__ = "servant"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    class_name: Mapped[str] = mapped_column("class", String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    ascension_level: Mapped[int] = mapped_column(Integer, nullable=False)
    level: Mapped[int] = mapped_column(Integer, nullable=False)
    state : Mapped[str] = mapped_column(String)
    alignment : Mapped[str] = mapped_column(String)
    gender : Mapped[int] = mapped_column(String)
    
    noble_phantasm : Mapped["NoblePhantasm"] = relationship("NoblePhantasm", back_populates="servant")
    localizations : Mapped[List["ServantLocalization"]] = relationship("ServantLocalization", back_populates="servant")
    aliases : Mapped[List["Alias"]] = relationship("Alias", back_populates="servant")
    contracts : Mapped[List["Contract"]] = relationship("Contract", back_populates="servant")
    skills : Mapped[List["ServantSkill"]] = relationship("ServantSkill", back_populates="servant", lazy="select")

    def __repr__(self):
        return self._repr('id', 'class_name', 'name', 'ascension_level', 'level', 'state', 'alignment', 'gender')
    def __str__(self):
        return f'The servant {self.name} of {self.class_name} class'

class ServantPicture(Base):
    __tablename__ = "servant_picture"
    servant_id : Mapped[int] = mapped_column(Integer, primary_key=True)
    grade : Mapped[int] = mapped_column(Integer, primary_key=True)
    image : Mapped[str] = mapped_column(String)

    
class Alias(Base):
    __tablename__ = "alias"
    id : Mapped[int] = mapped_column(Integer, primary_key=True)
    language_code : Mapped[str] = mapped_column(String, nullable=False)
    name : Mapped[str] = mapped_column(String, nullable=False)
    servant_id : Mapped[int] = mapped_column(Integer, ForeignKey("servant.id"), nullable=False)
    servant : Mapped["Servant"] = relationship("Servant", back_populates="aliases")

class NoblePhantasm(Base):
    __tablename__ = "noble_phantasm"
    servant_id : Mapped[int] = mapped_column(Integer, ForeignKey("servant.id"), primary_key=True)
    rank : Mapped[str] = mapped_column(String)
    activation_type : Mapped[str] = mapped_column("type", String)
    name_ru : Mapped[str] = mapped_column(String)
    name_en : Mapped[str] = mapped_column(String)
    description_ru : Mapped[str] = mapped_column(Text)
    description_ru : Mapped[str] = mapped_column(Text)
    servant : Mapped["Servant"]= relationship("Servant", back_populates="noble_phantasm")

    
class Contract(Base):
    __tablename__ = "contract"
    master_id : Mapped[int] = mapped_column(Integer, ForeignKey("master.id"), primary_key=True)
    servant_id : Mapped[int] = mapped_column(Integer, ForeignKey("servant.id"), primary_key=True)
    status : Mapped[str] = mapped_column(String, nullable=False)
    start_date : Mapped[DateTime] = mapped_column(DateTime)
    end_date : Mapped[DateTime] = mapped_column(DateTime)
    command_spells : Mapped[int] = mapped_column(Integer)
    master : Mapped["Master"] = relationship("Master", back_populates="contracts")
    servant : Mapped["Servant"] = relationship("Servant", back_populates="contracts")
    
class ServantLocalization(Base):
    __tablename__ = 'servant_localization'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    language: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(Text)
    history: Mapped[str] = mapped_column(Text)
    prototype_person: Mapped[str] = mapped_column(Text)
    illustrator: Mapped[str] = mapped_column(Text)
    voice_actor: Mapped[str] = mapped_column(Text)
    temper: Mapped[str] = mapped_column(Text)
    intro : Mapped[str] = mapped_column(Text)
    servant_id: Mapped[int] = mapped_column(Integer, ForeignKey('servant.id'), nullable=False)
    servant: Mapped["Servant"] = relationship("Servant", back_populates="localizations")
    
class Skill(Base):
    __tablename__ = "skill"
    id : Mapped[int] = mapped_column(Integer, primary_key=True)
    skill_type : Mapped[str] = mapped_column("type", String)
    servants : Mapped[List["ServantSkill"]] = relationship("ServantSkill", back_populates="skill")
    rank : Mapped[str] = mapped_column(String)
    name_ru : Mapped[str] = mapped_column(String)
    name_en : Mapped[str] = mapped_column(String)
    description_ru : Mapped[str] = mapped_column(Text)
    description_en : Mapped[str] = mapped_column(Text)
    icon : Mapped[str] = mapped_column(String)
    def __str__(self):
        return self.skill_type
    
class ServantSkill(Base):
    __tablename__ = "servant_skill"
    servant_id : Mapped[int] = mapped_column(Integer, ForeignKey("servant.id"), primary_key=True)
    skill_id : Mapped[int] = mapped_column(Integer, ForeignKey("skill.id"), primary_key=True)
    servant : Mapped["Servant"] = relationship("Servant", back_populates="skills")
    skill : Mapped["Skill"] = relationship("Skill", back_populates="servants")