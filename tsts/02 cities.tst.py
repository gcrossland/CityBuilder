from citybuilder import ConstantRng, RectangularShape, City, BitmapWorld

D = "02 cities *"

def T (pathName):
  r = ConstantRng(0).choice
  boundaryExclusions = set()
  endpoints = []
  execfile(pathName)
  c = City(200, 200, RectangularShape(0, 0, 600, 500), boundaryExclusions, endpoints, r)

  c.extendPlottage(3)

  world = BitmapWorld(c._tileShapeSet._boundary)
  c.place(world)
  for shape in boundaryExclusions:
    world._d.drawBox('X', shape)
  t("{}", world.getXpm())
