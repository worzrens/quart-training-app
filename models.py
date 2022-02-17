from sqlalchemy import Column, Enum, Integer, String
import db_utils
import model_types


class Switch(db_utils.Base):
    __tablename__ = 'switches'

    id = Column(Integer, primary_key=True)
    color = Column(String(80), nullable=False)
    type = Column(Enum(model_types.SwitchType), nullable=False)
    company = Column(String(120), nullable=False)

    def __repr__(self):
        return f'<{self.company}> {self.color}'