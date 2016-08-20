from citybuilder import Box, Display

def T ():
  d = Display(Box(0, 0, 70, 70))
  d.drawBox('*', Box(1, 1, 70 - 1, 70 - 1))
  d.drawBox('p', Box(1, 2, 70 - 3, 70 - 4))
  d.drawBox('q', Box(14, 13, 70 - 12, 70 - 11))
  d.drawBox('r', Box(20, 20, 23, 23))
  d.drawBox('s', Box(30, 30, 32, 32))
  d.drawBox('t', Box(40, 40, 41, 41))
  # TODO single arg t() that just prints the value?
  # TODO include e.g. tsts/libraries in the pythonpath?
  # TODO do cmp iff tsts.good exists?
  t("{}", "\n".join(d.get()))
