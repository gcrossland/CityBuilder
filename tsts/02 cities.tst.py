from citybuilder import ShapeSet, RectangularShape, City, ConstantRng

def T ():
  boundaryExclusions = ShapeSet()
  boundaryExclusions.add(RectangularShape(100, 47, 101, 48))
  boundaryExclusions.add(RectangularShape(135, 46, 136, 47))
  c = City(30, 30, RectangularShape(0, 0, 140, 70), boundaryExclusions)

  r = ConstantRng(0)
  c.performGrowthIteration(r)
  c.extendPlotage(r)

  world = BitmapWorld(c._boundary.getBoundingBox())
  c.place(world)
  for shape in boundaryExclusions:
    world._d.drawBox('X', shape)
  t("{}", world.getXpm())
