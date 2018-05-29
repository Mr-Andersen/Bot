def logNote(g, str_):
  print('N: {str_}'.format(str_ = str_).ljust(g.log_len))
  g.log_len = 0

def logError(g, while_, more = ''):
  print('E: While {while_}{more}'.format(while_ = while_, more = '\n' + str(more) if str(more) != '' else '').ljust(g.log_len))
  g.log_len = 0

def logStatus(g, str_):
  print('S:', str_.ljust(g.log_len), end = '\r')
  g.log_len = len(str_) + len('S: ')
