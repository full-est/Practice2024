from config import DATABASE_URL
from sqlalchemy import Column, String, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

Base = declarative_base()
engine = create_engine(DATABASE_URL)
Session = sessionmaker(engine)
session = Session()


def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()


class Vacancy(Base):
    __tablename__ = "vacancies"
    id = Column(String, primary_key=True, unique=True)
    name = Column(String)
    experience = Column(String)
    employer = Column(String)
    employment = Column(String)
    salary = Column(String)
    area = Column(String)


Base.metadata.create_all(engine)
