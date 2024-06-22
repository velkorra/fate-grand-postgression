from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    def _repr(self, *fields):
        attrs = ', '.join(f'{field}={repr(getattr(self, field))}' for field in fields)
        return f'<{self.__class__.__name__}({attrs})>'