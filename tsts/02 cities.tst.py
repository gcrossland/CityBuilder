from citybuilder import ShapeSet, RectangularShape, City

def T ():
  boundaryExclusions = ShapeSet()
  c = City(25, 25, RectangularShape(0, 0, 140, 70), boundaryExclusions)

  world = BitmapWorld(c._boundary.getBoundingBox())
  c.place(world)
  t("{}", "\n".join(world.get()))
