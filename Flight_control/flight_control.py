import sqlite3
from csv import reader


# Connect to DataBase
conn = sqlite3.connect(":memory:")
c = conn.cursor()


# Create table (2.1)
c.execute(
    """CREATE TABLE FlightLeg (
    id INTEGER PRIMARY KEY,
    tailNumber VARCHAR(6),
    sourceAirportCode VARCHAR(3),
    destinationAirportCode VARCHAR(3),
    sourceCountryCode VARCHAR(3),
    destinationCountryCode VARCHAR(3),
    departureTimeUtc DATE,
    landingTimeUtc DATE
    ) """
)
conn.commit()


# Import data from flightlegs.csv to program (2.2.1)
with open("flightlegs.csv", "r") as data_file:
    db = reader(data_file, delimiter=";")
    header = next(db)
    to_db = [
        (
            i[0],
            i[1],
            i[2],
            i[3],
            i[4],
            i[5],
            i[6],
        )
        for i in db
    ]


# Import data from program to DataBase (2.2.2)
c.executemany(
    """INSERT INTO FlightLeg (
        tailNumber,
        sourceAirportCode,
        destinationAirportCode,
        sourceCountryCode,
        destinationCountryCode,
        departureTimeUtc,
        landingTimeUtc
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
    to_db,
)
conn.commit()


# Create column with flight duration (2.3.1)
c.executescript(
    """
    ALTER TABLE FlightLeg ADD COLUMN flightDuration date;

    UPDATE
        FlightLeg
    SET
        flightDuration = round((julianday(landingTimeUtc) - julianday(departureTimeUtc))*1440);
    """
)
conn.commit()


# Create column with flight type (2.3.2)
c.executescript(
    """
    ALTER TABLE FlightLeg ADD COLUMN flightType VARCHAR(1);

    UPDATE
        FlightLeg
    SET
        flightType = 'D'
    WHERE
        sourceCountryCode = destinationCountryCode;

    UPDATE
        FlightLeg
    SET
        flightType = 'I'
    WHERE
        sourceCountryCode != destinationCountryCode;
    """
)
conn.commit()


# Get plane with the most flights (2.4.1)
c.execute(
    """
    SELECT
        tailNumber, COUNT(*)
    FROM
        FlightLeg
    GROUP BY
        tailNumber
    ORDER BY
        COUNT(*) DESC
    """
)
print("\nSamolot który wykonał najwięcej lotów: {}".format(c.fetchone()[0]))


# Get plane with the most time flying (2.4.2)
c.execute(
    """
    SELECT
        tailNumber, SUM(flightDuration)
    FROM
        FlightLeg
    GROUP BY
        tailNumber
    ORDER BY
        SUM(flightDuration) DESC
    """
)
print("\nSamolot który przeleciał łącznie najwięcej minut: {}".format(c.fetchone()[0]))


# Get shortest and longest of domestic and international flights (2.4.3)
SQL_COMMANDS = [("D", "ASC"), ("D", "DESC"), ("I", "ASC"), ("I", "DESC")]
longest_shortest_flights = []

for command in SQL_COMMANDS:
    c.execute(
        """
        SELECT
            tailNumber, departureTimeUtc, flightDuration
        FROM
            FlightLeg
        WHERE
            flightType='{}'
        ORDER BY
            flightDuration {}
        """.format(
            *command
        )
    )
    longest_shortest_flights.append(c.fetchone())

print(
    """
Loty krajowe:
    Najkrótszy: {}, {} - trwał {} min
    Najdłuższy: {}, {} - trwał {} min\n
Loty międzynarodowe:
    Najkrótszy: {}, {} - trwał {} min
    Najdłuższy: {}, {} - trwał {} min
    """.format(
        *longest_shortest_flights[0],
        *longest_shortest_flights[1],
        *longest_shortest_flights[2],
        *longest_shortest_flights[3]
    )
)


# Get wrong records and shortest time between flights (2.4.4, 2.4.5)
c.execute(
    """
    SELECT
        tailNumber, julianday(departureTimeUtc), julianday(landingTimeUtc), departureTimeUtc
    FROM
        FlightLeg
    ORDER BY
        tailNumber DESC,
        departureTimeUtc ASC
    """
)

error_list = []
break_time_shortest = 10000

shortest_break_data = c.fetchall()
for i, _ in enumerate(shortest_break_data):
    if i == 0:
        pass
    else:
        if shortest_break_data[i][0] == shortest_break_data[i - 1][0]:
            break_time_check = shortest_break_data[i][1] - shortest_break_data[i - 1][2]
            if break_time_check < 0:
                error_list.append(
                    (
                        shortest_break_data[i - 1][0],
                        shortest_break_data[i - 1][3],
                        shortest_break_data[i][0],
                        shortest_break_data[i][3],
                    )
                )
            else:
                if break_time_check < break_time_shortest:
                    break_time_shortest = break_time_check
                    break_time_shortest_info = (
                        shortest_break_data[i - 1][0],
                        shortest_break_data[i - 1][3],
                        shortest_break_data[i][0],
                        shortest_break_data[i][3],
                    )

print("Lista par błędnych rekordów lotów:")
for i in error_list:
    print("\t{}, {} - {}, {}".format(i[0], i[1], i[2], i[3]))

print("\nNajkrótsza przerwa miała miejsce między lotem:")
print(
    "\t{}, {}, a lotem: {}, {} i trwała {} min".format(
        *break_time_shortest_info, int(round(break_time_shortest * 1440, 0))
    )
)


# Close connection
conn.close()
