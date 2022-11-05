import pandas as pd
import argparse
import crepe


def main():
    parser = argparse.ArgumentParser(prog = "crepe_cli",
    description = "This is a command line client to user the crepe program and configure shit",
    epilog = "For help call someone")

    parser.add_argument("-f","--file")
    parser.add_argument("-o","--output")
    parser.add_argument("-i","--interactive")

    args = parser.parse_args()
    
    file_name = args.file

    output_filename = args.output

    if file_name != None:
        f = crepe.ImportFile(file_name)
        f.load_file()
        value_df = f.extract_values()

        
        ids = list(value_df.codes.values)
        ogs = list(value_df.origin.unique())
        country_of_destination = "SE"

        td = crepe.TariffData(ids,ogs,country_of_destination)
        result = td.get_data()
        print(result)

        if output_filename == None:
            print("No output name specified. See -h for help")

        else:
            result.to_csv(output_filename)

        




if __name__ == "__main__":
    main()