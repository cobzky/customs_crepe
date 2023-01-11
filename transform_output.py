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

def compress_product(df):
    ndf = df.loc[:,['Tull-id', 'Tx dag', 'Varupost antal', 'Deklarationssätt',
       'Deklarationstyp', 'Transportsätt vid gräns', 'Transportsätt inrikes',
       'Avsändare', 'Avsändarland', 'Varupost nr', 'Varukod', 'Ursprungsland',
       'Förfarandekod', 'Förmånskod', 'Statistiskt värde', 'Nettovikt','Tredjelandstullsats', 'Preferenstullsats',
       'Autonom suspension tullsats',"entity"]].drop_duplicates()

    assert len(ndf) == 1,print(ndf)



def compress(df):
    unique_ids = df.loc[:,"Tull-id"].unique()
    dfs = []
    for uid in tqdm(unique_ids):
        sdf = df.loc[df.loc[:,"Tull-id"] == uid,:]
        unique_numbers = sdf.loc[:,"Varupost nr"].unique()
        for un in unique_numbers:
            ssdf = sdf.loc[df.loc[:,"Varupost nr"] == un,:]
            compress_product(ssdf)


def main():

    df = pd.read_excel("data/test_export_final.xlsx")
    print(df)

    print(df.columns)

    compress(df)

    



if __name__ == "__main__":
    main()