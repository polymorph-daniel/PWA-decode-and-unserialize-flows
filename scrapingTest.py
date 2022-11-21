import requests
from bs4 import BeautifulSoup

from pypodio2 import api
from client_settings import *

c = api.OAuthClient(
    client_id,
    client_secret,
    username,
    password,    
)
print c.Item.find(22342)

page = requests.get("https://workflow-automation.podio.com/flows.php")
page

print(page.status_code)

soup = BeautifulSoup(page.content, 'html.parser')
print(soup.prettify())