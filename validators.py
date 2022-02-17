import models
import model_types

class ValidationError(Exception):
    def __init__(self, msg, details = None, code = 400):
        self.msg = str(msg)
        self.details = details
        self.code = code

    def __str__(self):
        return self.msg
    
    @property
    def info(self):
        error_data = {
             "error": self.msg,
        }
        if self.details:
            error_data["details"] = self.details

        return error_data, self.code

def validate_empty_search_criteria(data):
    if not data:
        raise ValidationError('No search criteria provided')

def validate_search_criterias(data):
    unknown_columns = []
    
    for [k, v] in data.items():
        if k not in models.Switch.__table__.columns.keys():
            unknown_columns.append(k)
    if unknown_columns:    
        raise ValidationError('Unknown search criteria columns', details=unknown_columns)

def validate_switch_enum(data):
    type = data.get('type')
    if type and not model_types.SwitchType.has(type):
        raise ValidationError('Provided switch type does not exist')


def validate_switch_exists(id, is_exists):
    if not is_exists(models.Switch, {'id': id}):
        raise ValidationError('Switch with provided id does not exist', code=404)
        

def validate_switch_already_created(is_already_exists):
    if is_already_exists:
        raise ValidationError('Object with provided parameters already exists', code=400)


