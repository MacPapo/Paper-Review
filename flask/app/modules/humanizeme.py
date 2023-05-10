import humanize
from datetime import datetime


def humanize_natural(date):
    return humanize.naturaltime(datetime.utcnow() - date)


def humanize_date(date):
    return humanize.naturaldate(date)
