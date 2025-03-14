import os
import pandas as pd
from datetime import datetime
import calendar

from schedula_clas import Schedule


class Day:
    def __init__(self, date):
        self.date = date
        self.schedule = Schedule("7:00", "18:00")


def load_excel_file(path):
    if os.path.isfile(path):
        return pd.read_excel(path)
    else:
        raise FileNotFoundError


def string_to_date(date_string):
    return datetime.strptime(date_string, "%Y-%m-%d")


def is_date_sunday(date_string):
    return string_to_date(date_string).weekday() == 6


def get_all_months_in_df(df):
    return df["Datum"].dt.to_period("M").unique()


def get_all_mitarbeiter_in_df(df):
    return df["Mitarbeiter"].unique()


def get_days_for_mitarbeiter(df):
    # List which contains all NON-SUNDAY dates
    valid_days = []

    # Iterate over months found in table
    for month in get_all_months_in_df(excel_df):
        # Get number of days in a month
        number_days = calendar.monthrange(month.year, month.month)[1]

        # Iterate over days per month
        for day in range(1, number_days + 1):
            if not is_date_sunday(f"{month.year}-{month.month}-{day}"):
                # Create a new day object
                print(f"########## Date to build schedule for:\t{month.year}-{month.month}-{day}")
                if pd.to_datetime(f"{month.year}-{month.month}-{day}") in df["Datum"].values:
                    new_day = Day(f"{month.year}-{month.month}-{day}")

                    df_current_day = df[df["Datum"] == f"{month.year}-{month.month}-{day}"]

                    for index, row in df_current_day.iterrows():
                        new_day.schedule.add_blocked_time(row["von"], row["bis"])

                    print("##### Free slots for that date")
                    print(f"{new_day.schedule.display_free_slots()}")

                else:
                    new_day = Day(f"{month.year}-{month.month}-{day}")
                    print("##### ALL Slots available for that date")

                valid_days.append(new_day)

    return valid_days


def fill_days_for_mitarbeiter(df):
    for day in df:
        day.schedule.total_free_time()

    return


def fill_day(df, day_obj):
    if day_obj.schedule.total_free_time() < 120:
        return df, day_obj
    else:
        8
        fill_day(df, day_obj)


if __name__ == '__main__':
    excel_df = load_excel_file("./149.xlsx")

    for mitarbeiter in get_all_mitarbeiter_in_df(excel_df):
        print(f"\n\n############### LISTE FÜR MITARBEITER: {mitarbeiter}")
        excel_df_mitarbeiter = excel_df[excel_df["Mitarbeiter"] == mitarbeiter]
        days = get_days_for_mitarbeiter(excel_df_mitarbeiter)
