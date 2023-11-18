import requests
from requests import Request, Session

data = "Sean is Cool!"

s = Session()
req = Request("JPS", "http://localhost/")
prepped = req.prepare()
r = s.send(prepped)
print(r.status_code)