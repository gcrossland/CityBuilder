from citybuilder import RectangularShape, Display

def T ():
  d = Display(RectangularShape(0, 0, 70, 70))
  d.drawBox('*', RectangularShape(1, 1, 70 - 1, 70 - 1))
  d.drawBox('p', RectangularShape(1, 2, 70 - 3, 70 - 4))
  d.drawBox('q', RectangularShape(14, 13, 70 - 12, 70 - 11))
  d.drawBox('r', RectangularShape(20, 20, 23, 23))
  d.drawBox('s', RectangularShape(30, 30, 32, 32))
  d.drawBox('t', RectangularShape(40, 40, 41, 41))
  # TODO single arg t() that just prints the value?
  # TODO include e.g. tsts/libraries in the pythonpath?
  # TODO do cmp iff tsts.good exists?
  t("{}", "\n".join(d.get()))
