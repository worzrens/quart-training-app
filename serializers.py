from marshmallow_sqlalchemy import SQLAlchemySchema
from marshmallow_enum import EnumField

from flask_marshmallow import Marshmallow
from main import app
import models
import model_types


ma = Marshmallow(app)

class SwitchSchema(SQLAlchemySchema):
    class Meta:
        model = models.Switch

    id = ma.auto_field()
    color = ma.auto_field()
    type = EnumField(model_types.SwitchType)
    company = ma.auto_field()


switch_schema = SwitchSchema()
switches_schema = SwitchSchema(many=True)