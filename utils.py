
import urllib.request
import re
import os
import errno
import sys
import tarfile
import shutil
from bs4 import BeautifulSoup
from datetime import datetime

HOME = os.path.expanduser("~")

BUILDER_PAGE = 'https://builder.blender.org/'
BUILD_DIR = HOME + '/blender_builder/'
DOWNLOAD_DIR = HOME + '/Downloads/blender_builds/'
TS_NOW = datetime.now().timestamp()


# Found in stackoverflow, human readable size
def humanbytes(B):
    'Return the given bytes as a human friendly KB, MB, GB, or TB string'
    B = float(B)
    KB = float(1024)
    MB = float(KB ** 2)
    GB = float(KB ** 3)
    TB = float(KB ** 4)

    if B < KB:
        return '{0} {1}'.format(B, 'Bytes' if 0 == B > 1 else 'Byte')
    elif KB <= B < MB:
        return '{0:.2f}KB'.format(B/KB)
    elif MB <= B < GB:
        return '{0:.2f}MB'.format(B/MB)
    elif GB <= B < TB:
        return '{0:.2f}GB'.format(B/GB)
    elif TB <= B:
        return '{0:.2f}TB'.format(B/TB)


# Compare file sizes regardless to the unit(default bytes)
def greater_size(f_size1, f_size2):
    f1 = float(re.sub(r"[a-zA-z]+", '', f_size1))
    f2 = float(re.sub(r"[a-zA-z]+", '', f_size2))

    if f1 < f2:
        return False
    else:
        return True


# Check if path exist
def check_path(to_check):
    path_to_check = str(to_check)
    assert_msg = """The path: \'" + path_to_check + "\' does not exist.
    Task aborted"""
    assert os.path.exists(path_to_check), assert_msg


# Creates a folder if it doesn't already exist
def create_folder(folder_path):
    if not os.path.exists(folder_path):
        try:
            os.makedirs(folder_path)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise


# Delete files or folder macthing a regex.
# If creation_hrs defined, remove only thoses older than creation_hrs hours
def clean_files(match_regex, f_path, creation_hrs=None):
    check_path(f_path)
    rg = re.compile(match_regex)

    try:
        ls_dir = os.listdir(f_path)
        to_rm = [os.path.join(f_path, f) for f in ls_dir if rg.match(f)]

        if creation_hrs:
            limit_ts = TS_NOW - (creation_hrs * 60 * 60)  # hours to sec
            to_rm = [f for f in to_rm if os.stat(f).st_mtime < limit_ts]

        for m in to_rm:
            if os.path.isdir(m):
                shutil.rmtree(m, ignore_errors=True)
            else:
                os.remove(m)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
