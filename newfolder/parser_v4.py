#!/usr/bin/env python3

import csv
import logging
import json
import sys
import yaml
from collections import defaultdict, OrderedDict
from datetime import datetime, timedelta
from pathlib import Path

# Set logging level
logging.basicConfig(stream=sys.stdout,
                    format="%(message)s",
                    level=logging.INFO)

# Current date in India
INDIA_DATE = datetime.strftime(
    datetime.utcnow() + timedelta(hours=5, minutes=30), "%Y-%m-%d")
INDIA_UTC_OFFSET = "+05:30"

# Arbitrary minimum date
MIN_DATE = "2020-01-01"

# Input/Output root directory
ROOT_DIR = Path("tmp")
CSV_DIR = ROOT_DIR / "csv" / "latest"
# State codes to be used as API keys
META_DATA = ROOT_DIR / "misc.json"
# Geographical districts of India
DISTRICT_LIST = ROOT_DIR / "state_district_wise.json"
# All raw_data's
RAW_DATA = "raw_data{n}.json"
# Deaths and recoveries for entries in raw_data1 and raw_data2
OUTCOME_DATA = "deaths_recoveries{n}.json"
# District data as of 26th April
DISTRICT_DATA_GOSPEL = CSV_DIR / "districts_26apr_gospel.csv"
GOSPEL_DATE = "2020-04-26"
# India testing data
ICMR_TEST_DATA = ROOT_DIR / "data.json"
STATE_TEST_DATA = CSV_DIR / "statewise_tested_numbers_data.csv"
DISTRICT_TEST_DATA = CSV_DIR / "district_testing.csv"
STATE_VACCINATION_DATA = CSV_DIR / "vaccine_doses_statewise_v2.csv"
DISTRICT_VACCINATION_DATA = CSV_DIR / "cowin_vaccine_data_districtwise.csv"

## For adding metadata
# For state notes and last updated
STATE_WISE = ROOT_DIR / "data.json"
# For district notes
DISTRICT_WISE = ROOT_DIR / "state_district_wise.json"

# API outputs
OUTPUT_DIR = ROOT_DIR / "v4"
OUTPUT_MIN_DIR = OUTPUT_DIR / "min"
OUTPUT_DATA_PREFIX = "data"
OUTPUT_TIMESERIES_PREFIX = "timeseries"
# CSV Outputs
OUTPUT_STATES_CSV = CSV_DIR / "states.csv"
OUTPUT_DISTRICTS_CSV = CSV_DIR / "districts.csv"

# Two digit state codes
STATE_CODES = {}
# State codes to state names map (capitalized appropriately)
STATE_NAMES = {}
# State/district populations
STATE_POPULATIONS = {}
DISTRICT_POPULATIONS = defaultdict(dict)
# Code corresponding to MoHFW's 'Unassigned States' in sheet
UNASSIGNED_STATE_CODE = "UN"
# Dict containing geographical districts
DISTRICTS_DICT = defaultdict(dict)
# District key to give to unkown district values in raw_data
UNKNOWN_DISTRICT_KEY = "Unknown"
# States with single district/no district-wise data
SINGLE_DISTRICT_STATES = ["CH", "DL", "LD"]
NO_DISTRICT_DATA_STATES = ["AN", "AS", "GA", "MN", "SK", "TG"]

# Three most important statistics
PRIMARY_STATISTICS = ["confirmed", "recovered", "deceased"]
# Raw data key => Statistics
RAW_DATA_MAP = {
    "hospitalized": "confirmed",
    "recovered": "recovered",
    "deceased": "deceased",
    "migrated_other": "other",
}
ICMR_DATA_DICT = {
    "tested": {
        "key": "totalsamplestested",
        "source": "source"
    },
    "vaccinated1": {
        "key": "firstdoseadministered",
        "source": "source4"
    },
    "vaccinated2": {
        "key": "seconddoseadministered",
        "source": "source4"
    },
}
VACCINATION_DATA_DICT = {
    "vaccinated1": "First Dose Administered",
    "vaccinated2": "Second Dose Administered",
}
ALL_STATISTICS = [*RAW_DATA_MAP.values(), *ICMR_DATA_DICT.keys()]
# CSV Headers
CSV_STATISTIC_HEADERS = {
    "confirmed": "Confirmed",
    "recovered": "Recovered",
    "deceased": "Deceased",
    "other": "Other",
    "tested": "Tested",
}
STATE_CSV_HEADER = ["Date", "State", *CSV_STATISTIC_HEADERS.values()]
DISTRICT_CSV_HEADER = [
    "Date", "State", "District", *CSV_STATISTIC_HEADERS.values()
]
# Skip warning for these states
VACCINATION_SKIP_STATES = {"total", "miscellaneous"}

# Categories to keep in timeseries API
TIMESERIES_TYPES = ["total", "delta", "delta7"]

# Log statements width
PRINT_WIDTH = 70

# Nested default dict of dict
ddict = lambda: defaultdict(ddict)
# Dictionaries which stored final parsed data
data = ddict()
timeseries = ddict()


def parse_state_metadata(raw_data):
  for i, entry in enumerate(raw_data["state_meta_data"]):
    # State name with sheet capitalization
    state_name = entry["stateut"].strip()
    # State code caps
    state_code = entry["abbreviation"].strip().upper()
    STATE_CODES[state_name.lower()] = state_code
    STATE_NAMES[state_code] = state_name
    # State population
    try:
      population = int(entry["population"].strip())
    except ValueError:
      if entry["population"]:
        logging.warning(
            f"[L{i+2}] [Bad population: {entry['population']}] {state_code}")
      continue
    STATE_POPULATIONS[state_code] = population


def parse_district_list(raw_data):
  # Initialize with districts from single district states
  for state in SINGLE_DISTRICT_STATES:
    district = STATE_NAMES[state]
    DISTRICTS_DICT[state][district.lower()] = district
  # Parse from file
  for i, entry in enumerate(raw_data.values()):
    state = entry["statecode"].strip().upper()
    if state not in STATE_CODES.values():
      logging.warning(f"[L{i + 2}] Bad state: {entry['statecode']}")
      continue
    if "districtData" not in entry:
      continue

    for district in entry["districtData"]:
      district = district.strip()
      DISTRICTS_DICT[state][district.lower()] = district


