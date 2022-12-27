import pandas as pd
import numpy as np
import sys
import requests
from crepe import TariffData


def import_file(name,type = "csv"):
    if type == "csv":
        df = pd.read_csv(name)

    else:

        df = pd.read_excel(name)
    return df

def fix_percentage(x):
    return float(x.replace(" %",""))

def clean_data(df):
    df = df.rename(columns = {" Measure type":"measure_type"})
    df = df.loc[(df.Origin  == "ERGA OMNES") & (df.measure_type == "Third country duty"),:]
    df =  df.loc[:,["Goods code","Duty","Origin code"]].rename(columns = {"Goods code":"product_code","Duty":"duty","Orgin code":"origin_code"})

    #df.loc[:,"duty"] = df.duty.apply(lambda x : fix_percentage(x))
    return df

def main():
    df = import_file("data/duty.csv")
    df = clean_data(df)
    print(df)

    print(df.loc[df.product_code == 3824999390,:])
    print(len(df.product_code.unique()))
    comparison  =  import_file("data/300_AB.xlsx","xlsx")
    comparison = comparison.rename(columns = {"Varukod":"product_code"})
    print(comparison)

    comparison = comparison.drop_duplicates()
    print(len(comparison.product_code.unique()))

    ndf = df.merge(comparison,how = "left",on = ["product_code","product_code"])
    print(ndf.loc[ndf.tariffFormula.isna() == False,:])



if __name__ == "__main__":
    main()