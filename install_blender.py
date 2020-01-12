# Debian Linux blender download and install from blender builder

# pip install beautifulsoup
# sudo apt-get install python3-bs4

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


# Parse dedicated html tag for infos
def extract_infos(a_tag):
    download_extension = a_tag['href']
    name = a_tag.find('span', class_='name').contents[0]
    date = a_tag.find('span', class_='name').select('small')[0].get_text()
    build_type = a_tag.find('span', class_='build').get_text()
    build_size = a_tag.find('span', class_='size').get_text()
    infos = {
        'build_name': name,
        'build_date': date,
        'build_type': build_type,
        'build_size': build_size,
        'download_extension': download_extension
    }
    return infos


# Download linux zip file
# Return a tuple (Exist, Downloaded, Path)
def download_build(selected_build, download_path=DOWNLOAD_DIR):
    name = selected_build['build_name']
    date = selected_build['build_date']
    size = selected_build['build_size']
    extension = selected_build['download_extension']

    download_url = BUILDER_PAGE + extension
    filename = extension.split('/').pop()
    file_path = download_path + filename

    create_folder(download_path)

    try:
        # check if file exist and extract if so
        fh = open(file_path, 'r')
        print('Build from ' + date + ' already downloaded')
        return True, False, file_path
    except FileNotFoundError:
        print("Downloading")
        clean_files("blender.*tar.*", download_path, 7 * 24)
        # Downloading
        urllib.request.urlretrieve(download_url, file_path)

        # check downloaded file size
        file_infos = os.stat(file_path)
        if greater_size(str(size), str(humanbytes(file_infos.st_size))):
            print("Expected size downloaded")
            print(name + ' downloaded in ' + file_path)
            return True, True, file_path
        else:
            print("Expected size not reached")
            # Removing corrupted file
            os.remove(file_path)
            print("Corrupted file removed")
            return False, False, None


# Untar build files
def extract_build(filename, dest_path=BUILD_DIR):
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
    # clean_files("arch_*", arch_path, 7 * 24)  # Remove archives older than 7d
    if os.path.exists(blender_path):
        shutil.move(blender_path, arch_path + '/arch_' + str(int(TS_NOW)))

    try:
        os.rename(dest_path + '/' + blender_folder, blender_path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


# Reading blender builder web page
with urllib.request.urlopen(BUILDER_PAGE + 'download') as response:
    html = response.read()
soup = BeautifulSoup(html, 'html.parser')

# Retrieving linux builds infos
download_blocks = soup.find_all('section', class_="builds-list platform-linux")

selected = []
for section in download_blocks:
    selected.extend(section.select('li a'))

result_download = download_build(extract_infos(selected[0]))

if result_download[1]:  # Extract file only when it is downloaded
    print("Extracting")
    extract_build(result_download[2])
