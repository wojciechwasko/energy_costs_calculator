#!/usr/bin/env python
import argparse
import numpy as np
import pandas as pd
from datetime import datetime

def parse_schedule(schedule_str):
    schedule = [0] * 24
    segments = schedule_str.split(';')
    for segment in segments:
        time_range, price = segment.split('=')
        start, end = time_range.split('-')
        price = float(price.replace(',', '.'))
        start_hour = int(start.split(':')[0])
        end_hour = int(end.split(':')[0])
        if start_hour == end_hour:
            schedule = [price] * 24
            break
        for hour in range(start_hour, end_hour if end_hour > start_hour else 24):
            schedule[hour % 24] = price
    if any(p == 0 for p in schedule):
        raise ValueError("Schedule must cover the full 24 hours.")
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
        flat_cost = np.sum(hourly_data[:, 0] * [schedule[int(t.hour)] for t in data[:, 0]])
        net_cost = np.sum(np.maximum(hourly_data[:, 2], 0) * [schedule[int(t.hour)] for t in data[:, 0]])
        costs[scheme_name] = {'Flat': flat_cost, 'Net': net_cost}
    return costs

def main():
    parser = argparse.ArgumentParser(description="Calculate energy costs based on different billing schemes.")
    parser.add_argument('-s', '--schedules', required=True, nargs='+', help="Billing schemes as 'starttime-endtime=price' separated by semicolons.")
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

