#!/usr/bin/python3

import requests as req
import json
import sqlite3 as sql
from random import Random
from os import listdir

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
  response = req.post(urly(method), data = dct, proxies = proxies)
  result = response.json()
  return result

# === handle db funcitons ===
def addHandle(handle, chat_id):
  db.execute('INSERT INTO handles VALUES (\'{handle}\', {chat_id}, NULL);'.format(handle = handle, chat_id = chat_id))
  db.commit()

def handleInDB(handle):
  return len(db.execute('SELECT handle FROM handles WHERE handle = \'{handle}\';'.format(handle = handle)).fetchall()) > 0

def getHandle(handle):
  return db.execute('SELECT * FROM handles WHERE handle = \'{handle}\';'.format(handle = handle)).fetchall()[0] # because handles are unique

def userHandles(chat_id):
  return set([ tuple_[0] for tuple_ in db.execute('SELECT handle FROM handles WHERE chat_id = {chat_id};'.format(chat_id = chat_id)).fetchall() ])

def disableHandle(handle, date):
  db.execute('UPDATE handles SET chat_id = NULL, date = {date} WHERE handle = \'{handle}\';'.format(handle = handle, date = date))
  db.commit()

def eraseHandle(handle):
  db.execute('DELETE FROM handles WHERE handle = \'{handle}\';')
  db.commit()

# === user db functions ===
def addUser(chat_id):
  db.execute('INSERT INTO users VALUES ({chat_id}, \'\', \'\');'.format(chat_id = chat_id))
  db.commit()

def userInDB(chat_id):
  return len(db.execute('SELECT * FROM users WHERE chat_id = {chat_id};'.format(chat_id = chat_id)).fetchall()) > 0

def getUser(chat_id):
  return db.execute('SELECT * FROM users WHERE chat_id = {chat_id};'.format(chat_id = chat_id)).fetchall()[0] # users are also unique

def setUserFrom(chat_id, from_):
  db.execute('UPDATE users SET from_ = \'{from_}\''.format(from_ = from_))
  db.commit()

def setUserState(chat_id, state):
  db.execute('UPDATE users SET state = \'{state}\''.format(state = state))
  db.commit()

# === Log functions ===
def logNote(str_):
  global log_len
  print('N: {str_}'.format(str_ = str_).ljust(log_len))
  log_len = 0

def logError(while_, more = ''):
  global log_len
  print('E: While {while_}{more}'.format(while_ = while_, more = '\n' + more if more != '' else '').ljust(log_len))
  log_len = 0

def logStatus(str_):
  global log_len
  print('S:', str_.ljust(log_len), end = '\r')
  log_len = len(str_) + 3

# === other functions ===
def sendAnswer(type_, chat_id, locale_lang = 'en', **kwargs):
  logStatus('Answering to {chat_id}'.format(chat_id = chat_id))
  res = tgQuery('sendMessage', offset = offset, chat_id = chat_id,
                text = locale[locale_lang][type_].format(**kwargs),
                parse_mode = 'Markdown')
  if res['ok'] != True:
    logError(while_ = 'sending answer', more = { 'server answer': res['description'],
                                                 'chat_id': chat_id,
                                                 'text': locale[locale_lang][type_].format(**kwargs) })
  else:
    logNote('Answer {type_} to {chat_id} sent'.format(type_ = type_, chat_id = chat_id))

