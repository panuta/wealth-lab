from datetime import datetime


def strip_time(dt):
    return datetime(dt.year, dt.month, dt.day, 0, 0, 0, 0)
