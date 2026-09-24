from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy.ext.declarative import declarative_base


# PostgreSQL SETUP Link  jahid@2026J
SQLALCHEMY_DATABASE_URL = 'postgresql://postgres.xlsqshgxgovaycexhway:jahid@2026J@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres'


# MYSQL SETUP LINK
# SQLALCHEMY_DATABASE_URL = 'mysql+pymysql://root:12345678@127.0.0.1:3306/todoapplecation'

# SQLALCHEMY_DATABASE_URL = 'sqlite:///./todosapp.db'
# engine = create_engine(SQLALCHEMY_DATABASE_URL, 
#     connect_args={"check_same_thread": False})

engine = create_engine(SQLALCHEMY_DATABASE_URL)

sessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

Base = declarative_base()