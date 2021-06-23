import sys, argparse, os
import zipfile
import requests
import logging
logging.basicConfig(level=logging.DEBUG)

# download_date = sys.argv[1]
download_link = "https://links.sgx.com/1.0.0/derivatives-historical/4923/WEBPXTICK_DT.zip"
    
response = requests.get(download_link)

with open("download_file.zip.tmp", "wb") as download_file:
    for data in response.iter_content():
        download_file.write(data)

# Test is zip file is corrupted
zip_file = zipfile.ZipFile("download_file.zip.tmp")
zip_file_status = zip_file.testzip()
if zip_file_status is None:
    logging.info("Zip file is OK, Renaming the file...")
    os.rename("download_file.zip.tmp", "download_file.zip")

logging.info("Done")