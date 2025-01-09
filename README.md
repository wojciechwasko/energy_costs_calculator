A simple Python script to estimate energy costs when using different billing schemes.

```
usage: calc_energy_cost.py [-h] -s SCHEDULES [SCHEDULES ...] -f FILES [FILES ...]

Calculate energy costs based on different billing schemes.

options:
  -h, --help            show this help message and exit
  -s SCHEDULES [SCHEDULES ...], --schedules SCHEDULES [SCHEDULES ...]
                        Billing schemes with name and schedule definition.
  -f FILES [FILES ...], --files FILES [FILES ...]
                        CSV files to process.

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

Schedules defined based on data from https://www.energa.pl/dom/umowy/taryfa (accessed Jan 9th 2025):
    - until October 2025:
      "G11;00:00-00:00=0,5"
      "G12;00:00-06:00=0,4721;06:00-13:00=0,5;13:00-15:00=0,4721;15:00-22:00=0,5;22:00-00:00=0,4721"
      "G12w;00:00-06:00=0,4957;06:00-13:00=0,5;13:00-15:00=0,4957;15:00-22:00=0,5;22:00-00:00=0,4957;weekend=0,4957"
      "G12r;00:00-07:00=0,3796;07:00-13:00=0,5;13:00-16:00=0,3796;16:00-22:00=0,5;22:00-00:00=0,3796"
    - after October 2025:
      "G11;00:00-00:00=0,6249"
      "G12;00:00-06:00=0,4721;06:00-13:00=0,7283;13:00-15:00=0,4721;15:00-22:00=0,7283;22:00-00:00=0,4721"
      "G12w;00:00-06:00=0,4957;06:00-13:00=0,7620;13:00-15:00=0,4957;15:00-22:00=0,7620;22:00-00:00=0,4957;weekend=0,4957"
      "G12r;00:00-07:00=0,3796;07:00-13:00=0,8388;13:00-16:00=0,3796;16:00-22:00=0,8388;22:00-00:00=0,3796"
```
