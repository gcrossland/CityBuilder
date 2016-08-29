from citybuilder import ShapeSet, RectangularShape, City, ConstantRng, LinearRng

D = "03 cities *"

def T (pathName):
  boundaryExclusions = ShapeSet()
  #boundaryExclusions.add(RectangularShape(300, 247, 301, 248))
  #boundaryExclusions.add(RectangularShape(335, 246, 336, 247))
  c = City(230, 230, RectangularShape(0, 0, 600, 500), boundaryExclusions)

  execfile(pathName)

  world = BitmapWorld(c._boundary.getBoundingBox())
  c.place(world)
  for shape in boundaryExclusions._shapes:
    world._d.drawBox('X', shape)
  t("{}", world.getXpm())
