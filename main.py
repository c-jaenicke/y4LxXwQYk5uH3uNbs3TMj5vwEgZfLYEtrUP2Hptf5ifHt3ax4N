import os
import pandas as pd
from datetime import datetime, timedelta
import calendar


class Buchung:
    def __init__(self, von: str, bis: str, dauer: float, fakturierbar: str, vorgang: str,
                 mitarbeiter: str, taetigkeit: str, bemerkung: str, ort: str, ort_projektrelevant: bool,
                 projekt_nr: str, projekt_bezeichnung: str, dienstleistung: str, gewerk: str):
        self.von = datetime.strptime(von, "%H:%M")
        self.bis = datetime.strptime(bis, "%H:%M")
        self.dauer = dauer
        self.fakturierbar = fakturierbar
        self.vorgang = vorgang
        self.mitarbeiter = mitarbeiter
        self.taetigkeit = taetigkeit
        self.bemerkung = bemerkung
        self.ort = ort
        self.ort_projektrelevant = ort_projektrelevant
        self.projekt_nr = projekt_nr
        self.projekt_bezeichnung = projekt_bezeichnung
        self.dienstleistung = dienstleistung
        self.gewerk = gewerk

    def __repr__(self):
        return f"Event({self.von.strftime('%H:%M')}, {self.bis.strftime('%H:%M')}, {self.dauer} hours, {self.vorgang})"


class Arbeitstag:
    def __init__(self, datum: str, day_start: str = "07:00", day_end: str = "19:00"):
        self.datum = datetime.strptime(datum, "%Y-%m-%d").date()
        self.KW = self.datum.isocalendar()[1]
        self.day_start = datetime.strptime(day_start, "%H:%M")
        self.day_end = datetime.strptime(day_end, "%H:%M")
        self.events = []

    def add_event(self, event):
        self.events.append(event)

    def get_free_slots(self):
        if not self.events:
            return [(self.day_start, self.day_end)]

        self.events.sort(key=lambda x: x.von)

        free_slots = []

        if self.events[0].von > self.day_start:
            free_slots.append((self.day_start, self.events[0].von))

        for i in range(len(self.events) - 1):
            if self.events[i].bis < self.events[i + 1].von:
                free_slots.append((self.events[i].bis, self.events[i + 1].von))

        if self.events[-1].bis < self.day_end:
            free_slots.append((self.events[-1].bis, self.day_end))

        return free_slots


def get_file_paths():
    while True:
        try:
            main_file = input("Dateiname der Datei mit allen neuen Projektzeiten: ")
            secondary_file = input("Dateiname der Datei mit Zeiten die eingefügt werden sollen: ")

            df_main = load_excel_file(main_file)
            df_secondary = load_excel_file(secondary_file)

            output_directory = input(
                "Enter the directory where you want to save the output file (leave blank for the current folder): ")

            if not output_directory:
                output_directory = os.getcwd()

            output_filename = f"{os.path.basename(main_file).split('.')[0]}_{os.path.basename(secondary_file).split('.')[0]}_ZUSAMMENGEFÜGT.xlsx"
            output_path = os.path.join(output_directory, output_filename)

            return df_main, df_secondary, output_path
        except FileNotFoundError as e:
            print(e)
            print("Please provide valid file paths.")


def load_excel_file(path):
    if os.path.isfile(path):
        df_excel = pd.read_excel(path)
        df_excel['Datum'] = pd.to_datetime(df_excel['Datum'], format='%d.%m.%Y')
        df_excel['von'] = pd.to_datetime(df_excel['von'], format='%H:%M:%S').dt.strftime('%H:%M')
        df_excel['bis'] = pd.to_datetime(df_excel['bis'], format='%H:%M:%S').dt.strftime('%H:%M')
        return df_excel
    else:
        raise FileNotFoundError(f"The file at {path} was not found.")


