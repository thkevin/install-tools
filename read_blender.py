import urllib.request
import re

download_url = 'https://www.blender.org/download/'

with urllib.request.urlopen(download_url) as response:
   html = response.read()

encoding = re.findall(r'<meta.*?charset=["\']*(.+?)["\'>]', html, flags=re.I)[0]

print(encoding)
