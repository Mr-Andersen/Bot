from hashlib import sha256
from random import Random

random = Random()

def tableInDB(db, table):
  return (table,) in db.execute('SELECT name FROM sqlite_master WHERE type = ?;', ('table',)).fetchall()

def addTable(db, table, str_):
  db.execute('CREATE TABLE {table}({str_});'.format(table = table, str_ = str_))
  db.commit()

def addHandle(db, handle, chat_id, index_):
  db.execute('INSERT INTO handles VALUES (?, ?, ?);', (handle, chat_id, index_))
  db.commit()

def getHandle(db, handle):
  res = db.execute('SELECT * FROM handles WHERE handle = ?;', (handle,)).fetchall()
  if len(res) == 0:
    return None
  res = res[0]
  return { 'handle': res[0],
           'chat_id': res[1],
           'index_': res[2],
           'date': res[2] } # 'date' is sugar

def setHandleIndex(db, handle, index):
  db.execute('UPDATE handles SET index_ = ? WHERE handle = ?', (index, handle))
  db.commit()

def userHandles(db, chat_id):
  res = sorted(db.execute('SELECT * FROM handles WHERE chat_id = ?;', (chat_id,)).fetchall(), key = lambda item: item[2])
  for i in range(len(res)):
    res[i] = { 'handle': res[i][0],
               'chat_id': res[i][1],
               'index_': res[i][2] }
  return res

def disabledHandles(db):
  res = db.execute('SELECT * FROM handles WHERE chat_id = NULL;').fetchall()
  return res

def disableHandle(db, handle, date):
  db.execute('UPDATE handles SET chat_id = NULL, index_ = ? WHERE handle = ?;', (date, handle))
  db.commit()

def eraseHandle(db, handle):
  db.execute('DELETE FROM handles WHERE handle = ?;', (handle,))
  db.commit()

def addUser(db, chat_id):
  salt = random.randint(0, 1048576)
  hashed_chat_id = sha256(bytes(str(chat_id + salt), 'utf-8')).digest()
  db.execute('INSERT INTO users VALUES (?, ?, NULL, NULL, NULL);', (hashed_chat_id, salt))
  db.commit()

def getUser(db, chat_id):
  for row in db.execute('SELECT * FROM users;'):
    hashed_chat_id = sha256(bytes(str(chat_id + row[1]), 'utf-8')).digest()
    salt = row[1]
    if sha256(bytes(str(chat_id + row[1]), 'utf-8')).digest() == row[0]:
      return { 'chat_id': chat_id,
               'hashed_chat_id': row[0],
               'salt': row[1],
               'state': row[2],
               'from_': row[3],
               'buffer_': row[4] }
  return None

def setUserFrom(db, hashed_chat_id, from_):
  db.execute('UPDATE users SET from_ = ? WHERE hashed_chat_id = ?', (from_, hashed_chat_id))
  db.commit()

def setUserState(db, hashed_chat_id, state):
  db.execute('UPDATE users SET state = ? WHERE hashed_chat_id = ?;', (state, hashed_chat_id))
  db.commit()

def setUserBuffer(db, hashed_chat_id, buffer_):
  db.execute('UPDATE users SET buffer_ = ? WHERE hashed_chat_id = ?', (buffer_, hashed_chat_id))
  db.commit()
