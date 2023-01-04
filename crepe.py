import requests
import pandas as pd
import numpy as np
import sys
from tqdm import tqdm
import sqlite3
from time import sleep
from random import random
import pickle

class CountryData:
    """

    Class to access country information

    """

    def __init__(self,countries = "All",output = "verbose",output_type = "csv"):
        self.assert_output_type(output_type)
        self.countries = countries
        self.output = output
        self.output_type = output_type


    def assert_output_type(self,output_type):
        assert output_type in ["csv","sql"],"Ouput type must be csv or sql"


    def grab_country_info(self):
        country_url =  "https://trade.ec.europa.eu/access-to-markets/country/get/ALL?lang=en"
        result = requests.get(country_url).json()

        df = pd.DataFrame(result)
        self.country_data = df

        self.export_results(df)

    def export_results(self,df):
        if self.output_type == "csv":
            df.to_csv("country_data.csv")
            return 0

        if self.output_type == "sql":
            con = sqlite3.connect("CustomsDatabase")
            cur = con.cursor()
            df.to_sql("countries",con,if_exists = "replace",index = False)



        

class TariffData:
    """

    Class to get TariffData
    
    """

    def __init__(self,product_list = None,country_of_origin = None,country_of_destination = None,output_type = "sql"):
        self.product_list = [str(x)  for x in product_list]
        self.country_of_origin = country_of_origin
        self.country_of_destination = country_of_destination
        self.output_type = output_type

    

    def get_url(self,product_id,origin_country,destination_country):
        assert len(product_id)%2 == 0, "Seems like the product_id has the wrong parity"

        url = "https://trade.ec.europa.eu/access-to-markets/api/tariffs/get/{}/{}/{}?lang=EN".format(product_id,origin_country,destination_country)
        return url

    def get_json(self,url):
        headers = {"Connection":"keep-alive",
            "Host":"trade.ec.europa.eu",
            "Referer":"https://trade.ec.europa.eu/access-to-markets/en/results?product=100890&origin=NO&destination=SE",
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            "Sec-Fetch-Site":"same-origin"
                    }
        res = requests.get(url,headers = headers)
        return res.json()

    
    def get_response_df(self,json_obj):
        
        try:
            return pd.DataFrame(json_obj[0]["measures"])
        except Exception as e:
            pass

    def get_data(self,get_recursive = True):
        dfs = []
        exeptions = 0
        if self.product_list == None:
            print("You need to provide some products")
            return 0

        if self.country_of_origin == None:
            print("You need to provide some countires of origin")
            return 0

        if self.country_of_destination == None:
            print("You need to provide some destination country")
            return 0

        if get_recursive:
            errors = [0,0,0,0,0,0,0,0,0,0]
            errored_products = []

            for product in tqdm(self.product_list):
                
                for og_country in self.country_of_origin:
                    try:
                        url = self.get_url(product,og_country,self.country_of_destination)
                        
                        json_obj = self.get_json(url)
                    
                        df = self.get_response_df(json_obj)
                        df = df.loc[df.loc[:,"type"] == "Third country duty",:]
                        if len(df) == 0:
                            pass
                        else:
                            

                            df.loc[:,"product_id"] = product
                            df.loc[:,"country_of_origin"] = og_country
                            dfs.append(df)
                        
                        
                        

                    except Exception as e:
                        print(e)
                        exeptions += 1
                        errors.append(1)
                        errors = errors[1:]
                        errored_products.append(product)


                    if np.sum(errors) >= 9:
                        sleep(60*30)

                    else:
                        sleep(1 + random())

                    

        else:
            
            assert len(self.product_list) == len(self.country_of_origin)
            errors = [0,0,0,0,0,0,0,0,0,0]
            errored_products = []

            for i in tqdm(range(len(self.product_list))):
                og_country = self.country_of_origin[i]
                product = self.product_list[i]


                
                try:
                    url = self.get_url(product,og_country,self.country_of_destination)
                    json_obj = self.get_json(url)
                    df = self.get_response_df(json_obj)
                    df.loc[:,"product_id"] = product
                    df.loc[:,"country_of_origin"] = og_country
                    dfs.append(df)
                except Exception as e:
                        exeptions += 1
                        errors.append(1)
                        errors = errors[1:]
                        errored_products.append(product)

                if np.sum(errors) >= 9:
                    sleep(60*30)
                    errors = [0,0,0,0,0,0,0,0,0,0]


                else:
                    sleep(1 + random())

        print("Number of exceptions thrown = {}".format(exeptions))

        final_df = pd.concat(dfs)
        final_df = final_df.loc[:,["origin","type","startDate","endDate","exclusions","tariffFormula","product_id","country_of_origin"]]

        #self.export_results(final_df)

        return final_df,errored_products

    def export_results(self,df):
        """"
        
        To do: fix so that only alowed types are in df

        """
        if self.output_type == "csv":
            df.to_csv("tariff_data.csv")
            return 0

        if self.output_type == "sql":
            con = sqlite3.connect("CustomsDatabase")
            cur = con.cursor()
            df.to_sql("tariff_data",con,if_exists = "replace",index = False)




