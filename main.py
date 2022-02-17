from quart import Quart, request
import db_utils
from decorators import validate
import populate_db
import serializers
import model_types
import models

from validators import IS_EMPTY_SEARCH_CRITERIA, IS_SEARCH_CRITERIA_CORRECT, IS_SWITCH_ALREADY_CREATED, IS_SWITCH_TYPE_CORRECT, IS_SWITCH_EXISTS


app = Quart(__name__)


@app.route('/switches/search', methods=["POST"])
@validate(IS_EMPTY_SEARCH_CRITERIA, IS_SEARCH_CRITERIA_CORRECT, IS_SWITCH_TYPE_CORRECT)
async def switch_search():
    try:
        data = await request.get_json()

        filtered_switches = db_utils.session.query(models.Switch).filter_by(**data).all()            
        return {
            'result': serializers.switches_schema.dump(filtered_switches)
            }

    except Exception as e:
        return e.info


@app.route('/switches/<int:id>')
@validate(IS_SWITCH_EXISTS)
async def switch_retreive(id):
    try:

        switch = db_utils.session.query(models.Switch).get(id)
        return serializers.switch_schema.dump(switch)

    except Exception as e:
        return e.info

@app.route('/switches/<int:id>', methods=["PATCH"])
@validate(IS_SWITCH_EXISTS, IS_SWITCH_TYPE_CORRECT)
async def switch_partial_update(id):
    try:
        data = await request.get_json()

        switch = db_utils.session.query(models.Switch).filter(models.Switch.id == id)
        switch.update(data)        
        db_utils.session.commit()

        return serializers.switch_schema.dump(switch.first())

    except Exception as e:
        return e.info

@app.route('/switches/<int:id>', methods=['DELETE'])
@validate(IS_SWITCH_EXISTS)
async def switch_remove(id):
    try:
        switch = db_utils.session.query(models.Switch).get(id)
        db_utils.session.delete(switch)
        db_utils.session.commit()

        return {
            "success": True,
            "id": id
        }

    except Exception as e:
        return e.info

@app.route('/switches')
async def switches_list():
    switches = db_utils.session.query(models.Switch).all()
    return {
        "switches": serializers.switches_schema.dump(switches), 
    }

@app.route('/switches', methods=["POST"])
@validate(IS_SWITCH_TYPE_CORRECT, IS_SWITCH_ALREADY_CREATED)
async def switch_create():
    try:
        data = await request.get_json()
        color = data.get('color')
        type = data.get('type')
        company = data.get('company')

        new_switch = models.Switch(color=color, type=model_types.SwitchType.get(type), company=company)
        db_utils.session.add(new_switch)
        db_utils.session.commit()

        return serializers.switch_schema.dump(new_switch), 201
    
    except Exception as e:
        return e.info

@app.route('/populate', methods=["POST"])
async def populate():
    print("Adding population job")
    app.add_background_task(populate_db.populate_db)
    print("Population job added")

    return 'Population job has started', 201


if __name__ == "__main__":
    db_utils.create_db_schema()
    app.run(debug=True)