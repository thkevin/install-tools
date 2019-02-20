import urllib.request
import re

download_url = 'https://builder.blender.org/download/'

with urllib.request.urlopen(download_url) as response:
   html = response.read()

encoding = re.findall(r'<meta.*?charset=["\']*(.+?)["\'>]', html.decode(), flags=re.I)[0]

print(encoding)

