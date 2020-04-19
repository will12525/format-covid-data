import csv
import requests
import json
import abv_to_state as states_abv
import pprint
import matplotlib.pyplot as plt
from datetime import datetime

pp = pprint.PrettyPrinter(indent=4)


def from_url():
    url = "https://covidtracking.com/api/states/daily"
    url_data = requests.get(url=url).json()
    with open('states_daily.json', 'w') as outfile:
        json.dump(url_data, outfile)
    return url_data


def from_file():
    with open("states_daily.json") as data_file:
        return json.load(data_file)


def line_positives(historical_records):
    for key in historical_records:
        if key not in ("ME"):
            continue
        state_records = historical_records[key]
        x = []
        y = []
        for record in state_records:
            date_checked = datetime.strptime(record["dateChecked"], '%Y-%m-%dT%H:%M:%SZ')
            loc = checked_dates.index(date_checked)
            x.append(loc)
            y.append(record["positive"])
        plt.plot(x, y, label=key)
    plt.grid(True)
    plt.legend()
    plt.show()


def bar_positives(historical_records):
    count = 0
    for key in historical_records:
        if key in ("NY", "NJ"):
            continue
        state_records = historical_records[key]
        x = []
        y = []
        for record in state_records:
            date_checked = datetime.strptime(record["dateChecked"], '%Y-%m-%dT%H:%M:%SZ')
            loc = checked_dates.index(date_checked)

            x.append(loc)
            y.append(record["positive"])

        new = len(y)
        r = [count] * new
        try:
            plt.bar(r, y, width=2, color=(0.4, 0.0, 0.1, 0.1), label=key)
            labels.append(key)
            count += 2
        except:
            # No data exists, Aka: Samoa
            print(states_abv.states[key])
            continue

    plt.title("Positives over time per state")
    r = [x * 2 for x in range(len(labels))]
    plt.xticks(r, labels, rotation=90)
    plt.grid(True)
    plt.show()


def get_ratio(value, prev):
    if value is None:
        value = 0
    if prev != 0 and prev is not None:
        ratio = round((value - prev) / prev, 2)
    else:
        ratio = value
    prev = value

    return prev, ratio


def export_csv(historical_records, checked_dates):
    fields = ["Time", "positive", "negative", "death", "tests", "positive difference", "negative difference",
              "death difference", "testing difference"]
    csv_records = [None] * (len(checked_dates) + 1)
    print(csv_records)
    for key in historical_records:
        # if key not in ("TX", "MA"):
        #    continue

        # Append field titles for each section
        if csv_records[0] is None:
            csv_records[0] = [key]
            csv_records[0] += fields
        else:
            csv_records[0] += [key]
            csv_records[0] += fields

        state_records = historical_records[key]
        prev_pos = 0
        prev_neg = 0
        prev_death = 0
        prev_test = 0
        record_locations_added = [0] * (len(checked_dates))
        # Sort through each states records
        for record in state_records:
            date_checked = datetime.strptime(record.get("dateChecked", ""), '%Y-%m-%dT%H:%M:%SZ')
            positive = record.get("positive", 0)
            negative = record.get("negative", 0)
            death = record.get("death", 0)
            total_tested = record["totalTestResults"]

            # Assign defaults instead of None
            if date_checked is None:
                continue

            prev_pos, positive_ratio = get_ratio(positive, prev_pos)
            prev_neg, negative_ratio = get_ratio(negative, prev_neg)
            prev_death, death_ratio = get_ratio(death, prev_death)
            prev_test, test_ratio = get_ratio(total_tested, prev_test)

            record_data = ["", record["dateChecked"], positive, negative, death, total_tested, positive_ratio,
                           negative_ratio,
                           death_ratio, test_ratio]
            loc = checked_dates.index(date_checked) + 1
            record_locations_added[loc - 1] = 1
            # Append data row to csv list for state
            if csv_records[loc] is None:
                csv_records[loc] = record_data
            else:
                csv_records[loc] += record_data

        # Append empty rows if if no data was added
        for i in range(len(record_locations_added)):
            if record_locations_added[i] == 0:
                if csv_records[i + 1] is None:
                    csv_records[i + 1] = [""]
                    csv_records[i + 1] += [0] * len(fields)
                else:
                    csv_records[i + 1] += [""]
                    csv_records[i + 1] += [0] * len(fields)

    with open("state_formatted_data.csv", 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerows(csv_records)


data = from_url()
print("Done get")
historicalRecords = dict()
checked_dates = []
labels = []
plt.rc('grid', linestyle="-", color='black')

for i in range(len(data)):
    state = data[i]
    if state["state"] in historicalRecords.keys():
        historicalRecords[state["state"]].insert(0, state)
    else:
        historicalRecords[state["state"]] = [state]
print("Done sort")

# pp.pprint(historicalRecords["NY"][11])
# quit()
for key in historicalRecords:
    state_historical_records = historicalRecords[key]
    for record in state_historical_records:
        date_checked = datetime.strptime(record["dateChecked"], '%Y-%m-%dT%H:%M:%SZ')
        loc = 0
        if date_checked not in checked_dates:
            for i in range(len(checked_dates)):
                if date_checked < checked_dates[i]:
                    loc = i
                    break
                else:
                    loc = i + 1
            if loc == -1:
                loc = 0
            checked_dates.insert(loc, date_checked)

print("Done dates")

#line_positives(historicalRecords)
export_csv(historicalRecords, checked_dates)

