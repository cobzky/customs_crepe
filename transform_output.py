import pandas as pd
from tqdm import tqdm

['Tull-id', 'Tx dag', 'Varupost antal', 'Deklarationssätt',
       'Deklarationstyp', 'Transportsätt vid gräns', 'Transportsätt inrikes',
       'Avsändare', 'Avsändarland', 'Varupost nr', 'Varukod', 'Ursprungsland',
       'Förfarandekod', 'Förmånskod', 'Statistiskt värde', 'Nettovikt',
       'Löpnr', 'Avgiftsslag', 'Importvärde', 'Avgift tull',
       'Avgift Tilläggstull', 'Avgift Mervärdeskatt', 'Avgift Kemikalieskatt',
       'Tredjelandstullsats', 'Preferenstullsats',
       'Autonom suspension tullsats', 'Sparande preferens',
       'Sparande autonom suspension', 'Sparande IPR', 'Potentiellt sparande',
       'Potentiellt fel', 'check', 'entity']

def grab_valid_value(df,column):
    value = None
    for val in df.loc[:,column].values:
        if val == value:
            pass
        elif val == "Null":
            pass
        elif val == None:
            pass

        else:
            value = val

    return val

        



def compress_product(df):
    ndf = df.loc[:,['Tull-id', 'Tx dag', 'Varupost antal', 'Deklarationssätt',
       'Deklarationstyp', 'Transportsätt vid gräns', 'Transportsätt inrikes',
       'Avsändare', 'Avsändarland', 'Varupost nr', 'Varukod', 'Ursprungsland',
       'Förfarandekod', 'Förmånskod', 'Statistiskt värde', 'Nettovikt','Tredjelandstullsats', 'Preferenstullsats',
       'Autonom suspension tullsats',"entity"]].drop_duplicates()

    assert len(ndf) == 1,print(ndf)

    ndf.loc[:,'Importvärde'] = grab_valid_value(df,'Importvärde')  
    ndf.loc[:,"Avgift tull"] = grab_valid_value(df,'Avgift tull')
    ndf.loc[:,'Avgift Tilläggstull'] = grab_valid_value(df,'Avgift Tilläggstull')
    ndf.loc[:,'Avgift Mervärdeskatt'] = grab_valid_value(df,'Avgift Mervärdeskatt')
    ndf.loc[:,'Avgift Kemikalieskatt'] = grab_valid_value(df,'Avgift Kemikalieskatt')
    ndf.loc[:,'Sparande preferens'] = grab_valid_value(df,'Sparande preferens')
    ndf.loc[:,'Sparande autonom suspension'] = grab_valid_value(df,'Sparande autonom suspension')
    ndf.loc[:,'Sparande IPR'] = grab_valid_value(df,'Sparande IPR')
    ndf.loc[:,'Potentiellt sparande'] = grab_valid_value(df,'Potentiellt sparande')
    ndf.loc[:,'Potentiellt fel'] = grab_valid_value(df,'Potentiellt fel')
    ndf.loc[:,'check'] = grab_valid_value(df,'check')

    return ndf.loc[:,['Tull-id', 'Tx dag', 'Varupost antal', 'Deklarationssätt',
       'Deklarationstyp', 'Transportsätt vid gräns', 'Transportsätt inrikes',
       'Avsändare', 'Avsändarland', 'Varupost nr', 'Varukod', 'Ursprungsland',
       'Förfarandekod', 'Förmånskod', 'Statistiskt värde', 'Nettovikt', 'Importvärde', 'Avgift tull',
       'Avgift Tilläggstull', 'Avgift Mervärdeskatt', 'Avgift Kemikalieskatt',
       'Tredjelandstullsats', 'Preferenstullsats',
       'Autonom suspension tullsats', 'Sparande preferens',
       'Sparande autonom suspension', 'Sparande IPR', 'Potentiellt sparande',
       'Potentiellt fel', 'check', 'entity']]

    



def compress(df):
    unique_ids = df.loc[:,"Tull-id"].unique()
    dfs = []
    for uid in tqdm(unique_ids):
        sdf = df.loc[df.loc[:,"Tull-id"] == uid,:]
        unique_numbers = sdf.loc[:,"Varupost nr"].unique()
        for un in unique_numbers:
            ssdf = sdf.loc[sdf.loc[:,"Varupost nr"] == un,:]
            val = compress_product(ssdf)
            dfs.append(val)

    df = pd.concat(dfs)
    return df


def main():

    df = pd.read_excel("data/test_export_final_2.xlsx")
    print(df)
    print(df.loc[:,"Avgift tull"])

    print(df.columns)

    #compress(df)
    print(df.loc[df.loc[:,"Förfarandekod"] == 5100,:])
    


if __name__ == "__main__":
    main()