def parse_district(district, state, single_district=True, allow_unknown=True):
  district = district.strip()
  expected = True
  if single_district and state in SINGLE_DISTRICT_STATES:
    district = STATE_NAMES[state]
  elif allow_unknown and state in NO_DISTRICT_DATA_STATES:
    district = UNKNOWN_DISTRICT_KEY
  elif not district or district.lower() == "unknown":
    district = UNKNOWN_DISTRICT_KEY
  elif district.lower() in DISTRICTS_DICT[state]:
    district = DISTRICTS_DICT[state][district.lower()]
  else:
    expected = False
  return district, expected


def parse_district_metadata(raw_data):
  for i, entry in enumerate(raw_data["district_meta_data"]):
    # State code
    state = entry["statecode"].strip().upper()
    if state not in STATE_CODES.values():
      logging.warning(f"[L{i + 2}] Bad state: {state}")
      continue
    # District name with sheet capitalization
    district, expected = parse_district(entry["district"],
                                        state,
                                        single_district=False,
                                        allow_unknown=False)
    if not expected:
      logging.warning(f"[L{i + 2}] [{state}] Unexpected district: {district}")
    # District population
    try:
      population = int(entry["population"].strip())
    except ValueError:
      if entry["population"]:
        logging.warning(
            f"[L{i+2}] [Bad population: {entry['population']}] {state}: {district}"
        )
      continue
    DISTRICT_POPULATIONS[state][district] = population


def inc(ref, key, count):
  if not isinstance(ref[key], int):
    # Initialize with 0
    ref[key] = 0
  # Increment
  ref[key] += count


def parse(raw_data, i):
  for j, entry in enumerate(raw_data["raw_data"]):
    count_str = entry["numcases"].strip()

    if not count_str:
      continue

    state_name = entry["detectedstate"].strip().lower()
    try:
      state = STATE_CODES[state_name]
    except KeyError:
      # Entries with empty state names are discarded
      if state_name:
        # Unrecognized state entries are discarded and logged
        logging.warning(
            f"[L{j+2}] [{entry['dateannounced']}] [Bad state: {entry['detectedstate']}] {entry['numcases']}"
        )
      continue

    try:
      fdate = datetime.strptime(entry["dateannounced"].strip(), "%d/%m/%Y")
      date = datetime.strftime(fdate, "%Y-%m-%d")
      if date < MIN_DATE or date > INDIA_DATE:
        # Entries from future dates will be ignored
        logging.warning(
            f"[L{j+2}] [Future/past date: {entry['dateannounced']}] {entry['detectedstate']}: {entry['detecteddistrict']} {entry['numcases']}"
        )
        continue
    except ValueError:
      # Bad date
      logging.warning(
          f"[L{j+2}] [Bad date: {entry['dateannounced']}] {entry['detectedstate']}: {entry['detecteddistrict']} {entry['numcases']}"
      )
      continue

    district, expected = parse_district(entry["detecteddistrict"], state)
    if not expected:
      # Print unexpected district names
      logging.warning(
          f"[L{j+2}] [{entry['dateannounced']}] [Unexpected district: {district} ({state})] {entry['numcases']}"
      )

    try:
      count = int(count_str)
    except ValueError:
      logging.warning(
          f"[L{j+2}] [{entry['dateannounced']}] [Bad numcases: {entry['numcases']}] {state}: {district}"
      )
      continue

    if count:
      try:
        # All rows in v1 and v2 are confirmed cases
        statistic = ("confirmed" if i < 3 else
                     RAW_DATA_MAP[entry["currentstatus"].strip().lower()])

        inc(data[date]["TT"]["delta"], statistic, count)
        inc(data[date][state]["delta"], statistic, count)
        # Don't parse old district data since it's unreliable
        if (state in SINGLE_DISTRICT_STATES or state in NO_DISTRICT_DATA_STATES
            or
            (i > 2 and date > GOSPEL_DATE and state != UNASSIGNED_STATE_CODE)):
          inc(
              data[date][state]["districts"][district]["delta"],
              statistic,
              count,
          )

      except KeyError:
        # Unrecognized status
        logging.warning(
            f"[L{j+2}] [{entry['dateannounced']}] [Bad currentstatus: {entry['currentstatus']}] {state}: {district} {entry['numcases']}"
        )


def parse_outcome(outcome_data, i):
  for j, entry in enumerate(outcome_data["deaths_recoveries"]):
    state_name = entry["state"].strip().lower()
    try:
      state = STATE_CODES[state_name]
    except KeyError:
      # Entries with empty state names are discarded
      if state_name:
        # Unrecognized state entries are discarded and logged
        logging.warning(
            f"[L{j + 2}] [{entry['date']}] [Bad state: {entry['state']}]")
      continue

    try:
      fdate = datetime.strptime(entry["date"].strip(), "%d/%m/%Y")
      date = datetime.strftime(fdate, "%Y-%m-%d")
      if date < MIN_DATE or date > INDIA_DATE:
        # Entries from future dates will be ignored
        logging.warning(
            f"[L{j + 2}] [Future/past date: {entry['date']}] {state}")
        continue
    except ValueError:
      # Bad date
      logging.warning(f"[L{j + 2}] [Bad date: {entry['date']}] {state}")
      continue

    district, expected = parse_district(entry["district"], state)
    if not expected:
      # Print unexpected district names
      logging.warning(
          f"[L{j+2}] [{entry['date']}] [Unexpected district: {district} ({state})] {entry['numcases']}"
      )

    try:
      statistic = RAW_DATA_MAP[entry["patientstatus"].strip().lower()]

      inc(data[date]["TT"]["delta"], statistic, 1)
      inc(data[date][state]["delta"], statistic, 1)
      if state in SINGLE_DISTRICT_STATES or state in NO_DISTRICT_DATA_STATES:
        inc(data[date][state]["districts"][district]["delta"], statistic, 1)
      ## Don't parse old district data since it's unreliable
      #  inc(data[date][state]['districts'][district]['delta'], statistic,
      #      1)
    except KeyError:
      # Unrecognized status
      logging.warning(
          f"[L{j+2}] [{entry['date']}] [Bad patientstatus: {entry['patientstatus']}] {state}: {district}"
      )


