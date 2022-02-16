import json
from typing import final
import quart.flask_patch
import enum
from quart import Quart, Response, request
from marshmallow_sqlalchemy import SQLAlchemySchema
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Enum, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from flask_marshmallow import Marshmallow
from marshmallow_enum import EnumField

from validators import validate_empty_search_criteria, validate_search_criterias, validate_switch_enum

user='psql_user'
password='1'
host='localhost'
port='5432'
database='quart-app'
DATABASE_CONNECTION_URI = f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}'

app = Quart(__name__)
engine = create_engine(DATABASE_CONNECTION_URI)
Base = declarative_base()
ma = Marshmallow(app)
Session = sessionmaker(bind=engine)
session = Session()


class SwitchType(enum.Enum):
    linear = 'Linear'
    tactile = 'Tactile'
    clicky = 'Clicky'

    @classmethod
    def has(cls, name):
        return name in cls.__members__
    
    @classmethod
    def get(cls, name):
        return cls[name] if cls.has(name) else None

class Switch(Base):
    __tablename__ = 'switches'

    id = Column(Integer, primary_key=True)
    color = Column(String(80), nullable=False)
    type = Column(Enum(SwitchType), nullable=False)
    company = Column(String(120), nullable=False)

    def __repr__(self):
        return f'<{self.company}> {self.color}'


class SwitchSchema(SQLAlchemySchema):
    class Meta:
        model = Switch

    id = ma.auto_field()
    color = ma.auto_field()
    type = EnumField(SwitchType)
    company = ma.auto_field()


switch_schema = SwitchSchema()
switches_schema = SwitchSchema(many=True)

def fill_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    mock_switches = [
        Switch(color='Red', type=SwitchType.linear, company='MX Cherry'),
        Switch(color='Silver', type=SwitchType.linear, company='MX Cherry'),
        Switch(color='Black', type=SwitchType.linear, company='MX Cherry'),

        Switch(color='Brown', type=SwitchType.tactile, company='MX Cherry'),
        Switch(color='Clear', type=SwitchType.tactile, company='MX Cherry'),
        Switch(color='Gray', type=SwitchType.tactile, company='MX Cherry'),

        Switch(color='Blue', type=SwitchType.clicky, company='MX Cherry'),
        Switch(color='Green', type=SwitchType.clicky, company='MX Cherry'),
        Switch(color='White', type=SwitchType.clicky, company='MX Cherry'),
    ]
    session.bulk_save_objects(mock_switches)
    session.commit()
    return True

def is_exists(model, args):
    with Session() as session:
        return session.query(
            session.query(model).filter_by(**args).exists()
            ).scalar()

@app.route('/switches/search', methods=["POST"])
async def switch_search():
    request_errors = []

    try:
        data = await request.get_json()
        
        validate_empty_search_criteria(data, request_errors)
        validate_search_criterias(data, Switch, request_errors)
        validate_switch_enum(data, SwitchType, request_errors)

        if not request_errors:
            filtered_switches = session.query(Switch).filter_by(**data).all()
            print("SHOULD RETURN")
            
            return {
                'result': switches_schema.dump(filtered_switches)
                }
        return {
            "errors": request_errors
        }, 400

    except Exception as e:
        return {
            "errors": [str(e) if e else 'Unknown error occured'] 
        }, 500


@app.route('/switches/<int:id>')
async def switch_retreive(id):
    switch = session.query(Switch).get(id)
    if switch:
        return switch_schema.dump(switch)

    return {
        "error": 'No switch found with provided id'
    }, 404
    
@app.route('/switches/<int:id>', methods=["PATCH"])
async def switch_partial_update(id):
    request_errors = []
    switch = session.query(Switch).filter(Switch.id == id)
    if not switch.first():
        request_errors.append('No switch found with provided id')

    data = await request.get_json()
    type = data.get('type')

    if type and not SwitchType.has(type):
        request_errors.append('Provided switch type does not exist') 

    session.query(Switch).filter(Switch.id == id).update(data)        
    session.commit()

    if not request_errors:
        return switch_schema.dump(switch.first())

    return {
        "errors": request_errors 
    }, 400


@app.route('/switches/<int:id>', methods=['DELETE'])
async def switch_remove(id):
    request_errors = []
    switch = session.query(Switch).get(id)
    if switch:
        session.delete(switch)
        session.commit()

        return {
            "success": True,
            "id": id
        }

    return {
        "error": 'No switch found with provided id'
    }, 404

@app.route('/switches')
async def switches_list():
    switches = session.query(Switch).all()
    return {
        "switches": switches_schema.dump(switches), 
    }

@app.route('/switches', methods=["POST"])
async def switch_create():
    request_errors = []

    data = await request.get_json()
    color = data.get('color')
    type = data.get('type')
    company = data.get('company')

    if not SwitchType.has(type):
       request_errors.append('Provided switch type does not exist') 

    is_switch_exists = is_exists(Switch, {"color": color, "type": SwitchType.get(type), "company": company})
    if is_switch_exists:
        request_errors.append('Object with provided parameters already exists')

    if not request_errors: 
        new_switch = Switch(color=color, type=SwitchType.get(type), company=company)
        session.add(new_switch)
        session.commit()
        return switch_schema.dump(new_switch), 201

    return {
        "errors": request_errors 
    }, 400

@app.route('/populate', methods=["POST"])
async def populate():
    print('Started population')
    is_done = fill_db()
    print(f'Finished population {is_done}')
    return 'Completed', 201


if __name__ == "__main__":
    Base.metadata.create_all(engine)
    app.run(debug=True)