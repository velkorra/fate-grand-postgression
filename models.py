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
    contracts : Mapped[List["Contract"]] = relationship("Contract", back_populates="master")
    display_name : Mapped[str] = mapped_column(String)
    def __repr__(self):
        return f'<Master(id={self.id}, nickname={self.nickname})>'

class Servant(Base):
    __tablename__ = "servant"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    class_name: Mapped[str] = mapped_column("class", String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    ascension_level: Mapped[int] = mapped_column(Integer, nullable=False)
    level: Mapped[int] = mapped_column(Integer, nullable=False)
    localizations : Mapped[List["ServantLocalization"]] = relationship("ServantLocalization", back_populates="servant")
    contracts : Mapped[List["Contract"]] = relationship("Contract", back_populates="servant")
    def __repr__(self):
        return f'<Servant(id={self.id}, class_name={self.class_name}, name={self.name}, ascension_level={self.ascension_level}, level={self.level})>'
    def __str__(self):
        return f'The servant {self.name} of {self.class_name} class'
    
class Contract(Base):
    __tablename__ = "contract"
    id : Mapped[int] = mapped_column(Integer, primary_key=True)
    master_id : Mapped[int] = mapped_column(Integer, ForeignKey("master.id"), nullable=False)
    servant_id : Mapped[int] = mapped_column(Integer, ForeignKey("servant.id"), nullable=False)
    master : Mapped[Master] = relationship("Master", back_populates="contracts")
    servant : Mapped[Servant] = relationship("Servant", back_populates="contracts")
    status : Mapped[str] = mapped_column(String, nullable=False)
    start_date : Mapped[DateTime] = mapped_column(DateTime)
    end_date : Mapped[DateTime] = mapped_column(DateTime)
    command_spells : Mapped[int] = mapped_column(Integer)
    
class ServantLocalization(Base):
    __tablename__ = 'servant_localization'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    language: Mapped[str] = mapped_column(String(10), nullable=False)
    name: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(Text)
    history: Mapped[str] = mapped_column(Text)
    prototype_person: Mapped[str] = mapped_column(Text)
    illustrator: Mapped[str] = mapped_column(Text)
    voice_actor: Mapped[str] = mapped_column(Text)
    temper: Mapped[str] = mapped_column(Text)
    servant_id: Mapped[int] = mapped_column(Integer, ForeignKey('servant.id'), nullable=False)
    servant: Mapped["Servant"] = relationship("Servant", back_populates="localizations")