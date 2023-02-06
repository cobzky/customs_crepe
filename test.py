import pandas as pd
import sys
import os
path = os.getcwd()
files = os.listdir(path + "\data\Jan_23")

def find_file_path(file_type,entity,files):
    assert file_type in ["emma","tull"],"No"

    if file_type == "emma":
        for f in files:
            if "Detaljer" in f.split(" "):
                print(f.split(" "))
                if entity.lower() in f.split(" ")[4].lower():   
                    return f

    if file_type == "tull":
        for f in files:
            if "statistik" in f.split("_"):

                if entity.lower() in f.split("_")[-1].lower():
                    return f
            

files_subs = ["AB",
    "ETT",
    "LABS",
    "Battery",
    "Revolt"]

for name in files_subs:
    print(find_file_path("tull",name,files))

    
