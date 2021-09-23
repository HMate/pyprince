import orjson


def to_json(descriptor: dict):
    return orjson.dumps(descriptor, option=orjson.OPT_INDENT_2)
