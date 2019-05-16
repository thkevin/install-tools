# Debian Linux blender download and install from blender builder

# pip install beautifulsoup

import urllib.request
import re
import os
from bs4 import BeautifulSoup

builder_url = 'https://builder.blender.org/'
download_folder = './downloads/'


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
def download_build(selected_build):
    name = selected_build['build_name']
    date = selected_build['build_date']
    size = selected_build['build_size']
    extension = selected_build['download_extension']

    download_url = builder_url + extension
    filename = extension.split('/').pop()
    file_path = download_folder + filename

    try:
        # check if file exist
        fh = open(file_path, 'r')
        print('Build from ' + date + ' already downloaded')
    except FileNotFoundError:
        # Downloading
        urllib.request.urlretrieve(download_url, file_path)

        # check downloaded file size
        file_infos = os.stat(file_path)
        if greater_size(str(size), str(humanbytes(file_infos.st_size))):
            print("Expected size downloaded")
            print(name + ' downloaded in ' + file_path)
        else:
            print("Expected size not reached")
            # Removing corrupted file
            os.remove(file_path)
            print("Corrupted file removed")


# Found in stackoverflow, human readable size
def humanbytes(B):
    'Return the given bytes as a human friendly KB, MB, GB, or TB string'
    B = float(B)
    KB = float(1024)
    MB = float(KB ** 2)  # 1,048,576
    GB = float(KB ** 3)  # 1,073,741,824
    TB = float(KB ** 4)  # 1,099,511,627,776

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


# Reading blender builder download web page
with urllib.request.urlopen(builder_url + 'download') as response:
    html = response.read()
soup = BeautifulSoup(html, 'html.parser')

# Retrieving only linux tags
download_blocks = soup.find_all('section', class_="builds-list platform-linux")
selected = []
for section in download_blocks:
    selected.extend(section.select('li a'))

print(extract_infos(selected[1]))

download_build(extract_infos(selected[1]))
