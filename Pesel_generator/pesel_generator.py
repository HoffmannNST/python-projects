from random import randint
from time import time
from pandas import Series as pd_series
from faker import Faker

LONG_MONTHS = {1, 3, 5, 7, 8, 10, 12}
SHORT_MONTHS = {4, 6, 9, 11}
FEMALE_CODES = [0, 2, 4, 6, 8]
MALE_CODES = [1, 3, 5, 7, 9]
WEIGHTS = [1, 3, 7, 9, 1, 3, 7, 9, 1, 3]
ALLOWED_FAILS = 80
MOCK_DATA_CORRECT = [
    ("96032060484", "f", "1996-03-20"),
    ("03212564751", "m", "2003-01-25"),
    ("09291338241", "f", "2009-09-13"),
    ("79070619489", "f", "1979-07-06"),
    ("17322792418", "d", "any"),
]
MOCK_DATA_ERRORS = [
    ("96032060484", "m", "1996-03-20"),
    ("03212564751", "m", "2003-01-26"),
    ("0929133824", "f", "2009-09-13"),
    ("79070619488", "f", "1979-07-06"),
    ("17322792418", "d", "any"),
]


def generate_ssns(faker_records):
    """Function for generating PESEL codes.

    Args:
        records (int): number of records that needs to be created.

    Returns:
        object: pandas Series with all generated PESEL codes.
    """
    fake = Faker("pl_PL")
    Faker.seed(0)
    series_list = []

    try:
        for _ in range(faker_records):
            series_list.append(fake.ssn())
        series = pd_series(series_list)
        return series

    except TypeError:
        print("Podano nieprawidłową ilość wierszy!")


def generate_day(start_day, pesel_month, pesel_year):
    """Function for grnerating days of birth for PESEL codes.

    Args:
        start_day (int): the earliest day of the month possible for generation,
        pesel_month (int): month value generated for PESEL code,
        pesel_year (int): year value generated for PESEL code.

    Returns:
        int: day generated for PESEL code.
    """
    # 31day months
    if pesel_month in LONG_MONTHS:
        pesel_day = randint(start_day, 31)
    # 30day months
    elif pesel_month in SHORT_MONTHS:
        pesel_day = randint(start_day, 30)
    # February
    else:
        # Leap year
        if pesel_year % 4 == 0:
            pesel_day = randint(start_day, 29)
        # Normal year
        else:
            pesel_day = randint(start_day, 28)
    return pesel_day


def generate_date(date_from, date_to):
    """Function for generating birthday dates for PESEL codes.

    Args:
        date_from (str): minimal value of birthday range,
        date_to (str): maximal value of birthday range.

    Returns:
        tuple: values of year, month and day generated for PESEL code
    """
    # Get date components from date range values
    year_from, year_to = date_from[:4], date_to[:4]
    month_from, month_to = date_from[5:7], date_to[5:7]
    day_from, day_to = date_from[8:10], date_to[8:10]

    # Get randomized year
    pesel_year = randint(int(year_from), int(year_to))

    # Get randomized month and day
    if year_from == year_to:
        pesel_month = randint(int(month_from), int(month_to))
        if month_from == month_to:
            pesel_day = randint(int(day_from), int(day_to))
        else:
            if str(pesel_month) == month_to:
                pesel_day = randint(1, int(day_to))
            elif str(pesel_month) == month_from:
                pesel_day = generate_day(int(day_from), pesel_month, pesel_year)
            else:
                pesel_day = generate_day(1, pesel_month, pesel_year)
    else:
        if str(pesel_year) == year_to:
            pesel_month = randint(1, int(month_to))
            if str(pesel_month) == month_to:
                pesel_day = randint(1, int(day_to))
            else:
                pesel_day = generate_day(1, pesel_month, pesel_year)
        elif str(pesel_year) == year_from:
            pesel_month = randint(int(month_from), 12)
            if str(pesel_month) == month_from:
                pesel_day = generate_day(int(day_from), pesel_month, pesel_year)
            else:
                pesel_day = generate_day(1, pesel_month, pesel_year)
        else:
            pesel_month = randint(1, 12)
            pesel_day = generate_day(1, pesel_month, pesel_year)

    # Encode century into month
    if pesel_year < 1900:
        pesel_month += 80
    elif pesel_year > 1999:
        pesel_month += 20

    # Change year to YY format insted of YYYY format
    pesel_year = str(pesel_year)[2:4]

    return pesel_year, pesel_month, pesel_day


def generate_pesel(series_list, sex, date_from, date_to, fail_count):
    """Recursive function for generating PESEL codes with values restricted by input data.

    Args:
        series_list (list): list of all generated PESEL codes,
        sex (str): required sex - "f" for females, "m" for males,
        date_from (str): minimal value of birthday range,
        date_to (str): maximal value of birthday range,
        fail_count (int): count of generated consecutive not unique PESEL codes.

    Raises:
        TypeError: raises when input data are incorrect.
    """
    # Terminate function if too many conseciutive not unique PESEL codes were generated
    if fail_count > ALLOWED_FAILS:
        return fail_count

    # Generate date
    pesel_year, pesel_month, pesel_day = generate_date(date_from, date_to)

    # Generate 3 random digits
    order_number = randint(000, 999)

    # Generate sex
    index = randint(0, 4)
    if sex == "f":
        sex_number = FEMALE_CODES[index]
    elif sex == "m":
        sex_number = MALE_CODES[index]
    else:
        sex_number = randint(0, 9)

    # Parse components
    pesel_code = (
        str(pesel_year)
        + str(pesel_month).zfill(2)
        + str(pesel_day).zfill(2)
        + str(order_number).zfill(3)
        + str(sex_number)
    )

    # Generate contol digit by summarizing PESEL digits multplied by their weights
    control_digit = 0
    for i in range(0, 10):
        sum_element = int(pesel_code[i]) * WEIGHTS[i]
        if sum_element > 9:
            sum_element = int(str(sum_element)[-1:])
        control_digit += sum_element

    if control_digit % 10 == 0:
        control_digit = 0
    elif control_digit > 9:
        control_digit = 10 - int(str(control_digit)[-1:])

    # Parse full PESEL
    pesel_code += str(control_digit)

    # Check if generated PESEL code is unique, if not create new one
    if pesel_code in series_list:
        fail_count += 1
        fail_count = generate_pesel(series_list, sex, date_from, date_to, fail_count)
    else:
        fail_count = 0
        series_list.append(pesel_code)
    return fail_count


