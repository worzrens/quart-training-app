from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


user='psql_user'
password='1'
host='localhost'
port='5432'
database='quart-app'
DATABASE_CONNECTION_URI = f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}'

engine = create_engine(DATABASE_CONNECTION_URI)
Base = declarative_base()

Session = sessionmaker(bind=engine)
session = Session()

def create_db_schema():
    Base.metadata.create_all(engine)

def recreate_db_schema():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

def is_exists(model, args):
    return session.query(
        session.query(model).filter_by(**args).exists()
        ).scalar()