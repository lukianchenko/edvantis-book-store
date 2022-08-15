from datetime import datetime

from sqlalchemy.orm.collections import InstrumentedList

"""
Simple DB models serialization
"""


def serialize(model_object):
    if type(model_object) == list or type(model_object) == InstrumentedList:
        json_list = []
        for item in model_object:
            json_list.append({c.name: getattr(item, c.name) for c in item.__table__.columns if c.name != "password"})
        return json_list
    else:
        return {c.name: getattr(model_object, c.name) for c in model_object.__table__.columns if c.name != "password"}


def add_data_to_instance(field, data_list, model):
    if len(data_list) > 0:
        for item in data_list:
            model_object = model.query.filter_by(id=item.get("id", None)).first()
            field.append(model_object)


def add_bulk_data_to_instance(field, data_list, model):
    if len(data_list) > 0:
        model_objects = model.query.filter(model.id.in_(data_list)).all()
        if len(model_objects) > 0:
            for _ in model_objects:
                field.append(_)


def serialize_date(date):
    serialized_date = datetime.strptime(date, "%Y-%m-%d")
    return serialized_date