def parse_district_gospel(reader):
  for i, row in enumerate(reader):
    state = row["State_Code"].strip().upper()
    if (state not in STATE_CODES.values() or state in SINGLE_DISTRICT_STATES
        or state in NO_DISTRICT_DATA_STATES):
      if state not in STATE_CODES.values():
        logging.warning(f"[{i + 2}] Bad state: {state}")
      continue
    district, expected = parse_district(row["District"], state)
    if not expected:
      # Print unexpected district names
      logging.warning(f"[{i + 2}] Unexpected district: {state} {district}")

    for statistic in PRIMARY_STATISTICS:
      count = int(row[statistic.capitalize()] or 0)
      if count:
        data[GOSPEL_DATE][state]["districts"][district]["total"][
            statistic] = count


def parse_icmr(icmr_data):
  for j, entry in enumerate(icmr_data["tested"]):
    for statistic, statistic_dict in ICMR_DATA_DICT.items():
      key = statistic_dict["key"]
      count_str = entry[key].strip()

      if not count_str:
        continue

      try:
        fdate = datetime.strptime(entry["testedasof"].strip(), "%d/%m/%Y")
        date = datetime.strftime(fdate, "%Y-%m-%d")
        if date < MIN_DATE or date > INDIA_DATE:
          # Entries from future dates will be ignored and logged
          logging.warning(
              f"[L{j + 2}] [Future/past date: {entry['testedasof']}]")
          continue
      except ValueError:
        # Bad timestamp
        logging.warning(f"[L{j + 2}] [Bad date: {entry['testedasof']}]")
        continue

      try:
        count = int(count_str)
      except ValueError:
        logging.warning(
            f"[L{j + 2}] [{entry['testedasof']}] [Bad {key}: {entry[key]}]")
        continue

      if count:
        data[date]["TT"]["total"][statistic] = count

        # Add source/last updated
        meta_key = ("vaccinated" if statistic
                    in {"vaccinated1", "vaccinated2"} else statistic)
        data[date]["TT"]["meta"][meta_key]["source"] = entry[
            statistic_dict["source"]].strip()
        data[date]["TT"]["meta"][meta_key]["date"] = date


def parse_state_test(reader):
  for j, entry in enumerate(reader):
    count_str = entry["Total Tested"].strip()
    if not count_str:
      continue

    try:
      fdate = datetime.strptime(entry["Updated On"].strip(), "%d/%m/%Y")
      date = datetime.strftime(fdate, "%Y-%m-%d")
      if date < MIN_DATE or date > INDIA_DATE:
        # Entries from future dates will be ignored and logged
        logging.warning(
            f"[L{j+2}] [Future/past date: {entry['Updated On']}] {entry['State']}"
        )
        continue
    except ValueError:
      # Bad date
      logging.warning(
          f"[L{j + 2}] [Bad date: {entry['Updated On']}] {entry['State']}")
      continue

    state_name = entry["State"].strip().lower()
    try:
      state = STATE_CODES[state_name]
    except KeyError:
      # Entries having unrecognized state names are discarded
      logging.warning(
          f"[L{j+2}] [{entry['Updated On']}] [Bad state: {entry['State']}]")
      continue

    try:
      count = int(count_str)
    except ValueError:
      logging.warning(
          f"[L{j+2}] [{entry['Updated On']}] [Bad total tested: {entry['Total Tested']}] {entry['State']}"
      )
      continue

    source = entry["Source1"].strip()

    if count:
      data[date][state]["total"]["tested"] = count
      data[date][state]["meta"]["tested"]["source"] = source
      data[date][state]["meta"]["tested"]["date"] = date
      # Add district entry too for single-district states
      if state in SINGLE_DISTRICT_STATES:
        # District/State name
        district = STATE_NAMES[state]
        data[date][state]["districts"][district]["total"]["tested"] = count
        data[date][state]["districts"][district]["meta"]["tested"][
            "source"] = source
        data[date][state]["districts"][district]["meta"]["tested"][
            "date"] = date


def column_str(n):
  alpha = ""
  while n > 0:
    n, rem = divmod(n - 1, 26)
    alpha = chr(65 + rem) + alpha
  return alpha


def parse_pivot_headers(header1, header2):
  # Parse till the first date
  row_keys = {}
  for j, column in enumerate(header1):
    try:
      fdate = datetime.strptime(column.strip(), "%d/%m/%Y")
      break
    except ValueError:
      row_keys[column.lower()] = j

  # Parse headers in each date
  column_keys = {}
  while j < len(header1) and fdate == datetime.strptime(
      header1[j].strip(), "%d/%m/%Y"):
    column_keys[header2[j].strip().lower()] = j - len(row_keys)
    j += 1

  # Parse dates
  dates = []
  for j in range(len(row_keys), len(header1), len(column_keys)):
    dates.append(None)
    try:
      fdate = datetime.strptime(header1[j].strip(), "%d/%m/%Y")
      date = datetime.strftime(fdate, "%Y-%m-%d")
      if date < MIN_DATE or date > INDIA_DATE:
        # Entries from future dates will be ignored
        logging.warning(
            f"[{column_str(j + 1)}] Future/past date: {header1[j]}")
        continue
      dates[-1] = date
    except ValueError:
      # Bad date
      logging.warning(f"[{column_str(j + 1)}] Bad date: {header1[j]}")
  return row_keys, column_keys, dates


def parse_district_test(reader):
  header1 = next(reader)
  header2 = next(reader)
  row_keys, column_keys, dates = parse_pivot_headers(header1, header2)

  for i, row in enumerate(reader):
    state_name = row[row_keys["state"]].strip().lower()
    try:
      state = STATE_CODES[state_name]
    except KeyError:
      # Entries having unrecognized state names are discarded
      logging.warning(f"[L{i + 3}] Bad state: {row[row_keys['state']]}")
      continue

    if state in SINGLE_DISTRICT_STATES:
      # Skip since value is already added while parsing state data
      continue

    district, expected = parse_district(row[row_keys["district"]],
                                        state,
                                        allow_unknown=False)
    if not expected:
      # Print unexpected district names
      logging.warning(f"[L{i + 3}] Unexpected district: {state} {district}")

    for j1, j2 in enumerate(range(len(row_keys), len(row), len(column_keys))):
      # Date from header
      date = dates[j1]
      if not date:
        continue

      # Tested count
      count_str = row[j2 + column_keys["tested"]].strip()

      try:
        count = int(count_str)
      except ValueError:
        if count_str:
          logging.warning(
              f"[L{i + 3} {column_str(j2 + column_keys['tested'] + 1)}] [{state}: {district}] Bad Tested: {row[j2 + column_keys['tested']]}"
          )
        continue
      # Use Source1 key as source
      source = row[j2 + column_keys["source1"]].strip()
      if count:
        data[date][state]["districts"][district]["total"]["tested"] = count
        #  data[date][state]['districts'][district]['meta']['tested'][
        #      'source'] = source
        data[date][state]["districts"][district]["meta"]["tested"][
            "date"] = date


