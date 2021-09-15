# Debian Linux blender download and install from blender builder

# pip install beautifulsoup
# sudo apt-get install python3-bs4
from utils import *
from bs4 import BeautifulSoup

BUILDER_PAGE = 'https://builder.blender.org/'
BUILD_DIR = ''.join([HOME, '/blender_builder/'])
DOWNLOAD_DIR = ''.join([DOWNLOAD_DIR, 'blender_build/'])


# Parse dedicated html tag for infos
def extract_build_infos(a_tag):
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


# Download blender build linux file
# Return a tuple (Exist, Downloaded, Path)
def download_blender_build(selected_build, download_path=DOWNLOAD_DIR):
    name = selected_build['build_name']
    date = selected_build['build_date']
    size = selected_build['build_size']
    extension = selected_build['download_extension']

    download_url = ''.join([BUILDER_PAGE, extension])
    filename = extension.split('/').pop()
    file_path = ''.join([download_path, filename])

    create_folder(download_path)
    # Clean downloads older than 7 days in download folder
    clean_files("blender.*tar.*", download_path, 7 * 24)

    # Download build
    build_download = download_file(download_url, file_path)

    # check downloaded file by comparing the expected and actual sizes
    if build_download[1]:
        file_infos = os.stat(file_path)
        if greater_size(str(size), str(humanbytes(file_infos.st_size))):
            print("Expected size downloaded")
            print(''.join([name,' downloaded as ',file_path]))
            return build_download
        else:
            print("Expected size not reached")
            # Removing corrupted file
            os.remove(file_path)
            print("Corrupted file removed")
            return False, False, None
    else:
        return(build_download)


# Reading blender builder web page
with urllib.request.urlopen(BUILDER_PAGE + 'download') as response:
    html = response.read()
soup = BeautifulSoup(html, 'html.parser')

# Retrieving linux builds infos
download_blocks = soup.find_all('section', class_="builds-list platform-linux")

selected = []
for section in download_blocks:
    selected.extend(section.select('li a'))

result_download = download_blender_build(extract_build_infos(selected[0]))

if result_download[1]:  # Extract file only when it is downloaded
    print("Extracting")
    extract_blender_archive(result_download[2], BUILD_DIR)
