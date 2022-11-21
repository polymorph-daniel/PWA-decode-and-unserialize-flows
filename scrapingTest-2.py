from bs4 import BeautifulSoup
import requests
import re
import urllib.parse

client = requests.Session()

email = "dgarcia@nanmckay-sub.com"
password = "ij.7&frJ#%XzC@n"
HOMEPAGE_URL = "https://workflow-automation.podio.com/"
LOGIN_URL = ''
#LOGIN_URL = "https://podio.com/login_clientside"

csrf = "not found"

html = client.get(HOMEPAGE_URL).content
soup = BeautifulSoup(html, "html.parser")
for item in soup.find_all(id="login-link"):
    LOGIN_URL = item.get("href")
    csrf = urllib.parse.parse_qs(urllib.parse.urlparse(LOGIN_URL).query)['state'][0]
    print("login url: " + LOGIN_URL)
    print("csrf: " + csrf)

html = client.get(LOGIN_URL)

login_information = {
    'email':email,
    'password':password,
    'return_to': 'https://podio.com/oauth/authorize?response_type=code&client_id=globi-flow&redirect_uri=https%3A%2F%2Fworkflow-automation.podio.com%2Flogin.php%3Fa%3Dlogin&state=' + csrf,
    'remember_me': True
}

r = client.post(LOGIN_URL, data=login_information)

print(r.text)
#print(r.history)
#print(client)
