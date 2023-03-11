import requests
from bs4 import BeautifulSoup
import json
from argparse import ArgumentParser
from datetime import datetime

today = datetime.now()
print("Today is {}".format(today))

month_dict = {
    "1": "01 - January",
    "2": "02 - February",
    "3": "03 - March",
    "4": "04 - April",
    "5": "05 - May",
    "6": "06 - June",
    "7": "07 - Juny",
    "8": "08 - August",
    "9": "09 - September",
    "10": "10 - October",
    "11": "11 - November",
    "12": "12 - December",
}

today = datetime.now()

parser = ArgumentParser()

parser.add_argument("-y", "--year", default=str(today.year))
parser.add_argument("-m", "--month", default=str(today.month))

args = parser.parse_args()

target_year = str(args.year)

print("Grabbing year links for {}".format(target_year))

year_res = requests.get(
    "https://circabc.europa.eu/service/circabc/spaces/ac2dee97-426f-4d5f-a63a-7d8760f29513/children?language=en&guest=true&limit=10&page=1&order=modified_DESC&folderOnly=false&fileOnly=false"
)

for item in year_res.json()["data"]:
    if item["name"] == target_year:
        year_id = item["id"]


target_month = month_dict[str(args.month)]
target_month_name = target_month.split(" ")[-1]

print("Grabbing month links for {}".format(target_month_name))

first_res = requests.get(
    "https://circabc.europa.eu/service/circabc/spaces/{}/subspaces?language=&sort=title&order=ASC&guest=true".format(
        year_id
    )
)


for item in first_res.json():
    if item["name"] == target_month:
        month_id = item["id"]


print("Grabbing tariff data for {}-{}".format(target_month_name, target_year))

res = requests.get(
    "https://circabc.europa.eu/service/circabc/spaces/{}/children?language=en&guest=true&limit=10&page=1&order=modified_DESC&folderOnly=false&fileOnly=false".format(
        month_id
    )
)


data = res.json()["data"]


for item in data:
    if item["name"] == "Duties Import 01-99.xlsx":
        data_id = item["id"]

url = "https://circabc.europa.eu/rest/download/{}?ticket=".format(data_id)
data = requests.get(url).content
f = open(
    "data/tariff_download_{}_{}.xlsx".format(target_year, target_month_name.lower()),
    "wb",
)
f.write(data)
f.close()
print(
    "Done, stored tariff_download_{}_{}.xlsx in /data".format(
        target_year, target_month_name.lower()
    )
)
