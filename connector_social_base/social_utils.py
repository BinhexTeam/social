# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import date, datetime, timedelta

import pytz
from werkzeug.urls import url_encode, url_quote

from odoo.tools.date_utils import add


def convert_to_days(seconds=None, miliseconds=None):
    """
    Converts the given duration in seconds or miliseconds into days.

    :param int seconds: duration in seconds
    :param int miliseconds: duration in miliseconds
    :return: duration in days
    :rtype: int
    """
    if seconds:
        return seconds / 60 / 60 / 24
    elif miliseconds:
        return miliseconds / 1000 / 60 / 60 / 24
    return 0


def convert_to_date(
    date_add=None,
    seconds=None,
    miliseconds=None,
    expire_date=True,
    time_zone=None,
    format_date=None,
):
    if expire_date:
        if not date_add:
            date_add = date.today()
        return_date = add(
            date_add + timedelta(days=convert_to_days(seconds, miliseconds))
        )
    else:
        return_date = datetime.fromtimestamp(miliseconds / 1000)
    if time_zone:
        return_date = return_date.astimezone(time_zone)
    if format_date:
        return_date = return_date.strftime(format_date)
    return return_date


def convert_date_in_time(miliseconds, timezone=None):
    timezone = timezone if timezone else pytz.utc
    if isinstance(timezone, str):
        timezone = pytz.timezone(timezone)
    val_date = convert_to_date(
        miliseconds=miliseconds, expire_date=False, time_zone=timezone
    )
    current_date = datetime.now(timezone)
    diff_date = current_date - val_date
    seconds = diff_date.total_seconds()
    minutes = seconds / 60  # Convert seconds to minutes
    hours = minutes / 60  # Convert minutes to hours
    days = hours / 24  # Convert hours to days
    months = days / 30  # Convert days to months (months 30 days)
    years = months / 12  # Convert months to years

    if seconds < 60:
        date_in_time = f"{int(seconds)} seconds"
    elif minutes < 60:
        date_in_time = f"{int(minutes)} minutes"
    elif hours < 24:
        date_in_time = f"{int(hours)} hours"
    elif days < 30:
        date_in_time = f"{int(days)} días"
    elif months < 12:
        date_in_time = f"{int(months)} meses"
    else:
        years_exacts = int(years)
        months_exacts = int(months % 12)
        date_in_time = f"{years_exacts} years y {months_exacts} months"
    return date_in_time


def social_url_encode(field, values):
    """
    Encodes a list of values into a URL-encoded string.

    This function takes a field and a list of values, then constructs
    a URL-encoded string representation of the list in the format:
    'List(value1,value2,...)'. The encoded string is quoted safely
    for inclusion in URLs, allowing specific characters to remain
    unescaped.

    Args:
        field (str): The name of the field to be encoded.
        values (list): A list of string values to be encoded.

    Returns:
        str: A URL-encoded string representation of the field and list.
    """
    return url_quote(
        url_encode({field: f"List({','.join(values)})".replace("'", "")}).replace(
            "+", ""
        ),
        safe="()%=[]",
    )


def _generate_timestamps(date_start=None, date_end=None):
    if date_start:
        date_start_time = date_start.timestamp() * 1000
    else:
        date_start_time = datetime.now().timestamp() * 1000
    if date_end:
        date_end_time = date_start_time + date_end.timestamp()
    else:
        date_end_time = date_start_time + (30 * 86400000)
    return date_start_time, date_end_time
