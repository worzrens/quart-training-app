from functools import wraps

from quart import request


def validate(*validators):
    def wrapper_with_args(f):
        @wraps(f)
        async def wrapper(*args, **kwargs):
            try:
                print("WRAPPER ARGS ", validators, kwargs.get("id"), await request.get_json())

                for validator in validators:
                    validator(id = kwargs.get("id") if kwargs is not None else None, request_data = await request.get_json())

                return await f(*args, **kwargs)
            except Exception as e:
                return e.info
        return wrapper
    return wrapper_with_args