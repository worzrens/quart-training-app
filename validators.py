from flask import request


def validate_empty_search_criteria(data, request_errors):
    if not data:
        request_errors.append('No search criteria provided')
    
    return request_errors

def validate_search_criterias(data, Switch, request_errors):
    unknown_columns = []
    
    for [k, v] in data.items():
        if k not in Switch.__table__.columns.keys():
            unknown_columns.append(k)
    if unknown_columns:
        request_errors.append(f"Unknown columns: {', '.join(unknown_columns)}")
    
    return request_errors

def validate_switch_enum(data, SwitchType, request_errors):
    type = data.get('type')
    if type and not SwitchType.has(type):
        request_errors.append('Provided switch type does not exist') 

    return request_errors