def generate_unique_ssns(
    unique_records,
    sex,
    date_from,
    date_to,
):
    """Function for generation of unique PESEL codes with selected sex and birthday range.

    Args:
        records (int): number of records that needs to be created,
        sex (str): required sex - "f" for females, "m" for males,
        date_from (str): minimal value of birthday range,
        date_to (str): maximal value of birthday range.

    Returns:
        object: pandas Series with all generated unique PESEL codes.
    """
    series_list = []
    fail_count = 0
    try:
        # Check for date length
        if len(date_from) != 10 or len(date_to) != 10:
            raise TypeError
        for _ in range(unique_records):
            fail_count = generate_pesel(
                series_list, sex, date_from, date_to, fail_count
            )
            # Break if function cannot find unique PESEL code in ALLOWED_FAILS number of tries
            if fail_count > ALLOWED_FAILS:
                print("\t\tWarunki generowania numerów PESEL są zbyt wąskie.")
                print(
                    "\t\tWygenerowano jedynie {} numerów PESEL.".format(
                        len(series_list)
                    )
                )
                break
        return pd_series(series_list)

    except TypeError:
        print("Podano nieprawidłowe dane wejściowe!")


def validate_ssn(pesel_code, sex, birthday):
    """Function for validating PESEL codes.

    Args:
        pesel_code (str): PESEL code to be validated,
        sex (str): sex that should be encoded into PESEL code, "f" for females, "m" for males,
        birthday (str): birthday that should be encoded into PESEL code, "any" for not specified.

    Returns:
        str: expression stating if PESEL code is valid or what is wrong if not valid.
    """
    # Check lenght
    if len(pesel_code) != 11:
        return "Numer PESEL jest niepoprawny - niezgodna długość"

    # Check sex
    if sex == "f":
        if int(pesel_code[9]) not in FEMALE_CODES:
            return "Numer PESEL jest niepoprawny - niezgodna płeć"
    elif sex == "m":
        if int(pesel_code[9]) not in MALE_CODES:
            return "Numer PESEL jest niepoprawny - niezgodna płeć"

    # Check birthday
    if birthday != "any":
        # Get date components from birthday string
        century = int(birthday[:2])
        year = int(birthday[2:4])
        month = int(birthday[5:7])
        day = int(birthday[8:10])

        # Get date components from PESEL string
        year_check = int(pesel_code[:2])
        month_check = int(pesel_code[2:4])
        day_check = int(pesel_code[4:6])

        # Encode century into month
        if century < 19:
            month += 80
        elif century > 19:
            month += 20

        if year_check != year or month_check != month or day_check != day:
            return "Numer PESEL jest niepoprawny - niezgodna data urodzenia"

    # Ckeck control digit / last digit
    control_digit = 0
    for i in range(0, 10):
        sum_element = int(pesel_code[i]) * WEIGHTS[i]
        if sum_element > 9:
            sum_element = int(str(sum_element)[-1:])
        control_digit += sum_element

    if control_digit % 10 == 0:
        control_digit = 0
    elif control_digit > 9:
        control_digit = 10 - int(str(control_digit)[-1:])
    if control_digit != int(pesel_code[10]):
        return "Numer PESEL jest niepoprawny - niezgodna cyfra kontrolna"

    return "Numer PESEL jest poprawny"


if __name__ == "__main__":
    # generate_unique_ssns cannot generate 100'000 unique PESEL codes
    # with specified sex and within 1990-01-01, 1990-01-19 date range, because
    # there are only 94'905 possible PESEL code combinations. Therfore fail_count
    # and ALLOWED_FAILS were intoduced to prevent function from working too long
    # with low probability of finding new unique PESEL code.
    for records in [1000, 10000, 100000]:
        print("Excecution of {} records took:".format(records))
        start_time = time()
        series_faker = generate_ssns(records)
        print("\t{:.4f} seconds for generate_ssns".format(time() - start_time))

        start_time = time()
        series_unique = generate_unique_ssns(records, "m", "1990-01-01", "1990-01-19")
        print("\t{:.4f} seconds for generate_unique_ssns".format(time() - start_time))

    print()

    # Testing validate_ssn on random PESEL codes using "assert".
    for data in MOCK_DATA_CORRECT:
        assert validate_ssn(*data) == "Numer PESEL jest poprawny"

    # Testing output of validate_ssn on random PESEL codes with purposely wrong input.
    for data in MOCK_DATA_ERRORS:
        validation_result = validate_ssn(*data)
        print(validation_result)
