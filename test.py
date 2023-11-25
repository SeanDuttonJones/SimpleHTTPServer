import requests
from requests import Request, Session
from email.utils import formatdate

# data = "Sean is Cool!"

# s = Session()
# req = Request("JPS", "http://localhost/")
# prepped = req.prepare()
# r = s.send(prepped)
# print(r.status_code)

# r = requests.get("http://localhost/test.html", headers={"If-Modified-Since": formatdate(timeval=None, localtime=False, usegmt=True)})
# print(r.text)
# print(r.status_code)

proxy = {
    "http": "http://localhost:8888"
}

# r = requests.get("http://eu.httpbin.org/")
# # print(r.text)
# print(r.headers)
# print(r.status_code)

r = requests.post("http://eu.httpbin.org/post", proxies=proxy)
print(r.text)
print(r.headers)
print(r.status_code)