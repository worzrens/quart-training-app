import json
import quart.flask_patch
import enum
from quart import Quart, request
from marshmallow_sqlalchemy import SQLAlchemySchema
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_marshmallow import Marshmallow
from marshmallow_enum import EnumField

user='psql_user'
password='1'
host='localhost'
port='5432'
database='quart-app'
DATABASE_CONNECTION_URI = f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}'

app = Quart(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_CONNECTION_URI
engine = create_engine(DATABASE_CONNECTION_URI)
db = SQLAlchemy(app)
ma = Marshmallow(app)
Session = sessionmaker(engine)

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

class Switch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    color = db.Column(db.String(80), unique=True, nullable=False)
    type = db.Column(db.Enum(SwitchType), nullable=False)
    company = db.Column(db.String(120), nullable=False)

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
    db.drop_all()
    db.create_all()

    with Session() as session:
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
        print("QWEWQE", model.query.filter_by(**args).all())
        print("YYYYY", model.query.filter_by(**args).exists())
        print("ZZZZZ", session.query(
            model.query.filter_by(**args).exists()
            ).scalar()
            )

        return session.query(
            model.query.filter_by(**args).exists()
            ).scalar()

@app.route('/switches/<int:id>')
async def switches_get(id):
    switch = Switch.query.get(id)
    return switch_schema.dump(switch)

@app.route('/switches')
async def switches_list():
    switches = Switch.query.all()
    return {
        "switches": switches_schema.dump(switches), 
    }

@app.route('/switches', methods=["POST"])
async def switches_create():
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

    with Session() as session:
        if not request_errors: 
            new_switch = Switch(color=color, type=SwitchType.get(type), company=company)
            session.add(new_switch)
            session.commit()
            return switch_schema.dump(new_switch)

    return {
        "errors": request_errors 
    }, 400

@app.route('/populate', methods=["POST"])
async def populate():
    print('Started population')
    is_done = fill_db()
    print(f'Finished population {is_done}')
    print(Switch.query.all())
    return 'Completed', 201


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)