def parse_state_vaccination(reader):
  for j, entry in enumerate(reader):
    for statistic, key in VACCINATION_DATA_DICT.items():
      count_str = entry[key].strip()

      if not count_str:
        continue

      try:
        fdate = datetime.strptime(entry["Vaccinated As of"].strip(),
                                  "%d/%m/%Y")
        date = datetime.strftime(fdate, "%Y-%m-%d")
        if date < MIN_DATE or date > INDIA_DATE:
          # Entries from future dates will be ignored and logged
          logging.warning(
              f"[L{j+2}] [Future/past date: {entry['Vaccinated As of']}] {entry['State']}"
          )
          continue
      except ValueError:
        # Bad date
        logging.warning(
            f"[L{j + 2}] [Bad date: {entry['Vaccinated As of']}] {entry['State']}"
        )
        continue

      state_name = entry["State"].strip().lower()
      if state_name in VACCINATION_SKIP_STATES:
        continue

      try:
        state = STATE_CODES[state_name]
      except KeyError:
        # Entries having unrecognized state names are discarded
        logging.warning(
            f"[L{j+2}] [{entry['Vaccinated As of']}] [Bad state: {entry['State']}]"
        )
        continue

      try:
        count = int(count_str)
      except ValueError:
        logging.warning(
            f"[L{j+2}] [{entry['Vaccinated As of']}] [Bad {key}: {entry[key]}] {entry['State']}"
        )
        continue

      if count:
        data[date][state]["total"][statistic] = count
        #  data[date][state]["meta"]["vaccinated"]["source"] = source
        data[date][state]["meta"]["vaccinated"]["date"] = date

        # Add district entry too for single-district states
        if state in SINGLE_DISTRICT_STATES:
          # District/State name
          district = STATE_NAMES[state]
          data[date][state]["districts"][district]["total"][statistic] = count
          #  data[date][state]["districts"][district]["meta"]["vaccinated"][
          #      "source"] = source
          data[date][state]["districts"][district]["meta"]["vaccinated"][
              "date"] = date


def parse_district_vaccination(reader):
  header1 = next(reader)
  header2 = next(reader)
  row_keys, column_keys, dates = parse_pivot_headers(header1, header2)

  for i, row in enumerate(reader):
    state = row[row_keys["state_code"]].strip().upper()
    if state not in STATE_CODES.values():
      logging.warning(f"[L{i + 3}] Bad state: {row[row_keys['state_code']]}")
      continue

    if state in SINGLE_DISTRICT_STATES:
      # Skip since value is already added while parsing state data
      continue

    district, expected = parse_district(row[row_keys["district"]],
                                        state,
                                        allow_unknown=False)
    if not expected:
      # Print unexpected district names
      logging.warning(f"[L{i + 3}] Unexpected district: {state} {district}")

    for j1, j2 in enumerate(range(len(row_keys), len(row), len(column_keys))):
      # Date from header
      date = dates[j1]
      if not date:
        continue

      for statistic in VACCINATION_DATA_DICT:
        key = VACCINATION_DATA_DICT[statistic].lower()
        count_str = row[j2 + column_keys[key]].strip()
        try:
          count = int(count_str)
        except ValueError:
          if count_str:
            logging.warning(
                f"[L{i + 3} {column_str(j2 + column_keys[key] + 1)}] [{state}: {district}] Bad {key}: {row[j2 + column_keys[key]]}"
            )
          continue

        if count:
          inc(
              data[date][state]["districts"][district]["total"],
              statistic,
              count,
          )


def contains(raw_data, keys):
  if not keys:
    return True
  elif keys[0] in raw_data:
    return contains(raw_data[keys[0]], keys[1:])
  else:
    return False


def fill_deltas():
  dates = sorted(data)
  for i, date in enumerate(dates):
    curr_data = data[date]

    # Initialize today's delta with today's cumulative
    for state, state_data in curr_data.items():
      for key in ICMR_DATA_DICT:
        if contains(state_data, ["total", key]):
          state_data["delta"][key] = state_data["total"][key]

      if "districts" not in state_data:
        continue

      for district, district_data in state_data["districts"].items():
        for key in ICMR_DATA_DICT:
          if contains(district_data, ["total", key]):
            district_data["delta"][key] = district_data["total"][key]

    if i > 0:
      prev_date = dates[i - 1]
      prev_data = data[prev_date]
      for state, state_data in prev_data.items():
        for key in ICMR_DATA_DICT:
          if contains(state_data, ["total", key]):
            if key in curr_data[state]["total"]:
              # Subtract previous cumulative to get delta
              curr_data[state]["delta"][key] -= state_data["total"][key]
            else:
              # Take today's cumulative to be same as yesterday's
              # cumulative if today's cumulative is missing
              curr_data[state]["total"][key] = state_data["total"][key]
              curr_data[state]["meta"][key]["source"] = state_data["meta"][
                  key]["source"]
              curr_data[state]["meta"][key]["date"] = state_data["meta"][key][
                  "date"]

        if "districts" not in state_data:
          continue

        for district, district_data in state_data["districts"].items():
          for key in ICMR_DATA_DICT:
            if contains(district_data, ["total", key]):
              if key in curr_data[state]["districts"][district]["total"]:
                # Subtract previous cumulative to get delta
                curr_data[state]["districts"][district]["delta"][
                    key] -= district_data["total"][key]
              else:
                # Take today's cumulative to be same as yesterday's
                # cumulative if today's cumulative is missing
                curr_data[state]["districts"][district]["total"][
                    key] = district_data["total"][key]
                curr_data[state]["districts"][district]["meta"][key][
                    "source"] = district_data["meta"][key]["source"]
                curr_data[state]["districts"][district]["meta"][key][
                    "date"] = district_data["meta"][key]["date"]


