from citybuilder import ShapeSet, RectangularShape, City, ConstantRng

def T ():
  boundaryExclusions = ShapeSet()
  boundaryExclusions.add(RectangularShape(100, 47, 101, 48))
  boundaryExclusions.add(RectangularShape(135, 46, 136, 47))
  c = City(30, 30, RectangularShape(0, 0, 140, 70), boundaryExclusions)

  c.performGrowthIteration(ConstantRng(0))

  world = BitmapWorld(c._boundary.getBoundingBox())
  c.place(world)
  for shape in boundaryExclusions._shapes:
    world._d.drawBox('X', shape)
  t("{}", "\n".join(world.get()))