class ImportFile:
    def __init__(self,filename,header = 0):
        self.filename = filename
        self.filetype = None
        self.header = header
    
    def load_file(self):
        if self.filename[-4:] == "xlsx":
            try:
                self.input_file = pd.read_excel(self.filename,header = self.header)
                self.input_file.columns = self.input_file.iloc[6,:].values
                self.input_file = self.input_file.iloc[7:,:].reset_index(drop = True)
                self.filetype = "xlsx"
                return 0

            except Exception as e:
                print(e)
                

        if self.filename[-3:] == "csv":
            try:
                self.input_file = pd.read_csv(self.filename,dtype = str,heade  =self.header)
                self.filetype = "csv"
                return 0

            except Exception as e:
                print(e)


        print("No extension detected, please specify valid type (.xlsx,.csv)")
    
    def extract_values(self):
        if self.filetype == "csv":
            return self.input_file





    
class ProductData:
    """
    
    Class to get product data

    """

    def __init__(self,start_level = None):
        self.start_level = start_level
        self.product_ids = []

    def get_json(self,url):
        headers = {"Connection":"keep-alive",
            "Host":"trade.ec.europa.eu",
            "Referer":"https://trade.ec.europa.eu/access-to-markets/en/results?product=100890&origin=NO&destination=SE",
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            "Sec-Fetch-Site":"same-origin"
                    }
        res = requests.get(url,headers = headers)
        return res.json()


    def traverse(self,start_id = None):
        if start_id == None:
            start_id = self.start_level
            
        try:
            url = "https://trade.ec.europa.eu/access-to-markets/api/v2/nomenclature/products?country=SE&lang=EN&parent={}".format(start_id)
            result = self.get_json(url)
        
            for resp in result:
                if resp["hasChildren"] == False:
                    print(resp["code"])
                    self.product_ids.append(resp["code"])
                
                else:
                    self.traverse(start_id = resp["id"])

        except:
            pass
                
        #return self.product_ids



def get_tariffs(df1):
    
    df1.loc[:,"Varukod"] = [x.replace(" ","") for x in df1.Varukod]

    df1.loc[:,"merge_id"] = df1.Varukod + df1.Ursprungsland
    print(df1)

    df = df1.loc[:,["Varukod","Ursprungsland"]].drop_duplicates()
    products = [x.replace(" ","") for x in list(df.Varukod.values)]
    og_countries = list(df.Ursprungsland.values)


    td = TariffData(products,og_countries,"SE")
    result,errored_products = td.get_data(get_recursive = False)

    pickle.dump(errored_products,open("errors.p","wb"))

    result.to_csv("data/mid_result_2.csv")

    return result

    

    result.loc[:,"merge_id"] = result.product_id + result.country_of_origin
    result = result.loc[:,result.loc[:,"type"] == "Thrid country duty"]

    result.loc[:,"tariffFormula"] = [float(x.replace("%",""))/100 for x in result.tariffFormula]
    


    new_res = df1.loc[df1.Förmånskod == "300",:].merge(result, how = "left",on = ["merge_id","merge_id"])

    new_res.loc[:,"Statistiskt värde"] = pd.to_numeric(new_res.loc[:,"Statistiskt värde"])
    new_res.loc[:,"tariff_saving"] = new_res.loc[:,"Statistiskt värde"]*new_res.tariffFormula

    new_res.to_csv("data/test_result.csv")
    new_res.to_excel("data/test_result.xlsx")

    print(new_res)

def fix_values(x):
    if "EUR" in x:
        return "0"
    else:
        return x


