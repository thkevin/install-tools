
import urllib.request
import re
import os
import errno
import sys
import tarfile
import shutil
from bs4 import BeautifulSoup
from datetime import datetime
from distutils.version import LooseVersion, StrictVersion

HOME = os.path.expanduser("~")

DOWNLOAD_DIR = HOME + '/Downloads/'
SHORTCUTS_DIR = HOME + '/.local/share/applications/'
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


# Untar build files
def extract_blender_archive(filename, dest_path):
    check_path(filename)
    if filename.split('.').pop() in ['xz', 'bz2']:
        extract_mode = "r:" + filename.split('.').pop()
    else:
        return

    with tarfile.open(filename, extract_mode) as tar:
        blender_folder = os.path.commonprefix(tar.getnames())
        if all(m_path.startswith('blender') for m_path in tar.getnames()):
            tar.extractall(path=dest_path)
        else:
            return

    blender_path = dest_path + '/blender'

    # Archive old blender version
    arch_path = dest_path + '/archives/'
    create_folder(arch_path)
    clean_files("arch_*", arch_path, 7 * 24)  # Remove archives older than 7d
    if os.path.exists(blender_path):
        shutil.move(blender_path, arch_path + '/arch_' + str(int(TS_NOW)))

    try:
        os.rename(dest_path + '/' + blender_folder, blender_path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def download_file(file_url, dest_path):
    try:
        # check if file exist and extract if so
        fh = open(dest_path, 'r')
        print('File already exists')
        return True, False, dest_path
    except FileNotFoundError:
        print("Downloading")
        # Downloading
        urllib.request.urlretrieve(file_url, dest_path)
        return True, True, dest_path

# Create app shortcut
def desktop_shortcut():
    return 0