def process_update(update):
  logStatus('Processing update {index}'.format(index = update['update_id']))
  if 'message' not in update:
    return
  message = update['message']
  chat_id = message['chat']['id']
  if not userInDB(chat_id):
    addUser(chat_id)
  
  if 'reply_to_message' in message:
    if message['reply_to_message']['from']['username'] == 'anonymous_chat_ro_bot' and \
       message['reply_to_message']['text'][:5] == 'From:' and \
       message['reply_to_message']['text'][71:74] == 'To:':
       to = message['reply_to_message']['text'][6:70]
       sendAnswer('letter', getHandle(to)[1], from_ = message['reply_to_message']['text'][75:139],
                  to = to, text = message['text'])
       return sendAnswer('letter_sent', chat_id)
    return sendAnswer('wrong_reply', chat_id)

  state = getUser(chat_id)[1]
  command, *args = message['text'].split()
  if state == '': # user was doing nothing

    if command == '/start':
      return sendAnswer('greeting', chat_id, first_name = message['from']['first_name'])

    if command == '/new':
      while True:
        handle = genHandle()
        if not handleInDB(handle):
          break
      addHandle(handle, chat_id)
      return sendAnswer('new_handle', chat_id, index = len(userHandles(chat_id)), handle = handle)

    if command == '/del':
      if len(args) != 1 or not isHandle(args[0]):
        return sendAnswer('wrong_args', chat_id, correct = '/del <handle>')
      handle = args[0]
      if not handleInDB(handle) or getHandle(handle)[1] != chat_id:
        return sendAnswer('handle_not_found', chat_id)
      disableHandle(handle, message['date'] // 86400)
      if getUser(chat_id)[2] == handle:
        setUserFrom(chat_id, '')
      return sendAnswer('handle_disabled', chat_id)

    if command == '/from':
      if len(args) != 1:
        return sendAnswer('wrong_args', chat_id, correct = '/from <handle>')
      handle = args[0]
      if not handleInDB(handle) or getHandle(handle)[1] != chat_id:
        logNote(handleInDB(handle))
        return sendAnswer('handle_not_found', chat_id)
      setUserFrom(chat_id, handle)
      return sendAnswer('set_from', chat_id, handle = handle)

    if command == '/send':
      if len(args) != 1 or not isHandle(args[0]):
        return sendAnswer('wrong_args', chat_id, correct = '/send <handle>')
      handle = args[0]
      if not handleInDB(handle):
        return sendAnswer('handle_not_found', chat_id)
      if getUser(chat_id)[2] == '':
        return sendAnswer('from_not_set', chat_id)
      buffer_[chat_id] = handle
      setUserState(chat_id, 'sending')
      return sendAnswer('send_text', chat_id)

    if command == '/list':
      res = '\n\n'.join([ '`{handle}`'.format(handle = handle) for handle in userHandles(chat_id) ])
      return sendAnswer('empty', chat_id, content = res if res != '' else 'You have no handles')

    if command == '/help':
      return sendAnswer('help', chat_id)

    if command == '/cancel':
      setUserState(chat_id, '')
      return sendAnswer('cancelled', chat_id)
    return sendAnswer('unknown_command', chat_id)

  if state == 'sending':
    handle = getUser(chat_id)[2]
    sendAnswer('letter', getHandle(buffer_[chat_id])[1], from_ = handle, to = buffer_[chat_id], text = message['text'])
    setUserState(chat_id, '')
    del buffer_[chat_id]
    return sendAnswer('letter_sent', chat_id)

def print_dict(dct):
  return(json.dumps(dct, sort_keys = True, indent = 4, ensure_ascii = False))

# === main action ===
token = open('token', 'rt').read()
url = 'https://api.telegram.org/bot{token}/'.format(token = token)
urly = lambda method: url + method
proxies = {
  'https': 'socks5://127.0.0.1:9050',
  'http': 'socks5://127.0.0.1:9050',
}
random = Random()

offset = 0
buffer_ = dict()
log_len = 0

locale = dict()
for l in listdir('locale'):
  logStatus('Loading {locale} locale'.format(locale = l))
  locale[l] = json.load(open('locale/{locale}'.format(locale = l), 'rt'))
  logNote('Loaded {locale} locale'.format(locale = l))

db = sql.connect('database.db')
tables = set(db.execute('SELECT name FROM sqlite_master WHERE type=\'table\';').fetchall())

if ('handles',) not in tables:
  db.execute('CREATE TABLE handles(handle CHAR(64), chat_id INT, date INT);')
  logStatus('Created "handles" table')
else:
  logStatus('Found existing "handles" table')
logNote('Table "handles" opened')

if ('users',) not in tables:
  db.execute('CREATE TABLE users(chat_id INT, state TEXT, from_ CHAR(64));')
  logStatus('Created "users" table')
else:
  logStatus('Found existing "users" table')
logNote('Table "users" opened')

while True:
  ans = tgQuery('getUpdates', offset = offset)
  for update in ans['result']:
    process_update(update)
    logNote('Update {update_id} processed'.format(update_id = update['update_id']))
    offset = update['update_id'] + 1