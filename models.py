from sqlalchemy import Column, Integer, String
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
    def __repr__(self):
        return f'<Servant(id={self.id}, class_name={self.class_name}, name={self.name})>'
    def __str__(self):
        return f'The servant {self.name} of {self.class_name} class'