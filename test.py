import pandas as pd
import sys
import os
path = os.getcwd()
files = os.listdir(path + "\data\Jan_23")

def fix_po_number(x,entity):
    po_numbers = ""
    if x == None:
        return None
    else:
        if ((" " in x) or ("/" in x)) == False:
            val = x
            if entity == "AB":
                if (val[:3] == "100") or (val[:2] == "PO"):
                    po_numbers += val + " "
            if entity == "Ett":
                if (val[:3] == "300") or (val[:2] == "PO"):
                    po_numbers += val + " "

            if entity == "Labs":
                if (val[:3] == "200") or (val[:2] == "PO"):
                    po_numbers += val + " "

            if entity == "Revolt":
                if (val[:3] == "700") or (val[:2] == "PO"):
                    po_numbers += val + " "

            if entity == "Systems":
                if (val[:3] == "700") or (val[:2] == "PO"):
                    po_numbers += val + " "


        vals = x.split(" ")

        for val in vals:
            if entity == "Northvolt AB":
                if (val[:3] == "100") or (val[:2] == "PO"):
                    po_numbers += val + " "
            if entity == "Northvolt ETT":
                if (val[:3] == "300") or (val[:2] == "PO"):
                    po_numbers += val + " "

            if entity == "Northvolt LABS":
                if (val[:3] == "200") or (val[:2] == "PO"):
                    po_numbers += val + " "

            if entity == "Northvol Revolt":
                if (val[:3] == "700") or (val[:2] == "PO"):
                    po_numbers += val + " "

            if entity == "Northvolt Systems":
                if (val[:3] == "700") or (val[:2] == "PO"):
                    po_numbers += val + " "
        
        vals = x.split("/")
        for val in vals:
            if entity == "Northvolt AB":
                if (val[:3] == "100") or (val[:2] == "PO"):
                    po_numbers += val + " "
            if entity == "Northvolt ETT":
                if (val[:3] == "300") or (val[:2] == "PO"):
                    po_numbers += val + " "

            if entity == "Northvolt LABS":
                if (val[:3] == "200") or (val[:2] == "PO"):
                    po_numbers += val + " "

            if entity == "Northvol Revolt":
                if (val[:3] == "700") or (val[:2] == "PO"):
                    po_numbers += val + " "

            if entity == "Northvolt Systems":
                if (val[:3] == "700") or (val[:2] == "PO"):
                    po_numbers += val + " "

    return po_numbers

final_result = pd.read_excel("data/Results/test_export_final_Jan_23.xlsx")
    
po = []
for i in range(len(final_result)):
        x = str(final_result.iloc[i,:]["Reference"])
        entity = final_result.iloc[i,:]["Entity"]
        po.append(fix_po_number(x,entity))


res = pd.DataFrame({"reference":final_result.Reference,"Po":po})
print(res)
res.to_excel("po_test.xlsx")