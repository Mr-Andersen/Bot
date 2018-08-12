#!/usr/bin/python3

import requests as req
import json
import sqlite3 as sql
from os import listdir
import signal

from db_tools import *
from log_tools import *

def cleanExit(signal = None, frame = None):
  logNote(g, 'Exiting cleanly')
  g.db.close()
  exit(0)

# === Handles functions ===
def genHandle():
  alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-'
  res = ''
  for i in range(64):
    res += random.choice(alphabet)
  return res

def isHandle(handle):
  if len(handle) != 64:
    return False
  alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-'
  for c in handle:
    if c not in alphabet:
      return False
  return True

# === Tg API functions ===
def tgQuery(method, **dct):
  error = 0
  while True:
    try:
      response = req.post(g.urly(method), data = dct, proxies = g.proxies)
      break
    except req.exceptions.ConnectionError:
      if error == 0:
        logError(g, 'sending query')
      logStatus(g, 'Retrying query')
      error += 1
  result = response.json()
  logStatus(g, 'Sent query')
  return result

# === other functions ===
def sendAnswer(type_, chat_id, locale_lang = 'en', **kwargs):
  logStatus(g, 'Answering to {chat_id}'.format(chat_id = chat_id))
  res = tgQuery('sendMessage', disable_web_page_preview = True, offset = g.offset, chat_id = chat_id,
                text = g.locale[locale_lang][type_].format(**kwargs),
                parse_mode = 'HTML')
  if res['ok'] != True:
    logError(g, while_ = 'sending answer', more = { 'server answer': res['description'],
                                                 'chat_id': chat_id,
                                                 'text': g.locale[locale_lang][type_].format(**kwargs) })
  else:
    logNote(g, 'Answer {type_} to {chat_id} sent'.format(type_ = type_, chat_id = chat_id))

