from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class EmailPattern(Base):
    __tablename__ = 'email_patterns'
    id = Column(Integer, primary_key=True)
    company_name = Column(String)
    domain = Column(String)
    pattern = Column(String)

engine = create_engine('sqlite:///email_patterns.db')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
