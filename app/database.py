from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import logging

class FormatLog(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool | logging.LogRecord:
        return '[raw sql]' not in record


logging.basicConfig(
    filename='sqlalchemy.log',  # имя файла, куда будет записан лог
 # уровень логирования
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'  # форматирование сообщений
)
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    def _repr(self, *fields):
        attrs = ', '.join(f'{field}={repr(getattr(self, field))}' for field in fields)
        return f'<{self.__class__.__name__}({attrs})>' 
    

create_async_engine = create_async_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(
    bind=create_async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)



async def get_db():
    async with SessionLocal() as session:
        yield session