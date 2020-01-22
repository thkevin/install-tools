# Debian Linux blender download and install from blender builder

# pip install beautifulsoup
# sudo apt-get install python3-bs4
from utils import *


DOWNLOAD_PAGE = 'https://www.blender.org/download/'
INSTALL_DIR = '/opt/'


# Reading blender builder web page
with urllib.request.urlopen(DOWNLOAD_PAGE) as response:
    html = response.read()
soup = BeautifulSoup(html, 'html.parser')
linux_sect = soup.find(id = "linux")

download_url = linux_sect.find("a", dl_stats=re.compile("^Linux *")).get('href')
md5_url = linux_sect.find(class_="md5").a.get('href')

print(download_url)
print(md5_url)