def generate_valid_dates_for_month(mitarbeiter_df):
    schedules = {}
    unique_months = mitarbeiter_df['Datum'].dt.to_period('M').unique()

    for month in unique_months:
        year = month.year
        month_number = month.month

        valid_dates = []
        for day in range(1, calendar.monthrange(year, month_number)[1] + 1):
            date = datetime(year, month_number, day)
            if date.weekday() < 6:
                valid_dates.append(date.date())

        for valid_date in valid_dates:
            if valid_date not in schedules:
                schedules[valid_date] = Arbeitstag(datum=str(valid_date))

    return schedules


def populate_schedule_with_events(mitarbeiter_df, schedules):
    for _, row in mitarbeiter_df.iterrows():
        datum = row["Datum"].date()
        if datum in schedules:
            event = Buchung(
                von=row["von"],
                bis=row["bis"],
                dauer=row["Dauer"],
                fakturierbar=row["fakturierbar"],
                vorgang=row["Vorgang"],
                mitarbeiter=row["Mitarbeiter"],
                taetigkeit=row["Tätigkeit"],
                bemerkung=row["Bemerkung"],
                ort=row["Ort"],
                ort_projektrelevant=row["Ort projektrelevant"],
                projekt_nr=row["Projekt-Nr."],
                projekt_bezeichnung=row["Projektbezeichnung"],
                dienstleistung=row["Dienstleistung"],
                gewerk=row["Gewerk"]
            )
            schedules[datum].add_event(event)
    return schedules


def convert_schedule_to_dataframe(schedules):
    event_list = []
    for date, schedule in schedules.items():
        for event in schedule.events:
            event_dict = {
                "KW": schedule.KW,
                "Datum": schedule.datum,
                "Von": event.von.strftime("%H:%M"),
                "Bis": event.bis.strftime("%H:%M"),
                "Dauer": event.dauer,
                "Fakturierbar": event.fakturierbar,
                "Vorgang": event.vorgang,
                "Mitarbeiter": event.mitarbeiter,
                "Tätigkeit": event.taetigkeit,
                "Bemerkung": event.bemerkung,
                "Ort": event.ort,
                "Ort projektrelevant": event.ort_projektrelevant,
                "Projekt-Nr.": event.projekt_nr,
                "Projektbezeichnung": event.projekt_bezeichnung,
                "Dienstleistung": event.dienstleistung,
                "Gewerk": event.gewerk,
            }
            event_list.append(event_dict)

    df_schedule = pd.DataFrame(event_list)
    df_schedule = df_schedule[[
        "KW", "Datum", "Von", "Bis", "Dauer", "Fakturierbar", "Vorgang", "Mitarbeiter", "Tätigkeit",
        "Bemerkung", "Ort", "Ort projektrelevant", "Projekt-Nr.", "Projektbezeichnung", "Dienstleistung", "Gewerk"
    ]]
    return df_schedule


