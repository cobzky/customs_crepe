import requests
import pandas as pd
import sys
from tqdm import tqdm
import sqlite3

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

    def get_data(self):
        dfs = []
        if self.product_list == None:
            print("You need to provide some products")
            return 0

        if self.country_of_origin == None:
            print("You need to provide some countires of origin")
            return 0

        if self.country_of_destination == None:
            print("You need to provide some destination country")
            return 0

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

        final_df = pd.concat(dfs)

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




    

def main():
    cd = CountryData(output_type = "sql")
    cd.grab_country_info()
    print("Done")




    product_list = ['010121','01012910','01012990','010130']
    country_of_origins = ["US","CA","NO","CN","CH"]
    country_of_destination = "SE"
    
    td = TariffData(product_list,country_of_origins,country_of_destination)

    result = td.get_data()
    print(result)

if __name__ == "__main__":
    main()