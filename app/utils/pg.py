from sqlalchemy import select
from sqlalchemy.exc import ArgumentError
from sqlalchemy.sql.sqltypes import Boolean, Integer


class FilterBuilder:
    supported_ops = {
        "=": "__eq__",
        ">": "__gt__",
        ">=": "__ge__",
        "<": "__lt__",
        "<=": "__le__",
        "!=": "__ne__",
        "in": "in_",
        "not in": "notin_",
        "like": "like",
    }

    @classmethod
    def get_operator_method(cls, op):
        if op not in cls.supported_ops:
            raise Exception(f"{op} operator not supported.")

        return cls.supported_ops[op]

    @staticmethod
    def get_model_field(model, field):
        if not hasattr(model, field):
            raise Exception(f"Model has no attribute {field}.")

        return getattr(model, field)

    @staticmethod
    def transform_field_value(model_field, value, op):
        model_field_type = model_field.property.columns[0].type
        transform = str

        if type(model_field_type) is Integer:
            transform = int

        elif type(model_field_type) is Boolean:

            def transform_and_check(value):
                if value.lower() in ["0", "false"]:
                    return False
                elif value.lower() in ["1", "true"]:
                    return True

                raise Exception("Incorrect bool value.")

            transform = transform_and_check

        try:
            if op in ["in", "not in"]:
                transform_value = [transform(i) for i in value.split("|")]
            else:
                transform_value = transform(value)

            return transform_value
        except Exception:
            raise Exception(f"Value: {value} incorrect.")

    @classmethod
    def get_filter_by_field(cls, model, field: str, value: str, op: str):
        op_method = cls.get_operator_method(op)
        model_field = cls.get_model_field(model, field)
        transform_field_value = cls.transform_field_value(model_field, value, op)

        try:
            filter_ = getattr(model_field, op_method)(transform_field_value)
            return filter_
        except ArgumentError:
            raise Exception(f"Incorrect combination field: {field}, op: {op}.")

    @classmethod
    def get_filter(cls, model, fields: list, values: list, ops: list):
        for field, value, op in zip(fields, values, ops):
            yield cls.get_filter_by_field(model, field, value, op)


class OrderByBuilder:
    supported_direction = ["asc", "desc"]

    @classmethod
    def get_direction_method(cls, direction):
        if direction.strip().lower() not in cls.supported_direction:
            raise Exception(f"{direction} direction not supported.")

        return direction.strip().lower()

    @staticmethod
    def get_model_field(model, field):
        if not hasattr(model, field):
            raise Exception(f"Model has no attribute {field}.")

        return getattr(model, field)

    @classmethod
    def get_order_by_by_field(cls, model, field: str, direction: str):
        direction_method = cls.get_direction_method(direction)
        model_field = cls.get_model_field(model, field)

        return getattr(model_field, direction_method)()

    @classmethod
    def get_order_by(cls, model, fields: list, directions: list):
        for field, direction in zip(fields, directions):
            yield cls.get_order_by_by_field(model, field, direction)


async def pg_search(pg_session, query_filter, model):
    statement = select(model)

    for filter_ in FilterBuilder.get_filter(
        model, query_filter.filter_fields, query_filter.values, query_filter.ops
    ):
        statement = statement.filter(filter_)

    for order_by in OrderByBuilder.get_order_by(
        model, query_filter.sort_fields, query_filter.directions
    ):
        statement = statement.order_by(order_by)

    execute_result = await pg_session.execute(statement)
    count = len([i for i in execute_result.scalars()])

    if query_filter.offset:
        statement = statement.offset(query_filter.offset)

    if query_filter.limit:
        statement = statement.limit(query_filter.limit)

    execute_result = await pg_session.execute(statement)
    items = [i for i in execute_result.scalars()]

    return items, count
