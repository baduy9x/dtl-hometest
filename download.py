import sys, argparse, os
import zipfile
import requests
from datetime import datetime, timedelta
import logging
logging.basicConfig(level=logging.INFO)

def check_valid_date(date_str):
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    except:
        logging.error("The date input is not in corrected format, exiting...")
        sys.exit(0)
    if date_obj > datetime.now() - timedelta(days = 1):
        logging.warning("Data is not available for this date, exiting...")
        sys.exit(0)
    if date_obj.weekday() == 6 or date_obj.weekday() == 5:
        logging.warning("This is weekend, no data for this date, exiting...")
        sys.exit(0)

def check_valid_zip_file(file_path):
    zip_file = zipfile.ZipFile(file_path)
    zip_file_status = zip_file.testzip()
    if zip_file_status is None:
        logging.info("Zip file is OK")
        return True
    else:
        logging.error("File is not downloaded correctly")
        return False

def download(link, tmp_file_name, success_file_name, is_zip_file):
    response = requests.get(link)
    with open(tmp_file_name, "wb") as download_file:
        for data in response.iter_content():
            download_file.write(data)
    if is_zip_file:
        is_valid = check_valid_zip_file(tmp_file_name)
        if is_valid:
            os.rename(tmp_file_name, success_file_name)
            logging.info("File is successfully downloaded in {}".format(success_file_name))
        else:
            logging.error("The zip file downloaded is corrupted, download failed...")
            logging.error("Removing tmp file...")
            os.remove(tmp_file_name)
            logging.error("Exiting...")
            sys.exit(0)
    else:
        os.rename(tmp_file_name, success_file_name)
        logging.info("File is successfully downloaded in {}".format(success_file_name))

def cal_num_weekend_day_in_range(start_date, end_date):
    delta = (end_date - start_date).days
    result = 0
    for i in range(delta):
        curdate = start_date + timedelta(i)
        if curdate.weekday() == 5 or curdate.weekday() == 6:
            result += 1
    return result


def get_download_info(date, file_type):
    base_link = "https://links.sgx.com/1.0.0/derivatives-historical/"
    base_date = datetime(2021, 6, 16)
    base_number = 4921
    run_date = datetime.strptime(date, "%Y-%m-%d")

    if base_date >= run_date:
        num_weekend_day = cal_num_weekend_day_in_range(run_date, base_date)
        number = base_number - (base_date - run_date).days + num_weekend_day
    else:
        num_weekend_day = cal_num_weekend_day_in_range(base_date, run_date)
        number = base_number + (run_date - base_date).days - num_weekend_day

    if file_type == 'TICKDA':
        link = os.path.join(base_link, str(number), "WEBPXTICK_DT.zip")
        return (link, "WEBPXTICK_DT.tmp", "WEBPXTICK_DT.zip", True)
    elif file_type == 'TICKDS':
        link = os.path.join(base_link, str(number), "TickData_structure.dat")
        return (link, 'TickData_structure.tmp', 'TickData_structure.dat', False)
    elif file_type == 'TCDA':
        link = os.path.join(base_link, str(number), "TC.txt")
        return (link, "TC.tmp", "TC.txt", False)
    elif file_type == 'TCDS':
        link = os.path.join(base_link, str(number), "TC_structure.dat")
        return (link, "TC_structure.tmp", "TC_structure.dat", False)

    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(dest= "type", help = "File type to download", choices= ['TICKDA', 'TICKDS', 'TCDA', 'TCDS'])
    parser.add_argument(dest= "date", help = "The date of data to download, this must be in form yyyy-mm-dd, E.g '2021-06-23'")
    args = parser.parse_args()
    
    download_date = args.date
    file_type = args.type
    check_valid_date(download_date)

    if not os.path.isdir(download_date):
        os.mkdir(download_date)
    os.chdir(download_date)

    logging.info("Start to download file...")
    link, tmp_file_name, success_file_name, is_zip_file = get_download_info(download_date, file_type)

    download(link, tmp_file_name, success_file_name, is_zip_file)