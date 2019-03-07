import urllib.request
import re
from bs4 import BeautifulSoup

download_url = 'https://builder.blender.org/download/'

def extract_infos(a_tag):
    download_url = a_tag['href']
    build_name = a_tag.find('span', class_='name').contents[0]
    build_date = a_tag.find('span', class_='name').select('small')[0].get_text()
    build_type = a_tag.find('span', class_='build').get_text()
    build_size = a_tag.find('span', class_='size').get_text()
    infos = {
        'build_name': build_name,
        'build_date': build_date,
        'build_type': build_type,
        'build_size': build_size,
        'download_url': download_url
    }
    return infos

# Reading blender builder download web page
with urllib.request.urlopen(download_url) as response:
    html = response.read()

soup = BeautifulSoup(html, 'html.parser')

download_blocks = soup.find_all('section', class_="builds-list")

selected = []
for section in download_blocks:
    selected.extend(section.select('li a'))

for tag in selected:
    print(extract_infos(tag))

