import requests
from requests import Request, Session

data = "Sean is Cool!"

s = Session()
req = Request("POST", "http://localhost/", data=data)
prepped = req.prepare()
del prepped.headers["content-length"]
r = s.send(prepped)
print(r.status_code)