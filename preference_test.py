import requests
import pandas as pd


res = requests.get("https://trade.ec.europa.eu/access-to-markets/api/tariffs/get/7326909890/CA/SE?lang=EN").json()
print(res[0]["measures"])

for key in res[0]:
    print(key)


df = pd.DataFrame(res[0]["measures"])
print(df.columns)

print(df.loc[:,["type","measureType"]])

