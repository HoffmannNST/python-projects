import pandas
from faker import Faker


def generate_ssns(records):
    """Function for generation of PESEL codes.

    Args:
        records (int): number of records that needs to be created.

    Returns:
        object: pandas Series with all generated PESEL codes.
    """
    fake = Faker("pl_PL")
    Faker.seed(0)
    series_list = []

    try:
        for _ in range(records):
            series_list.append(fake.ssn())
        series = pandas.Series(series_list)
        return series

    except TypeError:
        print("Podano nieprawidłową ilość wierszy!")


def parse_date(pesel_code, century, month_decrement):
    """Function for parsing PESEL code to YYYY-MM-DD format.

    Args:
        pesel_code (str): PESEL code to be parsed,
        century (str): first two digits of year of birth taken from 3rd didgit in PESEL code,
        month_decrement (int): decrement value of 3rd digit in PESEL code.

    Returns:
        str: Date in YYYY-MM-DD format acquired from PESEL code.
    """
    pesel_date = (
        century
        + pesel_code[:2]
        + "-"
        + str(int(pesel_code[2]) - month_decrement)
        + pesel_code[3]
        + "-"
        + pesel_code[4:6]
    )
    return pesel_date


def transform_date(pesel_code, date_from, date_to):
    """Function for transforming PESEL code to YYYY-MM-DD format.

    Args:
        pesel_code (str): PESEL code to be parsed,
        date_from (str): minimal value of birthday range,
        date_to (str): maximal value of birthday range.

    Returns:
        str: Date in YYYY-MM-DD format acquired from PESEL code.
    """
    if pesel_code[2] < "2":
        pesel_date = parse_date(pesel_code, "19", 0)
    elif pesel_code[2] < "8":
        pesel_date = parse_date(pesel_code, "20", 2)
    else:
        pesel_date = parse_date(pesel_code, "18", 8)

    if pesel_date >= date_from and pesel_date <= date_to:
        date_in_range = True
    else:
        date_in_range = False

    return date_in_range


def get_unique_ssns(series_list, sex, date_from, date_to):
    """Recursive function for genereting PESEL codes with sex and dates restrictions.

    Args:
        series_list (list): list of all generated PESEL codes,
        sex (str): required sex - "f" for females, "m" for males,
        date_from (str): minimal value of birthday range,
        date_to (str): maximal value of birthday range.
    """
    fake = Faker("pl_PL")
    pesel_code = fake.unique.ssn()
    date_in_range = transform_date(pesel_code, date_from, date_to)

    if sex == "f":
        if (int(pesel_code[9]) % 2) == 0 and date_in_range:
            series_list.append(pesel_code)
        else:
            get_unique_ssns(series_list, sex, date_from, date_to)
    elif sex == "m":
        if (int(pesel_code[9]) % 2) == 1 and date_in_range:
            series_list.append(pesel_code)
        else:
            get_unique_ssns(series_list, sex, date_from, date_to)


def generate_unique_ssns(records, sex, date_from, date_to):
    """Function for generation of unique PESEL codes with selected sex and birthday range.

    Args:
        records (int): number of records that needs to be created,
        sex (str): required sex - "f" for females, "m" for males,
        date_from (str): minimal value of birthday range,
        date_to (str): maximal value of birthday range.

    Returns:
        object: pandas Series with all generated unique PESEL codes.
    """
    Faker.seed(0)
    series_list = []

    try:
        for _ in range(records):
            get_unique_ssns(series_list, sex, date_from, date_to)
        series = pandas.Series(series_list)
        return series

    except TypeError:
        print("Podano nieprawidłowe dane wejściowe!")


if __name__ == "__main__":
    Series = generate_ssns(1000)
    print(Series)
    Series = generate_unique_ssns(1000, "f", "1900-01-01", "1990-01-19")
    print(Series)
