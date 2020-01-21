# Debian Linux blender download and install from blender builder

# pip install beautifulsoup
# sudo apt-get install python3-bs4
from utils import *

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
