from datetime import datetime


def is_date_format(date):
    try:
        datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        return False
    return True


def current_year():
    return datetime.today().year


def year_choices(from_year):
    year = current_year()
    return list(range(year, from_year-1, -1))


YEARS = year_choices(from_year=2020)


def check_year(year):
    if not year:
        year = current_year()
    elif year != 'all':
        # number
        try:
            year = int(year)
            # if requested year does not exist in YEARS - show current year
            if year not in YEARS:
                year = current_year()
        except ValueError:
            year = current_year()
    return year


def prepare_orders_by_months():
    months = ['JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE', 'JULY', 'AUGUST', 'SEPTEMBER', 'OCTOBER', 'NOVEMBER', 'DECEMBER']
    orders = [0] * 12
    return list(map(list, zip(months, orders)))