def accumulate(start_after_date=MIN_DATE, end_date="3020-01-30"):
  # Cumulate daily delta values into total
  dates = sorted(data)
  for i, date in enumerate(dates):
    if date <= start_after_date:
      continue
    elif date > end_date:
      break
    curr_data = data[date]

    if i > 0:
      # Initialize today's cumulative with previous available
      prev_date = dates[i - 1]
      prev_data = data[prev_date]
      for state, state_data in prev_data.items():
        for statistic in RAW_DATA_MAP.values():
          if statistic in state_data["total"]:
            inc(
                curr_data[state]["total"],
                statistic,
                state_data["total"][statistic],
            )

        if (state not in SINGLE_DISTRICT_STATES
            and state not in NO_DISTRICT_DATA_STATES
            and ("districts" not in state_data or date <= GOSPEL_DATE)):
          # Old district data is already accumulated
          continue

        for district, district_data in state_data["districts"].items():
          for statistic in RAW_DATA_MAP.values():
            if statistic in district_data["total"]:
              inc(
                  curr_data[state]["districts"][district]["total"],
                  statistic,
                  district_data["total"][statistic],
              )

    # Add today's dailys to today's cumulative
    for state, state_data in curr_data.items():
      if "delta" in state_data:
        for statistic in RAW_DATA_MAP.values():
          if statistic in state_data["delta"]:
            inc(
                state_data["total"],
                statistic,
                state_data["delta"][statistic],
            )

        if (state not in SINGLE_DISTRICT_STATES
            and state not in NO_DISTRICT_DATA_STATES
            and ("districts" not in state_data or date <= GOSPEL_DATE)):
          # Old district data is already accumulated
          continue

        for district, district_data in state_data["districts"].items():
          if "delta" in district_data:
            for statistic in RAW_DATA_MAP.values():
              if statistic in district_data["delta"]:
                inc(
                    district_data["total"],
                    statistic,
                    district_data["delta"][statistic],
                )


def fill_gospel_unknown():
  # Gospel doesn't contain unknowns
  # Fill them based on gospel date state counts
  curr_data = data[GOSPEL_DATE]
  for state, state_data in curr_data.items():
    if "districts" not in state_data or "total" not in state_data:
      # State had no cases yet
      continue

    sum_district_totals = defaultdict(lambda: 0)
    for district, district_data in state_data["districts"].items():
      if "total" in district_data:
        for statistic, count in district_data["total"].items():
          if statistic in PRIMARY_STATISTICS:
            sum_district_totals[statistic] += count

    for statistic in PRIMARY_STATISTICS:
      if statistic in state_data["total"]:
        count = state_data["total"][statistic]
        if count != sum_district_totals[statistic]:
          # Counts don't match
          # We take Unknown district values = State - Sum(districts gospel)
          state_data["districts"][UNKNOWN_DISTRICT_KEY]["total"][statistic] = (
              count - sum_district_totals[statistic])


def accumulate_days(num_days, offset=0, statistics=ALL_STATISTICS):
  # Cumulate num_day delta values
  for date in data:
    curr_data = data[date]

    fdate = datetime.strptime(date, "%Y-%m-%d")
    dates = [
        datetime.strftime(fdate - timedelta(days=x), "%Y-%m-%d")
        for x in range(offset, num_days)
    ]
    key = f"delta{num_days}"
    if offset > 0:
      key = f"{key}_{offset}"
    for prev_date in dates:
      if prev_date in data:
        prev_data = data[prev_date]
        for state, state_data in prev_data.items():
          if "delta" in state_data:
            for statistic in statistics:
              if statistic in state_data["delta"]:
                inc(
                    curr_data[state][key],
                    statistic,
                    state_data["delta"][statistic],
                )

          if (state not in SINGLE_DISTRICT_STATES
              and state not in NO_DISTRICT_DATA_STATES
              and ("districts" not in state_data or date <= GOSPEL_DATE)):
            # Old district data is already accumulated
            continue

          for district, district_data in state_data["districts"].items():
            if "delta" in district_data:
              for statistic in statistics:
                if statistic in district_data["delta"]:
                  inc(
                      curr_data[state]["districts"][district][key],
                      statistic,
                      district_data["delta"][statistic],
                  )


def stripper(raw_data, dtype=ddict):
  # Remove empty entries
  new_data = dtype()
  for k, v in raw_data.items():
    if isinstance(v, dict):
      v = stripper(v, dtype)
    if v:
      new_data[k] = v
  return new_data


def add_populations():
  # Add population data for states/districts
  for curr_data in data.values():
    for state, state_data in curr_data.items():
      try:
        state_pop = STATE_POPULATIONS[state]
        state_data["meta"]["population"] = state_pop
      except KeyError:
        pass

      if "districts" not in state_data:
        continue

      for district, district_data in state_data["districts"].items():
        try:
          district_pop = DISTRICT_POPULATIONS[state][district]
          district_data["meta"]["population"] = district_pop
        except KeyError:
          pass


def trim_timeseries():
  for state_data in timeseries.values():
    if "dates" in state_data:
      dates = list(state_data["dates"])
      for date in sorted(dates, reverse=True):
        if "delta" in state_data["dates"][date]:
          last_date = date
          break
      for date in dates:
        if date > last_date:
          del state_data["dates"][date]

    if "districts" in state_data:
      for district_data in state_data["districts"].values():
        if "dates" in district_data:
          dates = list(district_data["dates"])
          for date in sorted(dates, reverse=True):
            if "delta" in district_data["dates"][date]:
              last_date = date
              break
          for date in dates:
            if date > last_date:
              del district_data["dates"][date]