def convert_result(result,df1,fta,eu_countries,filename = "2"):
    df1.loc[:,"Varukod"] = [x.replace(" ","") for x in df1.Varukod]

    df1.loc[:,"merge_id"] = df1.Varukod + df1.Ursprungsland

    result.loc[:,"merge_id"] = result.product_id.astype(str) + result.country_of_origin
    third_result = result.loc[result.loc[:,"type"] == "Third country duty",:]
    auto_result = result.loc[(result.loc[:,"type"] == "Autonomous tariff suspension"),:]

    third_result.loc[:,"tariffFormula"] = third_result.loc[:,"tariffFormula"].apply(lambda x : fix_values(x))

    third_result.loc[:,"tariffFormula"] = [float(x.replace("%",""))/100 for x in third_result.tariffFormula]
    auto_result.loc[:,"tariffFormula_auto"] = [float(x.replace("%",""))/100 for x in auto_result.tariffFormula]
    auto_result.loc[:,"tariffFormula_auto"].fillna(0)


    new_res = df1.loc[df1.Förmånskod == "300",:].merge(third_result, how = "left",on = ["merge_id","merge_id"])

    new_res.loc[:,"Statistiskt värde"] = pd.to_numeric(new_res.loc[:,"Statistiskt värde"])
    new_res.loc[:,"tariff_saving_300"] = new_res.loc[:,"Statistiskt värde"]*new_res.tariffFormula

    #new_res.to_csv("data/test_result.csv")
    new_res.to_excel("data/result_300_{}.xlsx".format(filename))

    df2 = df1.loc[(df1.loc[:,"Avgiftsslag"] == "Tull"),:]

    res_2 = df2.loc[df2.Förmånskod == "110"].merge(third_result,how = "left",on = ["merge_id","merge_id"])
    res_2 = res_2.merge(auto_result,how ="left",on = ["merge_id","merge_id"])
    res_2.loc[:,"tariff_saving_110"] = res_2.loc[:,"Statistiskt värde"]*(res_2.tariffFormula_x - res_2.tariffFormula_auto)
    print(res_2)
    res_2.to_excel("data/result_110_{}.xlsx".format(filename))


    df3 = df2.loc[(df2.loc[:,"Förmånskod"] != "300") & (df2.loc[:,"Avgift belopp"] > 5000) & (df2.Ursprungsland.isin(list(fta.country)) | df2.Ursprungsland.isin(list(eu_countries))),:]
    df3.loc[:,"possible_fta_savings"] = True

    df3.to_excel("data/possible_fta_savings_{}.xlsx".format(filename))
    

    print(df3)
    return new_res




def get_tarrifs_2(products,origin,destination,product_type):
    td = TariffData(products,origin,destination)
    result ,errored_products= td.get_data()

    pickle.dump(errored_products,open("errors.p","wb"))

    result.to_csv("data/testtest_{}.csv".format(product_type))

    return result

def import_file(name,type = "csv"):
    if type == "csv":
        df = pd.read_csv(name)

    else:

        df = pd.read_excel(name,converters = {"Goods code":str})
    return df

def fix_code(x):
    return int(x)
    c = str(x)

    if len(c) == 10:
        return int(c)
    else:
        return fix_code(c + "0")


def calc_forman_savings(row):
    third = row.Tredjelandstullsats
    pref = row.Preferenstullsats
    val = row.loc["Statistiskt värde"]

    if third == None:
        third = 0
    else:
        third = float(third.replace(" ","").replace("%",""))/100

    if pref == None:
        pref = 0

    else:
        pref = float(pref.replace(" ","").replace("%",""))/100

    if val == None:
        val = 0

    else:
        val = float(val)

    
    
    return val*(third - pref)

def calc_auto_savings(row):
    third = row.Tredjelandstullsats
    pref = row.loc["Autonom suspension tullsats"]
    val = row.loc["Statistiskt värde"]

    if third == None:
        third = 0
    else:
        third = float(third.replace(" ","").replace("%",""))/100

    if pref == None:
        pref = 0

    else:
        pref = float(pref.replace(" ","").replace("%",""))/100

    if val == None:
        val = 0

    else:
        val = float(val)

    
    
    return val*(third - pref)

