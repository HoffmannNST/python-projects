# Pesel generator

Project with functions for generating PESEL codes in two ways and comparing their performance.

## PESEL code

Polish national identity code (Public Electronic Census System, Polish: Powszechny Elektroniczny System Ewidencji Ludności - PESEL).

It has the form YYMMDDZZZXQ, where YYMMDD is the date of birth (with century encoded in month field), ZZZ is the personal identification number, X denotes sex (even for females, odd for males) and Q is a parity number.

More information on PESEL codes can be found [here](https://en.wikipedia.org/wiki/National_identification_number#Poland).

## Generation

Those ways of generation PESEL codes are:

- function `generate_ssns` made using Faker package,
- function `generate_unique_ssns` developed by myself.

### `generate_ssns`

Function uses Provider class with pl_PL localization and `.ssn` method for generating random PESEL codes.

### `generate_unique_ssns`

Function generates unique PESEL codes with specified parameters. PESEL code can be generated for virtual person with specified gender and birthday within a range of dates. Function creates a list of all possible PESEL codes within set range and randomizes their positions within list. Then specified number of PESEL codes are picked from list and are returned as pandas Series object. In case of too narrow date range and too big number of codes requested, so there is not enought of possible PESEL codes, function will return only the number of codes that can be generated.

## Validation

Project also contains `validate_ssn` function which takes PESEL code, date range and gender input and then checks if PESEL code is correct and matches specified gender and dates.
