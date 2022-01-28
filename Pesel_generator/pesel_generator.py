#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from random import shuffle
from time import time
from datetime import date, timedelta
from pandas import Series as pd_series
from faker import Faker

FEMALE_CODES = [0, 2, 4, 6, 8]
MALE_CODES = [1, 3, 5, 7, 9]
WEIGHTS = [1, 3, 7, 9, 1, 3, 7, 9, 1, 3]
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
    """Function for generating PESEL codes using faker package
    with Provider class for pl_PL localization and ssn method.

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
        print("Incorrect number of records was set!")


def generate_pesel_codes(gender, date_from, date_to):
    """Function for generating list of all possible PESEL codes within
    specified date range, and with specified gender.

    Args:
        gender (str): specified gender - "f" for females, "m" for males,
        date_from (str): minimal value of birthday range,
        date_to (str): maximal value of birthday range.

    Raises:
        TypeError: raise if input data is wrong.

    Returns:
        list: list of all possible PESEL codes.
    """
    possible_pesel_codes = []

    start_date = date(int(date_from[:4]), int(date_from[5:7]), int(date_from[8:10]))
    end_date = date(int(date_to[:4]), int(date_to[5:7]), int(date_to[8:10]))

    delta = end_date - start_date  # returns timedelta

    for i in range(delta.days + 1):  # Generate PESEL code date
        date_day = str(start_date + timedelta(days=i))
        century = int(date_day[:2])
        year = int(date_day[2:4])
        month = int(date_day[5:7])
        day = int(date_day[8:10])

        # Encode century into month
        if century < 19:
            month += 80
        elif century > 19:
            month += 20

        for random_digits in range(999):  # Add 3 digits from 0 to 9
            if gender == "f":
                gender_codes = FEMALE_CODES
            elif gender == "m":
                gender_codes = MALE_CODES
            else:
                raise TypeError
            for gender_digit in gender_codes:  # Add 1 digit for gender
                # Parse PESEL code without last digit
                pesel_code = (
                    str(year).zfill(2)
                    + str(month).zfill(2)
                    + str(day).zfill(2)
                    + str(random_digits).zfill(3)
                    + str(gender_digit)
                )

                # Generate contol digit by summarizing PESEL digits multplied by their weights
                control_digit = 0
                for count in range(0, 10):
                    sum_element = int(pesel_code[count]) * WEIGHTS[count]
                    if sum_element > 9:
                        sum_element = int(str(sum_element)[-1:])
                    control_digit += sum_element

                if control_digit % 10 == 0:
                    control_digit = 0
                elif control_digit > 9:
                    control_digit = 10 - int(str(control_digit)[-1:])

                # Parse full PESEL code
                pesel_code += str(control_digit)

                # Add PESEL code to the list of possible codes
                possible_pesel_codes.append(pesel_code)

    return possible_pesel_codes


def generate_unique_ssns(unique_records, gender, date_from, date_to):
    """Function for generating unique PESEL codes within specified
    date range, and with specified gender.

    Args:
        unique_records (int): number of records that needs to be created,
        gender (str): specified gender - "f" for females, "m" for males,
        date_from (str): minimal value of birthday range,
        date_to (str): maximal value of birthday range.

    Raises:
        TypeError: raise if input data is wrong.

    Returns:
        object: pandas Series with all generated unique PESEL codes.
    """
    try:
        picked_pesel_codes = []
        # Check for input date length
        if len(date_from) != 10 or len(date_to) != 10:
            raise TypeError

        # Generate all possible PESEL codes
        pesel_codes_list = generate_pesel_codes(gender, date_from, date_to)

        # Randomize list
        shuffle(pesel_codes_list)

        # Check if requested records exceed number of possible unique PESEL codes
        if len(pesel_codes_list) >= unique_records:
            for index in range(unique_records):
                picked_pesel_codes.append(pesel_codes_list[index])
        else:
            print("\tATTENTION! The parameters of the function is to strict!")
            print(
                f"\tMaximum number of unique PESEL codes were generated, which is: {len(pesel_codes_list)}"
            )
            for index in range(len(pesel_codes_list)):
                picked_pesel_codes.append(pesel_codes_list[index])

        return pd_series(picked_pesel_codes)
    except TypeError:
        print("Incorrect input data was set!")


def validate_ssn(pesel_code, gender, birthday):
    """Function for validating PESEL codes.

    Args:
        pesel_code (str): PESEL code to be validated,
        gender (str): gender that should be encoded into PESEL code, "f" for females, "m" for males,
        birthday (str): birthday that should be encoded into PESEL code, "any" for not specified.

    Returns:
        str: expression stating if PESEL code is valid or what is wrong if not valid.
    """
    # Check lenght
    if len(pesel_code) != 11:
        return "PESEL code is incorrect - wrong lenght"

    # Check gender
    if gender == "f":
        if int(pesel_code[9]) not in FEMALE_CODES:
            return "PESEL code is incorrect - gender missmatch"
    elif gender == "m":
        if int(pesel_code[9]) not in MALE_CODES:
            return "PESEL code is incorrect - gender missmatch"

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
            return "PESEL code is incorrect - birthday missmatch"

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
        return "PESEL code is incorrect - wrong control digit"

    return "PESEL code is correct"


if __name__ == "__main__":
    for records in [1000, 10000, 100000]:
        print(f"Generation of {records} PESEL codes took:")
        start_time = time()
        series_faker = generate_ssns(records)
        print(f"\t{time() - start_time :.4f} seconds for generate_ssns")

        start_time = time()
        series_unique = generate_unique_ssns(records, "m", "1990-01-01", "1990-01-19")
        print(f"\t{time() - start_time :.4f} seconds for generate_unique_ssns")

    print()

    # Testing validate_ssn on random PESEL codes using "assert".
    for data in MOCK_DATA_CORRECT:
        assert validate_ssn(*data) == "PESEL code is correct"

    # Testing output of validate_ssn on random PESEL codes with purposely wrong input.
    for data in MOCK_DATA_ERRORS:
        validation_result = validate_ssn(*data)
        print(validation_result)
