import decimal


def replace_decimals(obj):
    """
    Convert all whole number decimals in 'obj' to integers, convert all sets in lists
    """
    if isinstance(obj, list) or isinstance(obj, set):
        return [replace_decimals(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: replace_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, decimal.Decimal):
        return int(obj) if obj % 1 == 0 else obj
    return obj
