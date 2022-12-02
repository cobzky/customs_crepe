import requests
import pandas as pd
import sys
from tqdm import tqdm
import sqlite3
from time import sleep

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
        res = requests.get(url)
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

            for product in tqdm(self.product_list):
                for og_country in self.country_of_origin:
                    url = self.get_url(product,og_country,self.country_of_destination)
                    json_obj = self.get_json(url)
                    try:
                        df = self.get_response_df(json_obj)
                        df.loc[:,"product_id"] = product
                        df.loc[:,"country_of_origin"] = og_country

                    except Exception as e:
                        pass

                    dfs.append(df)

        else:
            
            assert len(self.product_list) == len(self.country_of_origin)
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

                
                sleep(2)

        print("Number of exceptions thrown = {}".format(exeptions))

        final_df = pd.concat(dfs)
        final_df = final_df.loc[:,["origin","type","startDate","endDate","exclusions","tariffFormula","product_id","country_of_origin"]]

        #self.export_results(final_df)

        return final_df

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
    def __init__(self,filename):
        self.filename = filename
        self.filetype = None
    
    def load_file(self):
        if self.filename[-4:] == "xlsx":
            try:
                self.input_file = pd.read_excel(self.filename)
                self.input_file.columns = self.input_file.iloc[6,:].values
                self.input_file = self.input_file.iloc[7:,:].reset_index(drop = True)
                self.filetype = "xlsx"
                return 0

            except Exception as e:
                print(e)
                

        if self.filename[-3:] == "csv":
            try:
                self.input_file = pd.read_csv(self.filename,dtype = str)
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


    def traverse(self,start_id = None):
        if start_id == None:
            start_id = self.start_id
            
        url = "https://trade.ec.europa.eu/access-to-markets/api/v2/nomenclature/products?country=SE&lang=EN&parent={}".format(start_id)
        result = requests.get(url).json()
        
        for resp in result:
            if resp["hasChildren"] == False:
                self.product_codes.append(resp["code"])
                
            else:
                self.traverse(start_id = resp["id"])
                
        return self.product_codes



def get_tariffs(df1):
    
    df1.loc[:,"Varukod"] = [x.replace(" ","") for x in df1.Varukod]

    df1.loc[:,"merge_id"] = df1.Varukod + df1.Ursprungsland
    print(df1)

    df = df1.loc[:,["Varukod","Ursprungsland"]].drop_duplicates()
    products = [x.replace(" ","") for x in list(df.Varukod.values)]
    og_countries = list(df.Ursprungsland.values)

    print(products)
    print(og_countries)

    td = TariffData(products,og_countries,"SE")
    result = td.get_data(get_recursive = False)

    result.to_csv("data/mid_result.csv")

    

    result.loc[:,"merge_id"] = result.product_id + result.country_of_origin
    result = result.loc[:,result.loc[:,"type"] == "Thrid country duty"]

    result.loc[:,"tariffFormula"] = [float(x.replace("%",""))/100 for x in result.tariffFormula]
    


    new_res = df1.loc[df1.Förmånskod == "300",:].merge(result, how = "left",on = ["merge_id","merge_id"])

    new_res.loc[:,"Statistiskt värde"] = pd.to_numeric(new_res.loc[:,"Statistiskt värde"])
    new_res.loc[:,"tariff_saving"] = new_res.loc[:,"Statistiskt värde"]*new_res.tariffFormula

    new_res.to_csv("data/test_result.csv")
    new_res.to_excel("data/test_result.xlsx")

    print(new_res)


def convert_result(result,df1,fta,eu_countries):
    df1.loc[:,"Varukod"] = [x.replace(" ","") for x in df1.Varukod]

    df1.loc[:,"merge_id"] = df1.Varukod + df1.Ursprungsland

    result.loc[:,"merge_id"] = result.product_id.astype(str) + result.country_of_origin
    third_result = result.loc[result.loc[:,"type"] == "Third country duty",:]
    auto_result = result.loc[(result.loc[:,"type"] == "Autonomous tariff suspension"),:]

    third_result.loc[:,"tariffFormula"] = [float(x.replace("%",""))/100 for x in third_result.tariffFormula]
    auto_result.loc[:,"tariffFormula_auto"] = [float(x.replace("%",""))/100 for x in auto_result.tariffFormula]
    auto_result.loc[:,"tariffFormula_auto"].fillna(0)


    new_res = df1.loc[df1.Förmånskod == "300",:].merge(third_result, how = "left",on = ["merge_id","merge_id"])

    new_res.loc[:,"Statistiskt värde"] = pd.to_numeric(new_res.loc[:,"Statistiskt värde"])
    new_res.loc[:,"tariff_saving_300"] = new_res.loc[:,"Statistiskt värde"]*new_res.tariffFormula

    #new_res.to_csv("data/test_result.csv")
    #new_res.to_excel("data/test_result.xlsx")

    df2 = df1.loc[(df1.loc[:,"Avgiftsslag"] == "Tull"),:]

    res_2 = df2.loc[df2.Förmånskod == "110"].merge(third_result,how = "left",on = ["merge_id","merge_id"])
    res_2 = res_2.merge(auto_result,how ="left",on = ["merge_id","merge_id"])
    res_2.loc[:,"tariff_saving_110"] = res_2.loc[:,"Statistiskt värde"]*(res_2.tariffFormula_x - res_2.tariffFormula_auto)
    print(res_2)
    res_2.to_excel("data/test_result_110.xlsx")


    df3 = df2.loc[(df2.loc[:,"Förmånskod"] != "300") & (df2.loc[:,"Avgift belopp"] > 5000) & (df2.Ursprungsland.isin(list(fta.country)) | df2.Ursprungsland.isin(list(eu_countries))),:]
    df3.loc[:,"possible_fta_savings"] = True

    df3.to_excel("data/possible_fta_savings.xlsx")
    

    print(df3)
    return new_res







def main():
    cd = CountryData(output_type = "sql")
    cd.grab_country_info()

    print(cd.country_data)

    eu_countries = cd.country_data.loc[cd.country_data.memberState == True,:].code.values

    #print("Done")




    product_list = ['010121','01012910','01012990','010130']
    country_of_origins = ["US","CA","NO","CN","CH"]
    country_of_destination = "SE"
    
    #td = TariffData(product_list,country_of_origins,country_of_destination)

    #result = td.get_data()
    #print(result.columns)
    #print(result)
    
    imp = ImportFile("data/statistik_import.xlsx")
    imp.load_file()
    test_file = imp.input_file
    #get_tariffs(test_file)
    fta = pd.read_csv("data/fta.txt")
    print(fta)

    df = pd.read_csv("data/mid_result.csv")

    final_result = convert_result(df,test_file,fta,eu_countries)
    print(final_result)



if __name__ == "__main__":
    main()