def generate_timeseries(districts=False):
  for date in sorted(data):
    curr_data = data[date]

    for state, state_data in curr_data.items():
      for stype in TIMESERIES_TYPES:
        if stype in state_data:
          for statistic, value in state_data[stype].items():
            timeseries[state]["dates"][date][stype][statistic] = value

      if not districts or "districts" not in state_data or date < GOSPEL_DATE:
        # Total state has no district data
        # District timeseries starts only from 26th April
        continue

      for district, district_data in state_data["districts"].items():
        for stype in TIMESERIES_TYPES:
          if stype in district_data:
            for statistic, value in district_data[stype].items():
              timeseries[state]["districts"][district]["dates"][date][stype][
                  statistic] = value
  trim_timeseries()


def add_state_meta(raw_data):
  last_date = sorted(data)[-1]
  last_data = data[last_date]
  for j, entry in enumerate(raw_data["statewise"]):
    state = entry["statecode"].strip().upper()
    if state not in STATE_CODES.values() or state not in last_data:
      # Entries having unrecognized state codes/zero cases are discarded
      if state not in STATE_CODES.values():
        logging.warning(
            f"[L{j+2}] [{entry['lastupdatedtime']}] Bad state: {entry['statecode']}"
        )
      continue

    try:
      fdate = datetime.strptime(entry["lastupdatedtime"].strip(),
                                "%d/%m/%Y %H:%M:%S")
    except ValueError:
      # Bad timestamp
      logging.warning(
          f"[L{j + 2}] [Bad timestamp: {entry['lastupdatedtime']}] {state}")
      continue

    last_data[state]["meta"]["date"] = last_date
    last_data[state]["meta"]["last_updated"] = fdate.isoformat(
    ) + INDIA_UTC_OFFSET
    if entry["statenotes"]:
      last_data[state]["meta"]["notes"] = entry["statenotes"].strip()


def add_district_meta(raw_data):
  last_data = data[sorted(data)[-1]]
  for j, entry in enumerate(raw_data.values()):
    state = entry["statecode"].strip().upper()
    if (state not in STATE_CODES.values() or state in SINGLE_DISTRICT_STATES
        or state in NO_DISTRICT_DATA_STATES):
      # Entries having unrecognized state codes are discarded
      if state not in STATE_CODES.values():
        logging.warning(f"[L{j + 2}] Bad state: {entry['statecode']}")
      continue

    for district, district_data in entry["districtData"].items():
      district, expected = parse_district(district, state)
      if not expected:
        logging.warning(f"[L{j + 2}] Unexpected district: {state} {district}")

      if district_data["notes"]:
        last_data[state]["districts"][district]["meta"][
            "notes"] = district_data["notes"].strip()


def tally_statewise(raw_data):
  last_data = data[sorted(data)[-1]]
  # Check for extra entries
  logging.info("Checking for extra entries...")
  for state, state_data in last_data.items():
    found = False
    for entry in raw_data["statewise"]:
      if state == entry["statecode"].strip().upper():
        found = True
        break
    if not found:
      logging.warning(yaml.dump(stripper({state: state_data}, dtype=dict)))
  logging.info("Done!")

  # Tally counts of entries present in statewise
  logging.info("Tallying final date counts...")
  for j, entry in enumerate(raw_data["statewise"]):
    state = entry["statecode"].strip().upper()
    if state not in STATE_CODES.values():
      continue

    try:
      fdate = datetime.strptime(entry["lastupdatedtime"].strip(),
                                "%d/%m/%Y %H:%M:%S")
    except ValueError:
      # Bad timestamp
      logging.warning(
          f"[L{j + 2}] [Bad timestamp: {entry['lastupdatedtime']}] {state}")
      continue

    for statistic in PRIMARY_STATISTICS:
      try:
        values = {
            "total":
            int(entry[statistic if statistic != "deceased" else "deaths"].
                strip()),
            "delta":
            int(entry["delta" + (
                statistic if statistic != "deceased" else "deaths").strip()]),
        }
      except ValueError:
        logging.warning(
            f"[L{j+2}] [{entry['lastupdatedtime']}] [Bad value for {statistic}] {state}"
        )
        continue

      for stype in ["total", "delta"]:
        if values[stype]:
          parsed_value = last_data[state][stype][statistic]
          if not isinstance(parsed_value, int):
            parsed_value = 0
          if values[stype] != parsed_value:
            # Print mismatch between statewise and parser
            logging.warning(
                f"{state} {statistic} {stype}: (sheet: {values[stype]}, parser: {parsed_value})"
            )


def tally_districtwise(raw_data):
  last_data = data[sorted(data)[-1]]
  # Check for extra entries
  logging.info("Checking for extra entries...")
  for state, state_data in last_data.items():
    if ("districts" not in state_data or state in SINGLE_DISTRICT_STATES
        or state in NO_DISTRICT_DATA_STATES):
      continue
    state_name = STATE_NAMES[state]
    if state_name in raw_data:
      for district, district_data in state_data["districts"].items():
        found = False
        for entryDistrict in raw_data[state_name]["districtData"].keys():
          entryDistrict, _ = parse_district(entryDistrict, state)
          if district == entryDistrict:
            found = True
            break
        if not found and (set(district_data["total"]) | set(
            district_data["delta"])) & set(PRIMARY_STATISTICS):
          # Not found in districtwise sheet
          key = f"{district} ({state})"
          logging.warning(yaml.dump(stripper({key: district_data},
                                             dtype=dict)))
    else:
      logging.warning(yaml.dump(stripper({state: state_data}, dtype=dict)))
  logging.info("Done!")

  # Tally counts of entries present in districtwise
  logging.info("Tallying final date counts...")
  for j, entry in enumerate(raw_data.values()):
    state = entry["statecode"].strip().upper()
    if (state not in STATE_CODES.values() or state == UNASSIGNED_STATE_CODE
        or state in SINGLE_DISTRICT_STATES
        or state in NO_DISTRICT_DATA_STATES):
      continue

    for district, district_data in entry["districtData"].items():
      district, _ = parse_district(district, state)
      for statistic in PRIMARY_STATISTICS:
        values = {
            "total": district_data[statistic],
            "delta": district_data["delta"][statistic],
        }
        for stype in ["total", "delta"]:
          if values[stype]:
            parsed_value = last_data[state]["districts"][district][stype][
                statistic]
            if not isinstance(parsed_value, int):
              parsed_value = 0
            if values[stype] != parsed_value:
              # Print mismatch between districtwise and parser
              logging.warning(
                  f"{state} {district} {statistic} {stype}: (sheet: {values[stype]}, parser: {parsed_value})"
              )


