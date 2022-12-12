import pandas as pd
from xml.dom import minidom
from ftplib import FTP
import os


def main():

    filename = "MeasureType_34e45886-3fdd-41ed-bf30-0382476cd5a9_221201.xml.gz.pgp"
    ftp = FTP('distr.tullverket.se')
    ftp.login(user = "M10746-1",passwd = "kehts3qW")
    ftp.cwd("/tulltaxan/xml/tot")
    ftp.retrlines('LIST')

    download_name = 'test_measure_file.gz.pgp'

    with open(download_name, 'wb') as fp:

        ftp.retrbinary('RETR ' + filename, fp.write)


    ftp.close()

    output_name = "decrypted_measure_test"

    os.system("gpg --output {}.gz --decrypt {}".format(output_name,download_name))
    os.system("gzip -d {}.gz".format(output_name))
    os.system("ls")

    #test = minidom.parse("test.xml")
    #print(test)

def test():
    os.system("ls")
    
if __name__ == "__main__":
    main()