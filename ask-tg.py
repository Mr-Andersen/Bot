#!/usr/bin/python3

import requests as req
import json

token = open('token', 'rt').read()
url = 'https://api.telegram.org/bot{token}/'.format(token = token)
urly = lambda method: url + method
proxies = {
  'https': 'socks5://127.0.0.1:9050',
  'http': 'socks5://127.0.0.1:9050',
}

def query(method, **dct):
  response = req.post(urly(method), data = dct, proxies = proxies)
  result = response.json()
  return result

def print_dict(dct):
  print(json.dumps(dct, sort_keys = True, indent = 4, ensure_ascii = False))

ans = query('getUpdates')
print_dict(ans)