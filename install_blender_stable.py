# Debian Linux blender download and install from blender builder

# pip install beautifulsoup
# sudo apt-get install python3-bs4
from utils import *
from bs4 import BeautifulSoup
from distutils.version import LooseVersion


DOWNLOAD_PAGE = 'https://download.blender.org/release/'
# INSTALL_DIR = '/opt/'
INSTALL_DIR = ''.join([HOME, '/blender_install_tools/'])  # using /tmp instead of /opt.. For now
DOWNLOAD_DIR = ''.join([DOWNLOAD_DIR, 'blender_stable/'])
print(DOWNLOAD_DIR)

# bs4 a tags object that return all
def release_infos(bs4_a_tag, regex='Blender(.*)/', base_link=DOWNLOAD_PAGE):
    version_regex = re.compile(regex, re.IGNORECASE)
    href = bs4_a_tag.get("href")
    version_search = re.search(version_regex, href)
    if version_search:
        version = version_search.group(1)
        if not re.match(r'^[0-9]', version):
            version = None
    else:
        version = None
    release = {
        'version': version,
        'folder': href,
        'link': ''.join([base_link, href])
    }
    return release


# Download blender build linux file
# Return a tuple (Exist, Downloaded, Path)
def download_blender_stable(download_url=DOWNLOAD_PAGE, download_path=DOWNLOAD_DIR):
    create_folder(download_path)

    # Reading blender release web page
    with urllib.request.urlopen(download_url) as response:
        html = response.read()
    soup = BeautifulSoup(html, 'html.parser')
    a_tags = soup.find_all("a")

    links = [a for a in a_tags if a.get("href").startswith("Blender")]
    all_releases = [r for r in list(map(release_infos, links)) if r['version']]
    last_release = all_releases[0]

    for m in all_releases:
        if LooseVersion(m['version']) > LooseVersion(last_release['version']):
            last_release = m

    # Listing release folder index
    with urllib.request.urlopen(last_release['link']) as response:
        html = response.read()
    soup = BeautifulSoup(html, 'html.parser')
    a_tags = soup.find_all("a")

    r_tags = [release_infos(a, 'blender-(.*)-linux', last_release['link']) for a in a_tags]
    linux_releases = [l for l in r_tags if l['version']]

    # Getting release's lastest stable archive
    latest_linux = linux_releases[0]
    latest_linux_version = latest_linux['version']
    for l in linux_releases:
        if LooseVersion(l['version']) > LooseVersion(latest_linux_version):
            latest_linux = l
    print(' '.join(["Last release :", latest_linux_version]))

    filename = latest_linux['link'].split('/').pop()
    file_path = os.path.realpath(''.join([download_path, '/', filename]))

    download_file(latest_linux['link'], file_path)
    print(os.stat(file_path))

    return file_path


extract_blender_archive(download_blender_stable(), INSTALL_DIR)
