import requests
from bs4 import BeautifulSoup


page = requests.get("https://workflow-automation.podio.com/flows.php")
page

print(page.status_code)git

soup = BeautifulSoup(page.content, 'html.parser')
print(soup.prettify())