import requests
import pandas as pd
import sys

class CountryData:
    """

    Class to access country information

    """

    def __init__(self,countries = "All",output = "verbose",output_type = "csv"):
        self.countries = countries
        self.output = output
        self.output_type = output_type

    def grab_country_info(self):
        country_url =  "https://trade.ec.europa.eu/access-to-markets/country/get/ALL?lang=en"
        result = requests.get(country_url).json()

        df = pd.DataFrame(result)

        return df
        

class TariffData:
    """

    Class to get TariffData
    
    """

    def __init__(self,product_list = None,country_of_origin = None,country_of_destination = None):
        self.product_list = product_list
        self.country_of_origin = country_of_origin
        self.country_of_destination = country_of_destination

    

    def get_url(self,product_id,origin_country,destination_country):
        assert len(product_id)%2 == 0, "Seems like the product_id has the wrong parity"

        url = "https://trade.ec.europa.eu/access-to-markets/api/tariffs/get/{}/{}/{}?lang=EN".format(product_id,origin_country,destination_country)
        return url

    def get_json(self,url):
        return requests.get(url).json()

    
    def get_response_df(self,json_obj):
        return pd.DataFrame(json_obj[0]["measures"])

    
class ProductData:
    """
    
    Class to get product data

    """

    def __init__(self,start_level = None):
        self.start_level = start_level
        self.product_ids = []


    

    

def main():
    #cd = CountryData()
    #country_df = cd.grab_country_info()
    #print(country_df)
    pass

if __name__ == "__main__":
    main()