def find_product(val,df,k = 1):
    result = df.loc[df.goodscode == val,:]
    result  = result.loc[(result.origin == "ERGA OMNES") & (result.measuretype == "Third country duty"),:]
    if len(result) > 0:
        return result,k
    else:
        new_val = int(str(val)[:-k] + k*"0")
        return find_product(new_val,df,k+1)


def find_product_for_pref(val,df,origin, k = 1):
    result = df.loc[df.goodscode == val,:]
    result  = result.loc[(result.origincode == origin) & (result.measuretype == "Tariff preference"),:]
    if k >= 6:
        return result,k

    if len(result) > 0:
        return result,k
    else:
        new_val = int(str(val)[:-k] + k*"0")
        return find_product_for_pref(new_val,df,origin,k+1)

def main_2():
    file_suffix = "Systems"
    df = import_file("data/duties2022.xlsx","xlxs")

    print(df.head(100))

    df.columns = [x.lower().replace(" ","") for x in df.columns]


    df.loc[:,"goodscode"] = [str(x) for x in df.goodscode]

    df.loc[:,"goodscode"] = df.goodscode.apply(lambda x : fix_code(x))

    print(df.loc[df.origin == "ERGA OMNES",:])



    
    filename = "data/statistik_import_2022-01-01_2022-12-31_AB.xlsx"
    imp = ImportFile(filename,header = 0)
    imp.load_file()
    test_file = imp.input_file
    fta = pd.read_csv("data/fta.txt")
    print(fta)

    print(test_file.columns)
    test_file.loc[:,"Avsändarland"] = None
    test_file.loc[:,"Importvärde"] = None
    test_file.loc[:,"Avgift tull"] = None

    test_file.loc[:,"Avgift Tilläggstull"] = None
    test_file.loc[:,"Avgift Mervärdeskatt"] = None
    test_file.loc[:,"Avgift Kemikalieskatt"] = None
    test_file.loc[:,"Avgift Mervärdeskatt"] = None
    test_file.loc[:,"Tredjelandstullsats"] = None
    test_file.loc[:,"Preferenstullsats"] = None
    test_file.loc[:,"Autonom suspension tullsats"] = None
    test_file.loc[:,"Sparande preferens"] = None
    test_file.loc[:,"Sparande autonom suspension"] = None

    test_file.loc[:,"Sparande IPR"] = None
    test_file.loc[:,"Potentiellt sparande"] = None
    test_file.loc[:,"Potentiellt fel"] = None
    test_file.loc[:,"check"] = None




    columns = ["Tull-id","Tx dag","Varupost antal","Deklarationssätt","Deklarationstyp","Transportsätt vid gräns",
    "Transportsätt inrikes","Avsändare","Avsändarland","Varupost nr","Varukod","Ursprungsland","Förfarandekod",
    "Förmånskod","Statistiskt värde","Nettovikt","Löpnr","Avgiftsslag","Importvärde","Avgift tull","Avgift Tilläggstull",
    "Avgift Mervärdeskatt","Avgift Kemikalieskatt","Tredjelandstullsats","Preferenstullsats",
    "Autonom suspension tullsats","Sparande preferens","Sparande autonom suspension","Sparande IPR","Potentiellt sparande","Potentiellt fel","check"]

    print(df.measuretype.unique())

    n = len(test_file)
    #n = 300
    for row in tqdm(range(n)):
        if test_file.iloc[row,:].loc["Avsändare"][-3:] == " AS":
            k = test_file.columns.get_loc("Avsändarland")
            test_file.iloc[row,k] = "Norge"

        if test_file.iloc[row,:].loc["Avgiftsslag"] == "Monetärt tullvärde":
            k = test_file.columns.get_loc("Importvärde")
            test_file.iloc[row,k] = test_file.iloc[row,:].loc["Statistiskt värde"]

        if test_file.iloc[row,:].loc["Avgiftsslag"] == "Tull":
            k = test_file.columns.get_loc("Avgift tull")
            test_file.iloc[row,k] = test_file.iloc[row,:].loc["Avgift belopp"]

        if test_file.iloc[row,:].loc["Avgiftsslag"] == "Tilläggstull":
            k = test_file.columns.get_loc("Avgift Tilläggstull")
            test_file.iloc[row,k] = test_file.iloc[row,:].loc["Avgift belopp"]

        if test_file.iloc[row,:].loc["Avgiftsslag"] == "Mervärdeskatt":
            k = test_file.columns.get_loc("Avgift Mervärdeskatt")
            test_file.iloc[row,k] = test_file.iloc[row,:].loc["Avgift belopp"]

        if test_file.iloc[row,:].loc["Avgiftsslag"] == "Kemikalieskatt":
            k = test_file.columns.get_loc("Avgift Kemikalieskatt")
            test_file.iloc[row,k] = test_file.iloc[row,:].loc["Avgift belopp"]

        
        k = test_file.columns.get_loc("Tredjelandstullsats")
        j = test_file.columns.get_loc("Varukod")
        origin_index = test_file.columns.get_loc("Ursprungsland")

        pref_index = test_file.columns.get_loc("Preferenstullsats")
        auto_index = test_file.columns.get_loc("Autonom suspension tullsats")
        forman_index = test_file.columns.get_loc("Förmånskod")
        sparande_index = test_file.columns.get_loc("Sparande preferens")
        auto_saving_index = test_file.columns.get_loc("Sparande autonom suspension")
        potential_index = test_file.columns.get_loc("Potentiellt sparande")
        check_index = test_file.columns.get_loc("check")


        val = int(test_file.iloc[row,j])

        sdf,iterations = find_product(val,df,k = 1)

        #print(sdf)

        #sdf = df.loc[df.goodscode == val,:]

        if iterations > 1:
            test_file.iloc[row,check_index] = "X"

        duty = sdf.loc[((sdf.addcode == "2500")  | (sdf.addcode.isna())),"duty"].values
        if len(duty) == 1:
            test_file.iloc[row,k] = duty[0]

        else:
            print(duty)
            print(sdf)
            print(iterations)
            print("Code {} not found in imported data".format(val))


        tp,iters_2 = find_product_for_pref(val,df,test_file.iloc[row,origin_index])  
        tp = tp.loc[:,"duty"].values

        if len(tp) == 1:
            test_file.iloc[row,pref_index] = tp[0]

        if iterations > 1:
            test_file.iloc[row,check_index] = "X"


        ats = sdf.loc[(sdf.origin == test_file.iloc[row,origin_index]) & sdf.measuretype == "Autonomous tariff suspension","duty"].values

        if len(ats) == 1:
            test_file.iloc[row,auto_index] = tp[0]


        if test_file.iloc[row,forman_index] == "300":
             test_file.iloc[row,sparande_index] = calc_forman_savings(test_file.iloc[row,:])

        if test_file.iloc[row,forman_index] == "110":
             test_file.iloc[row,auto_saving_index] = calc_auto_savings(test_file.iloc[row,:])


        if test_file.iloc[row,:].loc["Avgiftsslag"] == "Tull":
            if test_file.iloc[row,forman_index] != "300":
                if test_file.iloc[row,origin_index] in fta.country:
                    test_file.iloc[row,potential_index] = calc_forman_savings(test_file.iloc[row,:])


        


        

        

        

        
    

        

        


    

    test_file = test_file.loc[:,columns]

    test_file.to_excel("test_export.xlsx")
    


