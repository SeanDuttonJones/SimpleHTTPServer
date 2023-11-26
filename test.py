import requests
from requests import Request, Session
from email.utils import formatdate
import datetime

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

# r = requests.post("http://eu.httpbin.org/post", proxies=proxy)
# print(r.text)
# print(r.headers)
# print(r.status_code)
### 200 OK ###
print("\033[1;32m200 OK Proxy Testing\033[0m")
r = requests.get("http://localhost/test.html")
print("Content-Length:", r.headers["content-length"])
print("Status Code:", r.status_code, "OK")
print()

### 403 Forbidden ###
print("\033[1;32m403 Forbidden Proxy Testing\033[0m")
r = requests.get("http://localhost/forbidden")
print("Status Code:", r.status_code, "Forbidden")
print()

### 404 Not Found ###
print("\033[1;32m404 Not Found Proxy Testing\033[0m")
r = requests.get("http://localhost:80/a_page_that_does_not_exist.html")
print("Status Code:", r.status_code, "Not Found")
print()

### 304 Not Modified ###
print("\033[1;32m304 Not Modified Testing\033[0m")
# January 1, 1970
print("--- If-Modified-Since: January 1, 1970 ---")
r = requests.get("http://localhost/test.html", headers={"If-Modified-Since": formatdate(timeval=0, localtime=False, usegmt=True)})
print("Status Code:", r.status_code, "OK")

print()
# Current Time
print("--- If-Modified-Since: Now ---")
r = requests.get("http://localhost/test.html", headers={"If-Modified-Since": formatdate(timeval=None, localtime=False, usegmt=True)})
print("Status Code:", r.status_code, "Not Modified")
print()

### 411 Length Required ###
data = "Sean is Cool!"

print("\033[1;32m411 Length Required Proxy Testing\033[0m")
print("--- GET ---")
s = Session()
req = Request("GET", "http://localhost/test.html", data=data)
prepped = req.prepare()
del prepped.headers["content-length"]
r = s.send(prepped)
print("Status Code:", r.status_code, "Length Required")
print()

print("--- POST ---")
s = Session()
req = Request("POST", "http://localhost/test.html", data=data)
prepped = req.prepare()
del prepped.headers["content-length"]
r = s.send(prepped)
print("Status Code:", r.status_code, "Length Required")
print()

print("--- HEAD ---")
s = Session()
req = Request("HEAD", "http://localhost/test.html", data=data)
prepped = req.prepare()
del prepped.headers["content-length"]
r = s.send(prepped)
print("Status Code:", r.status_code, "Length Required")
print()

print("--- PUT ---")
s = Session()
req = Request("PUT", "http://localhost/test.html", data=data)
prepped = req.prepare()
del prepped.headers["content-length"]
r = s.send(prepped)
print("Status Code:", r.status_code, "Length Required")
print()

print("--- DELETE ---")
s = Session()
req = Request("DELETE", "http://localhost/test.html", data=data)
prepped = req.prepare()
del prepped.headers["content-length"]
r = s.send(prepped)
print("Status Code:", r.status_code, "Length Required")
print()

### Bad Request ###
print("\033[1;32m400 Bad Request Proxy Testing\033[0m")
s = Session()
req = Request("JPS", "http://localhost/test.html")
prepped = req.prepare()
r = s.send(prepped)
print("Status Code:", r.status_code, "Bad Request")
print()