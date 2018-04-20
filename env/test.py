import requests
from bs4 import BeautifulSoup

baseurl = 'https://en.wikipedia.org/wiki/Chicago'
page_text = requests.get(baseurl).text
page_soup = BeautifulSoup(page_text, 'html.parser')

content = page_soup.find_all(class_='mergedrow')
result=[]
for c in content:
	result.append(c.text.strip())
print(result)