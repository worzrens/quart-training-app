import imp
import quart.flask_patch
from quart import Quart, jsonify
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base

user='psql_user'
password='1'
host='localhost'
port='5432'
database='quart-app'
DATABASE_CONNECTION_URI = f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}'


app = Quart(__name__)
engine = create_engine(DATABASE_CONNECTION_URI)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()

class Switch(Base):
    __tablename__ = 'switches'
    id = Column(Integer, primary_key=True)
    color = Column(String(80), unique=True, nullable=False)
    type = Column(String(120), unique=True, nullable=False)

    def __repr__(self):
        return '<Switch %r>' % self.color


@app.route('/')
async def hello():
    switches = db_session.query(Switch).all()
    print(switches)
    return '1'

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    app.run()