def write_csvs(writer_states, writer_districts):
  # Write header rows
  writer_states.writerow(STATE_CSV_HEADER)
  writer_districts.writerow(DISTRICT_CSV_HEADER)
  for date in sorted(data):
    curr_data = data[date]

    for state in sorted(curr_data):
      state_data = curr_data[state]
      # Date, State, Confirmed, Recovered, Deceased, Other, Tested
      if set(state_data["total"]) & set(CSV_STATISTIC_HEADERS):
        row = [
            date,
            STATE_NAMES[state],
            state_data["total"]["confirmed"] or 0,
            state_data["total"]["recovered"] or 0,
            state_data["total"]["deceased"] or 0,
            state_data["total"]["other"] or 0,
            state_data["total"]["tested"] or "",
        ]
        writer_states.writerow(row)

      if "districts" not in state_data or date < GOSPEL_DATE:
        # Total state has no district data
        # District timeseries starts only from 26th April
        continue

      for district in sorted(state_data["districts"]):
        district_data = state_data["districts"][district]
        if set(district_data["total"]) & set(CSV_STATISTIC_HEADERS):
          # Date, State, District, Confirmed, Recovered, Deceased, Other, Tested
          row = [
              date,
              STATE_NAMES[state],
              district,
              district_data["total"]["confirmed"] or 0,
              district_data["total"]["recovered"] or 0,
              district_data["total"]["deceased"] or 0,
              district_data["total"]["other"] or 0,
              district_data["total"]["tested"] or "",
          ]
          writer_districts.writerow(row)


