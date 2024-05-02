import datetime

# converts local time into UTC ISO
def iso_to_utc(input_time):
    # Convert the input time to a datetime object
    dt = datetime.datetime.fromisoformat(input_time)
    # Convert the datetime object to UTC timezone
    utc_dt = dt.astimezone(datetime.timezone.utc)
    # Format the UTC datetime in ISO format
    utc_time = utc_dt.isoformat()
    return utc_time


# converts '13-Jun-2021' into '13-06-2021'
def dmy_en_month_to_number(date_string):
    datetime_obj = datetime.datetime.strptime(date_string, '%d-%b-%Y')
    new_date_string = datetime_obj.strftime('%d-%m-%Y')
    return new_date_string