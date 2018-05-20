#!/usr/bin/python3

import requests as req
import json
from random import Random

token = open('token', 'rt').read()
url = 'https://api.telegram.org/bot{token}/'.format(token = token)
urly = lambda method: url + method
proxies = {
  'https': 'socks5://127.0.0.1:9050',
  'http': 'socks5://127.0.0.1:9050',
}
log = print
random = Random()

offset = 0
users = dict()
handles = dict()

locale = { 'en': json.load(open('locale/en', 'rt')) }

def genHandle():
  alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_-'
  res = ''
  for i in range(64):
    res += random.choice(alphabet)
  return res

def isHandle(handle):
  res = (len(handle) == 64)
  alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_-'
  for c in handle:
    res = res and (c in alphabet)
    if not res:
      return False
  return True

def query(method, **dct):
  response = req.post(urly(method), data = dct, proxies = proxies)
  result = response.json()
  return result

def process_update(update):
  global users, handles
  if 'message' not in update:
    return
  message = update['message']
  if message['chat']['id'] not in users:
    users[message['chat']['id']] = [None, [], 0]
  
  state = users[message['chat']['id']][0]
  if state == None: # user was doing nothing
    if message['text'] == '/start':
      query('sendMessage', offset = offset, chat_id = message['chat']['id'],
            text = locale['en']['greeting'].format(first_name = message['from']['first_name']), parse_mode = 'Markdown')
      return
    if message['text'] == '/new':
      while True:
        handle = genHandle()
        if handle not in handles:
          break
      handles[handle] = message['chat']['id']
      users[message['chat']['id']][1].append(handle)
      query('sendMessage', offset = offset, chat_id = message['chat']['id'],
            text = locale['en']['new_handle'].format(index = len(users[message['chat']['id']][1]), handle = handle), parse_mode = 'Markdown')
      return
    if message['text'].partition(' ')[0] == '/del':
      handle = message['text'].partition(' ')[2]
      if isHandle(handle):
        query('sendMessage', offset = offset, chat_id = message['chat']['id'],
              text = locale['en']['wrong_args'].format(correct = '/del <handle>'), parse_mode = 'Markdown')
        return
      if handle not in handles:
        query('sendMessage', offset = offset, chat_id = message['chat']['id'],
              text = locale['en']['handle_not_found'], parse_mode = 'Markdown')
        return
      handles[handle] = None
      users[message['chat']['id']][1].pop(handle)
      return
    if message['text'].partition(' ')[0] == '/from':
      index = message['text'].partition(' ')[2]
      if not index.isdigit():
        query('sendMessage', offset = offset, chat_id = message['chat']['id'],
              text = locale['en']['wrong_args'].format(correct = '/from <index:int>'), parse_mode = 'Markdown')
        return
      index = int(index)
      if index > len(users[message['chat']['id']][1]):
        query('sendMessage', offset = offset, chat_id = message['chat']['id'],
              text = locale['en']['index_out_of_bounds'], parse_mode = 'Markdown')
        return
      users[message['chat']['id']][2] = index - 1
      return
    if message['text'].partition(' ')[0] == '/send':
      handle = message['text'].partition(' ')[2]
      if not isHandle(handle):
        query('sendMessage', offset = offset, chat_id = message['chat']['id'],
              text = locale['en']['wrong_args'].format(correct = '/send <handle>'), parse_mode = 'Markdown')
        return
      if handle not in handles:
        query('sendMessage', offset = offset, chat_id = message['chat']['id'],
              text = locale['en']['handle_not_found'], parse_mode = 'Markdown')
        return
      query('sendMessage', offset = offset, chat_id = message['chat']['id'],
            text = locale['en']['send_text'], parse_mode = 'Markdown')
      users[message['chat']['id']].append(handle)
      users[message['chat']['id']][0] = 'sending'
      return
    if message['text'] == '/help':
      query('sendMessage', offset = offset, chat_id = message['chat']['id'],
            text = locale['en']['help'], parse_mode = 'Markdown')
    if message['text'] == '/cancel':
      users[message['chat']['id']][0] = None
      return
    query('sendMessage', offset = offset, chat_id = message['chat']['id'],
         text = locale['en']['unknown_command'], parse_mode = 'Markdown')
    return
  if state == 'sending':
    handle = users[message['chat']['id']][-1]
    query('sendMessage', offset = offset, chat_id = handles[handle],
         text = '*From:* `{from_}`\n*To:* `{to}`\n\n{text}'.format(from_ = users[message['chat']['id']][1][users[message['chat']['id']][2]],
                                                                 to = handle, text = message['text']), parse_mode = 'Markdown')
    handle = users[message['chat']['id']].pop()
    users[message['chat']['id']][0] = None
    return

def print_dict(dct):
  print(json.dumps(dct, sort_keys = True, indent = 4, ensure_ascii = False))

#ans = query('sendMessage', offset = 4086476, chat_id = 250918540, text = '[googlemoogle](https://google.com/)', parse_mode = 'Markdown')
#print_dict(query('getUpdates'))
while True:
  ans = query('getUpdates', offset = offset)
  if len(ans['result']) == 0:
    print('.', end = '')
  else:
    print('\nNew updates!')
  for update in ans['result']:
    print_dict(update)
    process_update(update)
    offset = update['update_id'] + 1