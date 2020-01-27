# Debian Linux blender download and install from blender builder

# pip install beautifulsoup
# sudo apt-get install python3-bs4
from utils import *


DOWNLOAD_PAGE = 'https://download.blender.org/release/'
# INSTALL_DIR = '/opt/'
INSTALL_DIR = '/tmp/'  # using /tmp instead of /opt.. For now

DOWNLOAD_DIR = DOWNLOAD_DIR + 'blender_stable/'

# bs4 a tags object that return all 
def release_infos(bs4_a_tag):
    href = bs4_a_tag.get("href")
    version_search = re.search(r'Blender(.*)/', href, re.IGNORECASE)
    version = version_search.group(1)
    if not re.match(r'^[0-9]',version):
        version = None
    release = {
        'version' : version,
        'folder' : href,
        'link' : DOWNLOAD_PAGE + href
    }
    return release


def download_blender_stable(download_url=DOWNLOAD_PAGE, download_path=DOWNLOAD_DIR):
    create_folder(download_path)

    # Reading blender release web page
    with urllib.request.urlopen(download_url) as response:
        html = response.read()
    soup = BeautifulSoup(html, 'html.parser')

    a_tags = [a for a in soup.find_all("a") if a.get("href").startswith("Blender")]
    all_releases = [r for r in list(map(release_infos, a_tags)) if r['version']]
    last_release = all_releases[0]

    for m in all_releases:
        if LooseVersion(m['version']) > LooseVersion(last_release['version']):
            last_release = m

    print("Downloading release: " + last_release['version'])

    # Listing release folder index
    with urllib.request.urlopen(last_release['link']) as response:
        html = response.read()
    soup = BeautifulSoup(html, 'html.parser')

    print(soup.find_all("a"))

    # splitted_url = [p for p in download_url.split('/') if p]
    # filename = splitted_url.pop()
    # file_path = os.path.realpath(download_path + '/' + filename)
    # print(download_url[:-1])
    # stable_download = download_file(download_url[:-1], file_path)
    # print(os.stat(stable_download[2]))
    return

download_blender_stable()
