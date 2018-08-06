import requests
import getpass

login_url = "https://www.hackerrank.com/auth/login"
login_data = {"login":"rajatgoyal715", "password":getpass.getpass('Password: ')}

r = requests.post(login_url, data=login_data)
print(r.request.headers)