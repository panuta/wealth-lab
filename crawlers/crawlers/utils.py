from decimal import Decimal


def str_to_numeric(str):
    str = str.replace(',', '')
    if '.' in str:
        return Decimal(str)
    else:
        return int(str)
