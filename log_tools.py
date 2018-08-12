from datetime import datetime

def logNote(g, str_):
  print('N: [{time}] {str_}'.format(time = datetime.now(), str_ = str_).ljust(g.log_len))
  g.log_len = 0

def logError(g, while_, more = ''):
  print('E: [{time}] While {while_}{more}'.format(time = datetime.now(), while_ = while_, more = '\n' + str(more) if str(more) != '' else '').ljust(g.log_len))
  g.log_len = 0

def logStatus(g, str_):
  res = 'S: [{time}] {str_}'.format(time = datetime.now(), str_ = str_)
  print(res.ljust(g.log_len), end = '\r')
  g.log_len = len(res)
