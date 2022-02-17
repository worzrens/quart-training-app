import models
import model_types
import db_utils

def populate_db():
    db_utils.recreate_db_schema()

    mock_switches = [
        models.Switch(color='Red', type=model_types.SwitchType.linear, company='MX Cherry'),
        models.Switch(color='Silver', type=model_types.SwitchType.linear, company='MX Cherry'),
        models.Switch(color='Black', type=model_types.SwitchType.linear, company='MX Cherry'),

        models.Switch(color='Brown', type=model_types.SwitchType.tactile, company='MX Cherry'),
        models.Switch(color='Clear', type=model_types.SwitchType.tactile, company='MX Cherry'),
        models.Switch(color='Gray', type=model_types.SwitchType.tactile, company='MX Cherry'),

        models.Switch(color='Blue', type=model_types.SwitchType.clicky, company='MX Cherry'),
        models.Switch(color='Green', type=model_types.SwitchType.clicky, company='MX Cherry'),
        models.Switch(color='White', type=model_types.SwitchType.clicky, company='MX Cherry'),

        models.Switch(color='Purple', type=model_types.SwitchType.tactile, company='Zealios'),
        models.Switch(color='Orange', type=model_types.SwitchType.linear, company='Zealios'),
    ]
    db_utils.session.bulk_save_objects(mock_switches)
    db_utils.session.commit()
    return True