import os
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Ensure /data directory exists
if not os.path.exists('/data'):
    os.makedirs('/data')

Base = declarative_base()

class EmailPattern(Base):
    __tablename__ = 'email_patterns'
    id = Column(Integer, primary_key=True)
    company_name = Column(String)
    domain = Column(String)
    pattern = Column(String)
    status = Column(String, default="unknown")  # New status column with default value

engine = create_engine('sqlite:///data/email_patterns.db')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
