import requests

sb = requests.Session()
a = sb.get('http://httpbin.org/cookies/set/number/123456789')
print(a.cookies)

r = sb.get('http://httpbin.org/cookies')
print(r.cookies)

print(r.text)