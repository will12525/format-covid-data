import csv
import requests
import json
import abv_to_state as states_abv
import pprint
import matplotlib.pyplot as plt
from datetime import datetime

pp = pprint.PrettyPrinter(indent=4)


def from_url():
    url = "https://covidtracking.com/api/us/daily"
    url_data = requests.get(url=url).json()
    with open('us_daily.json', 'w') as outfile:
        json.dump(url_data, outfile)
    return url_data


def from_file():
    with open("us_daily.json") as data_file:
        return json.load(data_file)


def get_ratio(value, prev):
    if value is None:
        value = 0
    if prev != 0 and prev is not None:
        ratio = round((value - prev) / prev, 2)
    else:
        ratio = value
    prev = value

    return prev, ratio


def export_csv(historical_records):
    fields = ["Time", "positive", "negative", "death", "tests", "positive difference", "negative difference",
              "death difference", "testing difference"]
    csv_records = [fields]
    prev_pos = 0
    prev_neg = 0
    prev_death = 0
    prev_test = 0
    for record in historical_records:
        date_checked = datetime.strptime(record["dateChecked"], '%Y-%m-%dT%H:%M:%SZ')
        positive = record["positive"]
        negative = record["negative"]
        death = record["death"]
        total_tested = record["totalTestResults"]

        if date_checked is None:
            continue

        prev_pos, positive_ratio = get_ratio(positive, prev_pos)
        prev_neg, negative_ratio = get_ratio(negative, prev_neg)
        prev_death, death_ratio = get_ratio(death, prev_death)
        prev_test, test_ratio = get_ratio(total_tested, prev_test)

        record_data = [record["dateChecked"], positive, negative, death, total_tested, positive_ratio, negative_ratio,
                       death_ratio, test_ratio]

        csv_records.append(record_data)

    with open("us_formatted_data.csv", 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerows(csv_records)
    print("Exported")


data = from_url()
print("Done get")
historicalRecords = []
plt.rc('grid', linestyle="-", color='black')

for item in data:
    historicalRecords.insert(0, item)

print("Done sort")
export_csv(historicalRecords)

#pp.pprint(historicalRecords)