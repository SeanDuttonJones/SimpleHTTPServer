import requests
from requests import Request, Session
from email.utils import formatdate

# data = "Sean is Cool!"

# s = Session()
# req = Request("JPS", "http://localhost/")
# prepped = req.prepare()
# r = s.send(prepped)
# print(r.status_code)

r = requests.get("http://localhost/test.html", headers={"If-Modified-Since": formatdate(timeval=None, localtime=False, usegmt=True)})
print(r.text)
print(r.status_code)