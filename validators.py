import models
import model_types
import db_utils

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


def IS_EMPTY_SEARCH_CRITERIA(**kwargs):
    if not kwargs.get("request_data"):
        raise ValidationError('No search criteria provided')


def IS_SEARCH_CRITERIA_CORRECT(**kwargs):
    unknown_columns = []
    
    for [k, v] in kwargs.get("request_data").items():
        if k not in models.Switch.__table__.columns.keys():
            unknown_columns.append(k)
    if unknown_columns:    
        raise ValidationError('Unknown search criteria columns', details=unknown_columns)


def IS_SWITCH_TYPE_CORRECT(**kwargs):
    type = kwargs.get("request_data").get('type')
    if type and not model_types.SwitchType.has(type):
        raise ValidationError('Provided switch type does not exist')


def IS_SWITCH_EXISTS(**kwargs):
    if not db_utils.is_exists(models.Switch, {'id': kwargs.get("id")}):
        raise ValidationError('Switch with provided id does not exist', code=404)
        

def IS_SWITCH_ALREADY_CREATED(**kwargs):
    if db_utils.is_exists(
        models.Switch,
        {
            "color": kwargs.get("request_data").get("color"),
            "type": model_types.SwitchType.get(kwargs.get("request_data").get("type")),
            "company": kwargs.get("request_data").get("company")
        }
    ):
        raise ValidationError(
            'Object with provided parameters already exists', code=400)