def main():

    file_suffix = "Systems"
    product_type = "3"
    get_products = False
    cd = CountryData(output_type = "sql")
    cd.grab_country_info()

    print(cd.country_data)

    eu_countries = cd.country_data.loc[cd.country_data.memberState == True,:].code.values

    print("Done")

    if get_products:

        pd = ProductData(start_level="-{}".format(product_type))
        pd.traverse()
        print(pd.product_ids)

        pickle.dump(pd.product_ids,open("products_{}.p".format(product_type),"wb"))


    




    #product_list = ['010121','01012910','01012990','010130']
    #country_of_origins = ["US","CA","NO","CN","CH"]
    product_list = pickle.load(open("products_{}.p".format(product_type),"rb"))
    country_of_origins = ["NO"]
    country_of_destination = "SE"
    result = get_tarrifs_2(product_list,country_of_origins,country_of_destination,product_type)
    print(result)
    

    #filename = "data/statistik_import_NV_" + file_suffix + ".xlsx"
    
    #imp = ImportFile(filename)
    #imp.load_file()
    #test_file = imp.input_file
    #df = get_tariffs(test_file)
    #fta = pd.read_csv("data/fta.txt")

    #df = pd.read_csv("data/mid_result_2.csv")

    #final_result = convert_result(df,test_file,fta,eu_countries,filename = file_suffix)
    #print(final_result)



if __name__ == "__main__":
    main_2()