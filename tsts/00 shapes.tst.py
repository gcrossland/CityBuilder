from citybuilder import RectangularShape, ArbitraryShape, Display

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
  t("{}\n\n", "\n".join(d.get()))

  viewport = RectangularShape(-12, -8, 12, 8)
  x0 = -10
  z0 = -6

  def getIntersectionTable (ss):
    d = Display(RectangularShape(-1, -1, len(ss), len(ss)))
    for i in xrange(0, len(ss)):
      d.drawPel(str(i), i, -1)
      d.drawPel(str(i), -1, i)
    for x in xrange(0, len(ss)):
      for z in xrange(0, len(ss)):
        d.drawPel((' ', '*')[ss[x].intersects(ss[z])], x, z)
    return "\n".join(d.get())

  sA0 = RectangularShape(x0, z0, x0 + 5, z0 + 4)
  sA1 = sA0.getTranslation(0, 4)
  sA2 = sA1.getTranslation(0, 4 - 1)
  sA3 = sA0.getTranslation(5 - 1, 0)
  sA4 = sA3.getTranslation(5, 0)
  sA5 = sA0.getTranslation(5, 4)
  sA6 = sA0.getTranslation(5 - 1, 4 - 1)
  sA7 = RectangularShape(x0 - 1, z0 + 5, x0 - 1 + 7, z0 + 5 + 3)
  sAs = (sA0, sA1, sA2, sA3, sA4, sA5, sA6, sA7)
  for i in xrange(0, len(sAs)):
    d = Display(viewport)
    d.drawBox('X', viewport)
    for j in xrange(0, i):
      d.drawShape('-', sAs[j])
    d.drawShape('#', sAs[i])
    t("cumulative to sA{}:\n{}", i, "\n".join(d.get()))
  t("{}\n\n", getIntersectionTable(sAs))

  def drawShape (s):
    d = Display(viewport)
    d.drawShape('#', s)
    return "\n".join(d.get())

  t0 = ArbitraryShape.Template((0b11111, 0b11111, 0b11111, 0b11111))
  sB0 = ArbitraryShape(t0, x0, z0)
  sB1 = sB0.getTranslation(0, 4)
  sB2 = sB1.getTranslation(0, 4 - 1)
  sB3 = sB0.getTranslation(5 - 1, 0)
  sB4 = sB3.getTranslation(5, 0)
  sB5 = sB0.getTranslation(5, 4)
  sB6 = sB0.getTranslation(5 - 1, 4 - 1)
  t1 = ArbitraryShape.Template((0b1111111, 0b1111111, 0b1111111))
  sB7 = ArbitraryShape(t1, x0 - 1, z0 + 5)
  sBs = (sB0, sB1, sB2, sB3, sB4, sB5, sB6, sB7)
  for i in xrange(0, len(sBs)):
    t("sA{} is sB{} = {}", i, i, drawShape(sAs[i]) == drawShape(sBs[i]))
  t("getIntersectionTable(sAs) is getIntersectionTable(sBs) = {}", getIntersectionTable(sAs) == getIntersectionTable(sBs))

  t2 = ArbitraryShape.Template([0] * 2 + [0b11111 << 4, 0b11111 << 4, 0b11111 << 4, 0b11111 << 4] + [0] * 1, 12)
  sC0 = ArbitraryShape(t2, x0 - 4, z0 - 2)
  sC1 = sC0.getTranslation(0, 4)
  sC2 = sC1.getTranslation(0, 4 - 1)
  sC3 = sC0.getTranslation(5 - 1, 0)
  sC4 = sC3.getTranslation(5, 0)
  sC5 = sC0.getTranslation(5, 4)
  sC6 = sC0.getTranslation(5 - 1, 4 - 1)
  t3 = ArbitraryShape.Template([0b0] * 15 + [0b1111111 << 15, 0b1111111 << 15, 0b1111111 << 15] + [0b0] * 15, 37)
  sC7 = ArbitraryShape(t3, x0 - 1 - 15, z0 + 5 - 15)
  sCs = (sC0, sC1, sC2, sC3, sC4, sC5, sC6, sC7)
  for i in xrange(0, len(sCs)):
    t("sA{} is sC{} = {}", i, i, drawShape(sAs[i]) == drawShape(sCs[i]))
  t("getIntersectionTable(sAs) is getIntersectionTable(sCs) = {}", getIntersectionTable(sAs) == getIntersectionTable(sCs))

  sss = (sAs, sCs)
  sAsT = getIntersectionTable(sAs)
  for perm in xrange(0, 2 ** len(sAs)):
    ss = [sss[(perm >> i) & 0b1][i] for i in xrange(0, len(sAs))]
    if not all(ss):
      continue
    t("perm {} - getIntersectionTable(sAs) is getIntersectionTable(s?s) = {}", bin(perm), sAsT == getIntersectionTable(ss))

  x0 += 2
  z0 += 2

  t4 = ArbitraryShape.Template(ArbitraryShape.Template.rows(
    "***  ",
    "*  * ",
    "*   *",
    "*    ",
    "*   *",
    "*    ",
    "* *  "
  ))
  sD0 = ArbitraryShape(t4, x0, z0)
  t5 = t4.getClockwiseQuarterRotation()
  sD1 = ArbitraryShape(t5, x0, z0)
  t6 = t5.getClockwiseQuarterRotation()
  sD2 = ArbitraryShape(t6, x0, z0)
  t7 = t6.getClockwiseQuarterRotation()
  sD3 = ArbitraryShape(t7, x0, z0)
  sD4 = ArbitraryShape(t7.getClockwiseQuarterRotation(), x0, z0)
  sD5 = ArbitraryShape(t4.getReflectionAroundXAxis(), x0, z0)
  sD6 = ArbitraryShape(t4.getReflectionAroundZAxis(), x0, z0)
  sDs = (sD0, sD1, sD2, sD3, sD4, sD5, sD6)
  for i in xrange(0, len(sDs)):
    d = Display(viewport)
    d.drawBox('X', viewport)
    d.drawShape('.', sDs[i].getBoundingBox())
    d.drawShape('#', sDs[i])
    t("sD{} (with bounding box):\n{}", i, "\n".join(d.get()))
  t("{}\n\n", getIntersectionTable(sDs))

  sE0 = sD0
  sE1 = ArbitraryShape(t5, x0 + 4, z0 + 3)
  sE2 = ArbitraryShape(t6, x0 + 4 - 1, z0 + 3 + 1)
  sE3 = ArbitraryShape(t7, x0 + 4 - 1 - 6, z0 + 3 + 1 + 1)
  sEs = (sE0, sE1, sE2, sE3)
  d = Display(viewport)
  d.drawBox('X', viewport)
  for i in xrange(0, len(sEs)):
    d.drawShape(str(i), sEs[i])
  t("sEs{}:\n{}", i, "\n".join(d.get()))
  t("{}\n\n", getIntersectionTable(sEs))

  t8 = ArbitraryShape.Template(ArbitraryShape.Template.rows(*(("* " * 4, " *" * 4)) * 4))
  sF0 = ArbitraryShape(t8, x0, z0)
  sF1 = ArbitraryShape(t8.getClockwiseQuarterRotation(), x0, z0)
  sFs = (sF0, sF1)
  for i in xrange(0, len(sFs)):
    d = Display(viewport)
    d.drawBox('X', viewport)
    d.drawShape('.', sFs[i].getBoundingBox())
    d.drawShape('#', sFs[i])
    t("sF{} (with bounding box):\n{}", i, "\n".join(d.get()))
  t("{}\n\n", getIntersectionTable(sFs))
