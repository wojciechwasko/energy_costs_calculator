#!/usr/bin/env python
import argparse
import numpy as np
import pandas as pd
from datetime import datetime

def parse_schedule(schedule_str):
    parts = schedule_str.split(';', 1)
    if len(parts) != 2:
        raise ValueError("Each schedule must start with a scheme name followed by the schedule definition.")
    scheme_name, schedule_def = parts
    schedule = {'name': scheme_name, 'weekday': [0] * 24, 'weekend': None}
    segments = schedule_def.split(';')
    for segment in segments:
        if segment.startswith('weekend='):
            weekend_price = float(segment.split('=')[1].replace(',', '.'))
            schedule['weekend'] = [weekend_price] * 24
        else:
            time_range, price = segment.split('=')
            start, end = time_range.split('-')
            price = float(price.replace(',', '.'))
            start_hour = int(start.split(':')[0])
            end_hour = int(end.split(':')[0])
            if start_hour == end_hour:
                schedule['weekday'] = [price] * 24
                break
            for hour in range(start_hour, end_hour if end_hour > start_hour else 24):
                schedule['weekday'][hour % 24] = price
    if any(p == 0 for p in schedule['weekday']):
        raise ValueError("Weekday schedule must cover the full 24 hours.")
    return schedule

def load_csv_files(csv_files):
    data = []
    for file in csv_files:
        df = pd.read_csv(file, sep=';', decimal=',')
        df.columns = ['Datetime', 'Energy Consumed', 'Energy Produced', 'Net Energy']
        df['Datetime'] = pd.to_datetime(df['Datetime'], format='%d.%m.%Y %H:%M')
        data.append(df)
    combined = pd.concat(data).drop_duplicates(subset=['Datetime']).sort_values('Datetime')
    return combined[['Datetime', 'Energy Consumed', 'Energy Produced', 'Net Energy']].to_numpy()

def calculate_costs(data, schedules):
    hourly_data = data[:, 1:]
    costs = {}
    for schedule in schedules:
        flat_cost = 0
        net_cost = 0
        for i, row in enumerate(data):
            hour = int(row[0].hour)
            is_weekend = row[0].weekday() >= 5
            price = schedule['weekend'][hour] if is_weekend and schedule['weekend'] else schedule['weekday'][hour]
            flat_cost += row[1] * price
            net_cost += max(row[3], 0) * price
        costs[schedule['name']] = {'Flat': flat_cost, 'Net': net_cost}
    return costs

def main():
    parser = argparse.ArgumentParser(
        description="Calculate energy costs based on different billing schemes.",
        epilog="""
Example:
    python script.py -s "G11;00:00-00:00=0,5" "G13r;00:00-06:00=0,4957;06:00-13:00=0,5;13:00-15:00=0,4957;15:00-22:00=0,5;22:00-00:00=0,4957;weekend=0,4213" -f file1.csv file2.csv

Schedule Syntax:
    <Scheme Name>;<TimeRange1>=<Price1>[;<TimeRange2>=<Price2>...][;weekend=<WeekendPrice>]
    - Scheme Name: A unique identifier for the billing scheme.
    - TimeRange: Defined as HH:MM-HH:MM (must align with hourly intervals, minutes must be 0).
    - Price: The rate in currency per kWh.
    - WeekendPrice: Optional rate applied for weekends (Saturday and Sunday).

CSV Format:
    The CSV files must have the following format:
    "Datetime;ENERGIA POBRANA [KWH];ENERGIA WPROWADZONA [KWH];SALDO ENERGII (BILANS = ENERGIA POBRANA - ENERGIA WPROWADZONA) [KWH]"
    - Datetime: Format "%d.%m.%Y %H:%M".
    - Energy Consumed: Energy taken from the grid (kWh).
    - Energy Produced: Energy supplied back to the grid (kWh).
    - Net Energy: Difference between consumed and produced energy (kWh).
    """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('-s', '--schedules', required=True, nargs='+', help="Billing schemes with name and schedule definition.")
    parser.add_argument('-f', '--files', required=True, nargs='+', help="CSV files to process.")
    args = parser.parse_args()

    schedules = []
    for schedule_str in args.schedules:
        try:
            schedules.append(parse_schedule(schedule_str))
        except ValueError as e:
            parser.error(f"Invalid schedule {schedule_str}: {e}")

    data = load_csv_files(args.files)

    costs = calculate_costs(data, schedules)

    for scheme, cost in costs.items():
        print(f"{scheme}: Flat Cost = {cost['Flat']:.2f}, Net Cost = {cost['Net']:.2f}")

if __name__ == '__main__':
    main()