if __name__ == "__main__":
  logging.info("-" * PRINT_WIDTH)
  logging.info("PARSER V4 START".center(PRINT_WIDTH))

  # Get possible state codes, populations
  logging.info("-" * PRINT_WIDTH)
  logging.info("Parsing state metadata...")
  with open(META_DATA) as f:
    logging.info(f"File: {META_DATA.name}")
    raw_data = json.load(f)
    parse_state_metadata(raw_data)
  logging.info("Done!")

  # Get all actual district names
  logging.info("-" * PRINT_WIDTH)
  logging.info("Parsing districts list...")
  with open(DISTRICT_LIST) as f:
    logging.info(f"File: {DISTRICT_LIST.name}")
    raw_data = json.load(f)
    parse_district_list(raw_data)
  logging.info("Done!")

  # Get district populations
  logging.info("-" * PRINT_WIDTH)
  logging.info("Parsing district metadata...")
  with open(META_DATA) as f:
    logging.info(f"File: {META_DATA.name}")
    raw_data = json.load(f)
    parse_district_metadata(raw_data)
  logging.info("Done!")

  # Parse raw_data's
  logging.info("-" * PRINT_WIDTH)
  logging.info("Parsing raw_data...")
  i = 1
  while True:
    fn = ROOT_DIR / RAW_DATA.format(n=i)
    if not fn.is_file():
      break
    with open(fn) as f:
      logging.info(f"File: {fn.name}")
      raw_data = json.load(f)
      parse(raw_data, i)
    i += 1
  logging.info("Done!")

  # Parse additional deceased/recovered info not in raw_data 1 and 2
  logging.info("-" * PRINT_WIDTH)
  logging.info("Parsing deaths_recoveries...")
  for i in [1, 2]:
    fn = ROOT_DIR / OUTCOME_DATA.format(n=i)
    with open(fn) as f:
      logging.info(f"File: {fn.name}")
      raw_data = json.load(f)
      parse_outcome(raw_data, i)
  logging.info("Done!")

  logging.info("-" * PRINT_WIDTH)
  logging.info("Adding district data for 26th April...")
  # Parse gospel district data for 26th April
  with open(DISTRICT_DATA_GOSPEL) as f:
    logging.info(f"File: {DISTRICT_DATA_GOSPEL.name}")
    reader = csv.DictReader(f)
    parse_district_gospel(reader)
  logging.info("Done!")

  logging.info("-" * PRINT_WIDTH)
  logging.info("Parsing ICMR test data for India...")
  with open(ICMR_TEST_DATA) as f:
    logging.info(f"File: {ICMR_TEST_DATA.name}")
    raw_data = json.load(f, object_pairs_hook=OrderedDict)
    parse_icmr(raw_data)
  logging.info("Done!")

  logging.info("-" * PRINT_WIDTH)
  logging.info("Parsing test data for all states...")
  with open(STATE_TEST_DATA) as f:
    logging.info(f"File: {STATE_TEST_DATA.name}")
    reader = csv.DictReader(f)
    parse_state_test(reader)
  logging.info("Done!")

  logging.info("-" * PRINT_WIDTH)
  logging.info("Parsing test data for districts...")
  with open(DISTRICT_TEST_DATA) as f:
    logging.info(f"File: {DISTRICT_TEST_DATA.name}")
    reader = csv.reader(f)
    parse_district_test(reader)
  logging.info("Done!")

  logging.info("-" * PRINT_WIDTH)
  logging.info("Parsing vaccination data for states...")
  with open(STATE_VACCINATION_DATA) as f:
    logging.info(f"File: {STATE_VACCINATION_DATA.name}")
    reader = csv.DictReader(f)
    parse_state_vaccination(reader)
  logging.info("Done!")

  logging.info("-" * PRINT_WIDTH)
  logging.info("Parsing vaccination data for districts...")
  with open(DISTRICT_VACCINATION_DATA) as f:
    logging.info(f"File: {DISTRICT_VACCINATION_DATA.name}")
    reader = csv.reader(f)
    parse_district_vaccination(reader)
  logging.info("Done!")

  # Fill delta values for tested
  logging.info("-" * PRINT_WIDTH)
  logging.info("Generating daily tested/vaccinated values...")
  fill_deltas()
  logging.info("Done!")

  # Generate total (cumulative) data points till 26th April
  logging.info("-" * PRINT_WIDTH)
  logging.info("Generating cumulative CRD values till 26th April...")
  accumulate(end_date=GOSPEL_DATE)
  logging.info("Done!")

  # Fill Unknown district counts for 26th April
  logging.info("-" * PRINT_WIDTH)
  logging.info(f"Filling {UNKNOWN_DISTRICT_KEY} data for 26th April...")
  fill_gospel_unknown()
  logging.info("Done!")

  # Generate rest of total (cumulative) data points
  logging.info("-" * PRINT_WIDTH)
  logging.info(
      "Generating cumulative CRD values from 26th April afterwards...")
  accumulate(start_after_date=GOSPEL_DATE)
  logging.info("Done!")

  # Generate 7 day delta values
  logging.info("-" * PRINT_WIDTH)
  logging.info("Generating 7-day delta values...")
  accumulate_days(7)
  logging.info("Done!")

  # Generate 14-21 day confirmed delta values
  logging.info("-" * PRINT_WIDTH)
  logging.info("Generating 14-21 day confirmed delta values...")
  accumulate_days(21, offset=14, statistics=["confirmed"])
  logging.info("Done!")

  # Strip empty values ({}, 0, '', None)
  data = stripper(data)

  # Add population figures
  logging.info("-" * PRINT_WIDTH)
  logging.info("Adding state/district populations...")
  add_populations()
  logging.info("Done!")

  # Generate timeseries
  logging.info("-" * PRINT_WIDTH)
  logging.info("Generating timeseries...")
  generate_timeseries(districts=True)
  logging.info("Done!")

  logging.info("-" * PRINT_WIDTH)
  logging.info("Adding state and district metadata...")
  with open(STATE_WISE) as f:
    logging.info(f"File: {STATE_WISE.name}")
    raw_data = json.load(f, object_pairs_hook=OrderedDict)
    add_state_meta(raw_data)

  with open(DISTRICT_WISE) as f:
    logging.info(f"File: {DISTRICT_WISE.name}")
    raw_data = json.load(f, object_pairs_hook=OrderedDict)
    add_district_meta(raw_data)
  logging.info("Done!")

  logging.info("-" * PRINT_WIDTH)
  logging.info("Dumping JSON APIs...")
  OUTPUT_MIN_DIR.mkdir(parents=True, exist_ok=True)

  # Dump prettified full data json
  fn = f"{OUTPUT_DATA_PREFIX}-all"
  # Only dump minified data-all.json
  #  with open((OUTPUT_DIR / fn).with_suffix('.json'), 'w') as f:
  #    json.dump(data, f, indent=2, sort_keys=True)
  # Dump minified full data
  with open((OUTPUT_MIN_DIR / fn).with_suffix(".min.json"), "w") as f:
    json.dump(data, f, separators=(",", ":"), sort_keys=True)

  # Split data and dump separate json for each date
  for i, date in enumerate(sorted(data)):
    curr_data = data[date]
    if i < len(data) - 1:
      fn = f"{OUTPUT_DATA_PREFIX}-{date}"
    else:
      fn = OUTPUT_DATA_PREFIX

    with open((OUTPUT_DIR / fn).with_suffix(".json"), "w") as f:
      json.dump(curr_data, f, indent=2, sort_keys=True)
    # Minified
    with open((OUTPUT_MIN_DIR / fn).with_suffix(".min.json"), "w") as f:
      json.dump(curr_data, f, separators=(",", ":"), sort_keys=True)

  # Dump full timeseries json
  fn = f"{OUTPUT_TIMESERIES_PREFIX}-all"
  # Only dump minified timeseries-all.json
  #  with open((OUTPUT_DIR / fn).with_suffix('.json'), 'w') as f:
  #    json.dump(timeseries, f, indent=2, sort_keys=True)
  with open((OUTPUT_MIN_DIR / fn).with_suffix(".min.json"), "w") as f:
    json.dump(timeseries, f, separators=(",", ":"), sort_keys=True)

  # Dump state timeseries json
  fn = OUTPUT_TIMESERIES_PREFIX
  # Filter out district time-series
  timeseries_states = {
      state: {
          "dates": timeseries[state]["dates"]
      }
      for state in timeseries
  }
  with open((OUTPUT_DIR / fn).with_suffix(".json"), "w") as f:
    json.dump(timeseries_states, f, indent=2, sort_keys=True)
  with open((OUTPUT_MIN_DIR / fn).with_suffix(".min.json"), "w") as f:
    json.dump(timeseries_states, f, separators=(",", ":"), sort_keys=True)

  # Split data and dump separate json for each state
  for state in timeseries:
    if state == UNASSIGNED_STATE_CODE:
      continue
    state_data = {state: timeseries[state]}
    fn = f"{OUTPUT_TIMESERIES_PREFIX}-{state}"

    with open((OUTPUT_DIR / fn).with_suffix(".json"), "w") as f:
      json.dump(state_data, f, indent=2, sort_keys=True)
    # Minified
    with open((OUTPUT_MIN_DIR / fn).with_suffix(".min.json"), "w") as f:
      json.dump(state_data, f, separators=(",", ":"), sort_keys=True)
  logging.info("Done!")

  # Tally final date counts with statewise API
  logging.info("-" * PRINT_WIDTH)
  logging.info("Comparing data with statewise sheet...")
  with open(STATE_WISE) as f:
    logging.info(f"File: {STATE_WISE.name}")
    raw_data = json.load(f, object_pairs_hook=OrderedDict)
    tally_statewise(raw_data)
  logging.info("Done!")

  # Tally final date counts with districtwise API
  logging.info("-" * PRINT_WIDTH)
  logging.info("Comparing data with districtwise sheet...")
  with open(DISTRICT_WISE) as f:
    logging.info(f"File: {DISTRICT_WISE.name}")
    raw_data = json.load(f, object_pairs_hook=OrderedDict)
    tally_districtwise(raw_data)
  logging.info("Done!")

  # Dump state/district CSVs
  logging.info("-" * PRINT_WIDTH)
  logging.info("Dumping CSVs...")
  with open(OUTPUT_STATES_CSV, "w") as f1:
    writer1 = csv.writer(f1)
    with open(OUTPUT_DISTRICTS_CSV, "w") as f2:
      writer2 = csv.writer(f2)
      write_csvs(writer1, writer2)
  logging.info("Done!")

  logging.info("-" * PRINT_WIDTH)
  logging.info("PARSER V4 END".center(PRINT_WIDTH))
  logging.info("-" * PRINT_WIDTH)
