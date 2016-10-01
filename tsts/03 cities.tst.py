from citybuilder import ConstantRng, ShapeSet, RectangularShape, City, BitmapWorld

D = "03 cities *"

def T (pathName):
  boundaryExclusions = ShapeSet()
  #boundaryExclusions.add(RectangularShape(300, 247, 301, 248))
  #boundaryExclusions.add(RectangularShape(335, 246, 336, 247))
  endpoints = [(0, 200), (200 + 3300, 200 + 200)]
  c = City(199, 200, RectangularShape(0, 0, 600, 500), boundaryExclusions, endpoints, ConstantRng(0).choice)

  execfile(pathName)
  c.extendPlottage(3)

  world = BitmapWorld(c._boundary.getBoundingBox())
  c.place(world)
  for shape in boundaryExclusions:
    world._d.drawBox('X', shape)
  t("{}", world.getXpm())
