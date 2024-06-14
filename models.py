from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .database import Base

class Master(Base):
    __tablename__ = "master"
    id = Column(Integer, primary_key=True)
    nickname = Column(String, nullable=False)
    def __repr__(self):
        return f'<Master(id={self.id}, nickname={self.nickname})>'

class Servant(Base):
    __tablename__ = "servant"
    id = Column(Integer, primary_key=True)
    class_name = Column("class", String, nullable=False)
    name = Column(String, nullable=False)
    ascension_level = Column(Integer, nullable=False)
    level = Column(Integer, nullable=False)
    def __repr__(self):
        return f'<Servant(id={self.id}, class_name={self.class_name}, name={self.name}, ascension_level={self.ascension_level}, level={self.level})>'
    def __str__(self):
        return f'The servant {self.name} of {self.class_name} class'
    
class Contract(Base):
    __tablename__ = "contract"
    id = Column(Integer, primary_key=True)
    master_id = Column(Integer, ForeignKey("master.id"), nullable=False)
    servant_id = Column(Integer, ForeignKey("servant.id"), nullable=False)
    master = relationship("Master")
    servant = relationship("Servant")
    status = Column(String, nullable=False)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    command_spells = Column(Integer)