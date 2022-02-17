import enum


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