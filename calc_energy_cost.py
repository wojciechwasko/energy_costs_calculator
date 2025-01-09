#!/usr/bin/env python

import argparse
import numpy as np
import pandas as pd
from datetime import datetime

def parse_schedule(schedule_str):
    schedule = {'weekday': [0] * 24, 'weekend': None}
    segments = schedule_str.split(';')
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
    for scheme_name, schedule in schedules.items():
        flat_cost = 0
        net_cost = 0
        for i, row in enumerate(data):
            hour = int(row[0].hour)
            is_weekend = row[0].weekday() >= 5
            price = schedule['weekend'][hour] if is_weekend and schedule['weekend'] else schedule['weekday'][hour]
            flat_cost += row[1] * price
            net_cost += max(row[3], 0) * price
        costs[scheme_name] = {'Flat': flat_cost, 'Net': net_cost}
    return costs

def main():
    parser = argparse.ArgumentParser(description="Calculate energy costs based on different billing schemes.")
    parser.add_argument('-s', '--schedules', required=True, nargs='+', help="Billing schemes as 'starttime-endtime=price' separated by semicolons, with optional 'weekend=price'.")
    parser.add_argument('-f', '--files', required=True, nargs='+', help="CSV files to process.")
    args = parser.parse_args()

    schedules = {}
    for i, schedule_str in enumerate(args.schedules):
        try:
            schedules[f"Scheme {i+1}"] = parse_schedule(schedule_str)
        except ValueError as e:
            parser.error(f"Invalid schedule {schedule_str}: {e}")

    data = load_csv_files(args.files)

    costs = calculate_costs(data, schedules)

    for scheme, cost in costs.items():
        print(f"{scheme}: Flat Cost = {cost['Flat']:.2f}, Net Cost = {cost['Net']:.2f}")

if __name__ == '__main__':
    main()

