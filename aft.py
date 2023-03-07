import ftplib
import os
import shutil
import time


# **********************************************************************************
# Function log_write()
# Log file to keep track of transferred files and errors
# **********************************************************************************
def log_write(log):
    LOG_FILE = 'transfer.log'
    try:
        # Write log entry for transferred files
        with open(LOG_FILE, 'a') as log_file:
            log_file.write(f'{time.strftime("%Y-%m-%d %H:%M:%S")} - {log} \n')
            # Comment next line to suppress console output
            print(log.strip('\n'))
    except Exception:
        with open(LOG_FILE, "w+") as log_file:
            log_file.write(f" ******* Log ******\n\n")
            # Comment next line to suppress console output
            print(log.strip('\n'))


# **********************************************************************************
# Function move_files()
# **********************************************************************************
def move_files():
    # Move files to internal network directory
    if not os.path.exists(internal_dir):
        os.makedirs(internal_dir)
    for filename in os.listdir(local_dir):
        source_path = os.path.join(local_dir, filename)
        dest_path = os.path.join(internal_dir, filename)
        shutil.move(source_path, dest_path)
    log_write(f'All files from {os.path.abspath(local_dir)} folder  moved to {os.path.abspath(internal_dir)}')


# **********************************************************************************
# Function download_files()
# ***********************************************************************************
def ftp_connect(ftp_host, ftp_user, ftp_pass):
    ftp = ftplib.FTP(ftp_host)
    ftp.login(user=ftp_user, passwd=ftp_pass)
    return ftp


# **********************************************************************************
# Function download_files()
# ***********************************************************************************
def download_files(ftp_host, ftp_user, ftp_pass):
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)
    # Connect to FTP server and read the file list
    ftp = ftplib.FTP(ftp_host)
    ftp.login(user=ftp_user, passwd=ftp_pass)
    files = ftp.nlst()
    for filename in files:
        local_path = os.path.join(local_dir, filename)
        if not filename.startswith('.'):
            with open(local_path, 'wb') as file:
                ftp.retrbinary('RETR ' + filename, file.write)
                log_write(f'{filename}  -  downloaded  to local folder')
    ftp.quit()


# **********************************************************************************
# Function schedule
# download interval and add a copy delay
# **********************************************************************************
def schedule(aruments):
    while True:
        ftp_host, ftp_user, ftp_pass, sch_interval1, sch_interval2 = aruments[0], aruments[1], aruments[2], aruments[3], \
        aruments[4]

        try:
            download_files(ftp_host, ftp_user, ftp_pass)
        except Exception as e:
            log_write(f"Download files, FTP error")
        print(f'Next files transfer in {sch_interval2} seconds')
        time.sleep(sch_interval2)

        try:
            move_files()
        except Exception as e:
            log_write(f"Move files error")
        print(f'Next download in {sch_interval1} seconds')
        time.sleep(sch_interval1)


# **********************************************************************************
# function make_interval:
# **********************************************************************************
def make_interval(my_int, default_int):
    # print(my_int,' - int-',default_int)
    try:
        my_int = my_int.strip().lower().split(":")
        hh, mm, ss = my_int[0], my_int[1], my_int[2]
        if hh == '':
            hh = 0
        else:
            hh = int(hh)
        if mm == '':
            mm = 0
        else:
            mm = int(mm)
        if ss == '':
            ss = 0
        else:
            ss = int(ss)
        my_int = hh * 3600 + mm * 60 + ss
        if my_int == 0:
            my_int = default_int
            log_write(f"Default interval value set to : {my_int} seconds")
    except Exception as e:
        my_int = default_int
        log_write(f"Default interval value set to : {my_int} seconds")
    finally:
        return my_int


lines = ''
if os.path.exists('config.txt'):
    try:
        with open('config.txt', 'r') as c:
            lines = c.read().splitlines()
            my_consts_list = []
            for i in range(7):
                my_const = lines[i].split('=')[1].replace('\'', '').replace('"', '').strip()
                my_consts_list.append(my_const)
    except Exception as f:
        # print(f)
        my_consts_list = ['', '', '', '', '', '', '']
        log_write(' Can not read config.txt set defaults values')

try:
    ftp_host = my_consts_list[0]
    ftp_user = my_consts_list[1]
    ftp_pass = my_consts_list[2]
    ftp_connect(ftp_host, ftp_user, ftp_pass)

except Exception as e:
    log_write(str(e))
    # Demo FTP server credentials
    log_write('FTP demo values loaded')
    ftp_host = 'files.000webhost.com'
    ftp_user = 'ftpdemo333'
    ftp_pass = 'XP%MQ(*qwgD#8QxoP@kh'

# Schedule intervals
download_interval = make_interval(my_consts_list[3], 7)
move_interval = make_interval(my_consts_list[4], 5)

# Local and internal folders
local_dir = my_consts_list[5]
internal_dir = my_consts_list[6]
if local_dir == '':
    local_dir = 'local_default'
if internal_dir == '':
    internal_dir = 'internal_default'

while True:
    try:
        arguments = [ftp_host, ftp_user, ftp_pass, download_interval, move_interval]
        schedule(arguments)
    except KeyboardInterrupt:
        print("Goodbye")
        exit(0)

# Usage:  python3 aft.py
# Ctrl c to stop execution
# Make sure you have config.txt in the same folder with the first 7 lines  as in my model