def process_update(update):
  logStatus(g, 'Processing update {index}'.format(index = update['update_id']))
  if 'message' not in update or 'text' not in update['message']:
    return
  message = update['message']
  chat_id = message['chat']['id']
  if getUser(g.db, chat_id) == None:
    addUser(g.db, chat_id)
  
  if 'reply_to_message' in message:
    if message['reply_to_message']['from']['username'] == 'anonymous_chat_ro_bot' and \
       message['reply_to_message']['text'][:5] == 'From:' and \
       message['reply_to_message']['text'][71:74] == 'To:':
       to = message['reply_to_message']['text'][6:70]
       sendAnswer('letter', getHandle(g.db, to)['chat_id'], from_ = message['reply_to_message']['text'][75:139],
                  to = to, text = message['text'])
       return sendAnswer('letter_sent', chat_id)
    return sendAnswer('wrong_reply', chat_id)

  state = getUser(g.db, chat_id)['state']
  command, *args = message['text'].split()
  command = command.split('@')[0]

  if command == '/cancel':
    setUserState(g.db, getUser(g.db, chat_id)['hashed_chat_id'], None)
    return sendAnswer('cancelled', chat_id)

  if state == None: # user was doing nothing

    if command == '/start':
      if len(args) == 0:
        return sendAnswer('greeting', chat_id, first_name = message['from']['first_name'])
      elif len(args) == 1 and isHandle(args[0]):
        hashed_chat_id = getUser(g.db, chat_id)['hashed_chat_id']
        setUserBuffer(g.db, hashed_chat_id, { 'target': args[0] })
        setUserState(g.db, hashed_chat_id, 'sending')
        return sendAnswer('fast_send', chat_id, handle = args[0])
      return sendAnswer('wrong_args', chat_id, correct = '/start [&lt handle &gt]')

    if command == '/new':
      while True:
        handle = genHandle()
        if getHandle(g.db, handle) == None:
          break
      addHandle(g.db, handle, chat_id, len(userHandles(g.db, chat_id)))
      return sendAnswer('new_handle', chat_id, index = len(userHandles(g.db, chat_id)), handle = handle)

    if command == '/del':
      if len(args) != 1 or not isHandle(args[0]):
        return sendAnswer('wrong_args', chat_id, correct = '/del &lt handle &gt')
      handle = args[0]
      handle = getHandle(g.db, handle)
      if handle == None or handle['chat_id'] != chat_id:
        return sendAnswer('handle_not_found', chat_id)

      disableHandle(g.db, handle['handle'], message['date'] // 86400)
      #logNote(g, 'USERHANDLES: {}'.format(userHandles(g.db, chat_id)))
      for i in userHandles(g.db, chat_id):
        #logNote(g, 'HANDLE: ' + print_dict(i))
        if i['index_'] > handle['index_']:
          setHandleIndex(g.db, i['handle'], i['index_'] - 1)

      return sendAnswer('handle_disabled', chat_id)

    if command == '/del_all':
      for handle in userHandles(g.db, chat_id):
        disableHandle(g.db, handle['handle'], message['date'] // 86400)
      return sendAnswer('empty', chat_id, content = 'Deleted all')

    if command == '/from':
      if len(args) != 1 or not args[0].isdigit():
        return sendAnswer('wrong_args', chat_id, correct = '/from &lt int:index &gt')
      index = int(args[0])
      setUserFrom(g.db, getUser(g.db, chat_id)['hashed_chat_id'], index - 1)
      return sendAnswer('set_from', chat_id, index = index)

    if command == '/send':
      if len(args) != 1 or not isHandle(args[0]):
        return sendAnswer('wrong_args', chat_id, correct = '/send &lt handle &gt')
      handle = args[0]
      if getHandle(g.db, handle) == None:
        return sendAnswer('handle_not_found', chat_id)
      if getUser(g.db, chat_id)['from_'] == None:
        return sendAnswer('from_not_set', chat_id)
      hashed_chat_id = getUser(g.db, chat_id)['hashed_chat_id']
      setUserBuffer(g.db, hashed_chat_id, { 'target': handle })
      setUserState(g.db, hashed_chat_id, 'sending')
      return sendAnswer('send_text', chat_id)

    if command == '/list':
      res = ''
      for handle in userHandles(g.db, chat_id):
        res += '{index}, <a href=\'https://t.me/anonymous_chat_ro_bot?start={handle}\'>link</a>: <pre>{handle}</pre>\n\n'.format(index = handle['index_'] + 1, handle = handle['handle'])
      return sendAnswer('empty', chat_id, content = res if res != '' else 'You have no handles')

    if command == '/help':
      return sendAnswer('help', chat_id)

  if state == 'verify_send':
    user = getUser(g.db, chat_id)
    if message['text'] == 'yes':
      handle = userHandles(g.db, chat_id)[user['from_']]['handle']
      target_handle = user['buffer_']['target']
      text = user['buffer_']['message_text']
      sendAnswer('letter', getHandle(g.db, target_handle)['chat_id'], from_ = handle, to = target_handle, text = text)
      setUserState(g.db, user['hashed_chat_id'], None)
      setUserBuffer(g.db, user['hashed_chat_id'], None)
      return sendAnswer('letter_sent', chat_id)
    setUserState(g.db, user['hashed_chat_id'], None)
    setUserBuffer(g.db, user['hashed_chat_id'], None)
    return sendAnswer('empty', chat_id, content = 'You sent something not equal to "yes", so operation cancelled')

  if state == 'sending':
    if message['text'][0] == '/':
      user = getUser(g.db, chat_id)
      new_buffer_ = user['buffer_']
      new_buffer_['message_text'] = message['text']
      setUserBuffer(g.db, user['hashed_chat_id'], new_buffer_)
      setUserState(g.db, user['hashed_chat_id'], 'verify_send')
      return sendAnswer('verify', chat_id)
    user = getUser(g.db, chat_id)
    handle = userHandles(g.db, chat_id)[user['from_']]['handle']
    target_handle = user['buffer_']['target']
    sendAnswer('letter', getHandle(g.db, target_handle)['chat_id'], from_ = handle, to = target_handle, text = message['text'])
    setUserState(g.db, user['hashed_chat_id'], None)
    setUserBuffer(g.db, user['hashed_chat_id'], None)
    return sendAnswer('letter_sent', chat_id)

  return sendAnswer('unknown_command', chat_id)

def print_dict(dct):
  return json.dumps(dct, sort_keys = True, indent = 4, ensure_ascii = False)

class Struct:
  pass

g = Struct()

# === main action ===
def main():
  signal.signal(signal.SIGINT, cleanExit)

  token = open('token', 'rt').read()
  url = 'https://api.telegram.org/bot{token}/'.format(token = token)
  g.urly = lambda method: url + method
  g.proxies = {
    'https': 'socks5://127.0.0.1:9050',
    'http': 'socks5://127.0.0.1:9050',
  }

  g.offset = 0
  g.log_len = 0
  
  g.locale = dict()
  for l in listdir('locale'):
    logStatus(g, 'Loading {locale} locale'.format(locale = l))
    g.locale[l] = json.load(open('locale/{locale}'.format(locale = l), 'rt'))
    logNote(g, 'Loaded {locale} locale'.format(locale = l))

  g.db = sql.connect('database.db')

  if not tableInDB(g.db, 'handles'):
    addTable(g.db, 'handles', 'handle CHAR(64), chat_id INT, index_ INT')
    logStatus(g, 'Created "handles" table')
  else:
    logStatus(g, 'Found existing "handles" table')
  logNote(g, 'Table "handles" opened')

  if not tableInDB(g.db, 'users'):
    addTable(g.db, 'users', 'hashed_chat_id BLOB, salt INT, state TEXT, from_ INT, buffer_ BLOB')
    logStatus(g, 'Created "users" table')
  else:
    logStatus(g, 'Found existing "users" table')
  logNote(g, 'Table "users" opened')

  while True:
    ans = tgQuery('getUpdates', offset = g.offset)
    for update in ans['result']:
      process_update(update)
      logNote(g, 'Update {update_id} processed'.format(update_id = update['update_id']))
      g.offset = update['update_id'] + 1

if __name__ == '__main__':
  main()
