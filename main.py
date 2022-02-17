from quart import Quart, request
import db_utils
import populate_db
import serializers
import model_types
import models

from validators import validate_empty_search_criteria, validate_search_criterias, validate_switch_already_created, validate_switch_enum, validate_switch_exists


app = Quart(__name__)


def is_exists(model, args):
    return db_utils.session.query(
        db_utils.session.query(model).filter_by(**args).exists()
        ).scalar()

@app.route('/switches/search', methods=["POST"])
async def switch_search():
    try:
        data = await request.get_json()
        
        validate_empty_search_criteria(data)
        validate_search_criterias(data, models.Switch)
        validate_switch_enum(data, model_types.SwitchType)

        filtered_switches = db_utils.session.query(models.Switch).filter_by(**data).all()            
        return {
            'result': serializers.switches_schema.dump(filtered_switches)
            }

    except Exception as e:
        return e.info


@app.route('/switches/<int:id>')
async def switch_retreive(id):
    try:
        validate_switch_exists(id, is_exists)

        switch = db_utils.session.query(models.Switch).get(id)
        return serializers.switch_schema.dump(switch)

    except Exception as e:
        return e.info

@app.route('/switches/<int:id>', methods=["PATCH"])
async def switch_partial_update(id):
    try:
        data = await request.get_json()

        validate_switch_exists(id, is_exists)
        validate_switch_enum(data)

        switch = db_utils.session.query(models.Switch).filter(models.Switch.id == id)
        switch.update(data)        
        db_utils.session.commit()

        return serializers.switch_schema.dump(switch.first())

    except Exception as e:
        return e.info

@app.route('/switches/<int:id>', methods=['DELETE'])
async def switch_remove(id):
    try:
        validate_switch_exists(id, is_exists)

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
async def switch_create():
    try:
        data = await request.get_json()
        color = data.get('color')
        type = data.get('type')
        company = data.get('company')
        
        validate_switch_enum(data)
        validate_switch_already_created(is_exists(models.Switch, {"color": color, "type": model_types.SwitchType.get(type), "company": company}))

        new_switch = models.Switch(color=color, type=model_types.SwitchType.get(type), company=company)
        db_utils.session.add(new_switch)
        db_utils.session.commit()
        return serializers.switch_schema.dump(new_switch), 201
    
    except Exception as e:
        return e.info

@app.route('/populate', methods=["POST"])
async def populate():
    app.add_background_task(populate_db.populate_db())
    return 'Population job has started', 201


if __name__ == "__main__":
    db_utils.create_db_schema()
    app.run(debug=True)