def insert_secondary_events_into_schedule_across_days(mitarbeiter_df_secondary, schedules):
    events_to_remove = []
    failed_events = []
    regular_events = []

    for idx, row in mitarbeiter_df_secondary.iterrows():
        mitarbeiter = row["Mitarbeiter"]
        dauer = row["Dauer"]
        von = row["von"]
        bis = row["bis"]
        event_duration = (datetime.strptime(bis, "%H:%M") - datetime.strptime(von, "%H:%M")).seconds / 3600

        event_inserted = False

        for date, schedule in schedules.items():
            free_slots = schedule.get_free_slots()

            if free_slots:
                for slot in free_slots:
                    start_time, end_time = slot
                    if (end_time - start_time).seconds / 3600 >= event_duration:
                        new_start_time = start_time
                        new_end_time = new_start_time + timedelta(hours=event_duration)

                        new_event = Buchung(
                            von=new_start_time.strftime("%H:%M"),
                            bis=new_end_time.strftime("%H:%M"),
                            dauer=event_duration,
                            fakturierbar=row["fakturierbar"],
                            vorgang=row["Vorgang"],
                            mitarbeiter=row["Mitarbeiter"],
                            taetigkeit=row["Tätigkeit"],
                            bemerkung=row["Bemerkung"],
                            ort=row["Ort"],
                            ort_projektrelevant=row["Ort projektrelevant"],
                            projekt_nr=row["Projekt-Nr."],
                            projekt_bezeichnung=row["Projektbezeichnung"],
                            dienstleistung=row["Dienstleistung"],
                            gewerk=row["Gewerk"]
                        )

                        schedule.add_event(new_event)
                        regular_events.append({
                            "Datum": date,
                            "Mitarbeiter": mitarbeiter,
                            "Vorgang": row["Vorgang"],
                            "Dauer": row["Dauer"],
                            "Von": row["von"],
                            "Bis": row["bis"],
                            "Ort": row["Ort"],
                            "Ort projektrelevant": row["Ort projektrelevant"],
                            "Projekt-Nr.": row["Projekt-Nr."],
                            "Projektbezeichnung": row["Projektbezeichnung"],
                            "Dienstleistung": row["Dienstleistung"],
                            "Gewerk": row["Gewerk"],
                            "Bemerkung": row["Bemerkung"],
                            "Tätigkeit": row["Tätigkeit"],
                            "Fakturierbar": row["fakturierbar"]
                        })
                        event_inserted = True
                        events_to_remove.append(idx)
                        break

            if event_inserted:
                break

        if not event_inserted:
            failed_event = {
                "Mitarbeiter": row["Mitarbeiter"],
                "Vorgang": row["Vorgang"],
                "Dauer": row["Dauer"],
                "Von": row["von"],
                "Bis": row["bis"],
                "Ort": row["Ort"],
                "Ort projektrelevant": row["Ort projektrelevant"],
                "Projekt-Nr.": row["Projekt-Nr."],
                "Projektbezeichnung": row["Projektbezeichnung"],
                "Dienstleistung": row["Dienstleistung"],
                "Gewerk": row["Gewerk"],
                "Bemerkung": row["Bemerkung"],
                "Tätigkeit": row["Tätigkeit"],
                "Fakturierbar": row["fakturierbar"]
            }
            failed_events.append(failed_event)

    mitarbeiter_df_secondary = mitarbeiter_df_secondary.drop(events_to_remove).reset_index(drop=True)
    failed_df = pd.DataFrame(failed_events)

    return mitarbeiter_df_secondary, failed_df, regular_events


if __name__ == '__main__':
    df_main, df_secondary, output_path = get_file_paths()

    mitarbeiter_list = list(set(df_main['Mitarbeiter'].unique()))
    mitarbeiter_list_only_secondary = list(
        set(df_secondary['Mitarbeiter'].unique()) - set(df_main['Mitarbeiter'].unique()))

    all_failed_events_df = pd.DataFrame()
    all_events_df = pd.DataFrame()

    schedules = {}

    for mitarbeiter in mitarbeiter_list:
        mitarbeiter_df = df_main[df_main["Mitarbeiter"] == mitarbeiter]

        schedules = generate_valid_dates_for_month(mitarbeiter_df)
        schedules = populate_schedule_with_events(mitarbeiter_df, schedules)

        populated_events = convert_schedule_to_dataframe(schedules)
        all_events_df = pd.concat([all_events_df, populated_events], ignore_index=True)

        mitarbeiter_df_secondary = df_secondary[df_secondary["Mitarbeiter"] == mitarbeiter]
        mitarbeiter_df_secondary, failed_df, regular_events = insert_secondary_events_into_schedule_across_days(
            mitarbeiter_df_secondary, schedules)

        if not failed_df.empty:
            all_failed_events_df = pd.concat([all_failed_events_df, failed_df], ignore_index=True)

        if regular_events:
            regular_events_df = pd.DataFrame(regular_events)
            all_events_df = pd.concat([all_events_df, regular_events_df], ignore_index=True)

    if not all_events_df.empty:
        all_events_df.to_excel(output_path, index=False)

    if not all_failed_events_df.empty:
        failed_output_path = os.path.join(os.path.dirname(output_path), "failed_events.xlsx")
        all_failed_events_df.to_excel(failed_output_path, index=False)
