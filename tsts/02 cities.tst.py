from citybuilder import ConstantRng, ShapeSet, RectangularShape, City, BitmapWorld

D = "02 cities *"

def T (pathName):
  r = ConstantRng(0).choice
  boundaryExclusions = ShapeSet()
  endpoints = []
  execfile(pathName)
  c = City(200, 200, RectangularShape(0, 0, 600, 500), boundaryExclusions, endpoints, r)

  c.extendPlotage(r, 8)

  world = BitmapWorld(c._boundary.getBoundingBox())
  c.place(world)
  for shape in boundaryExclusions:
    world._d.drawBox('X', shape)
  t("{}", world.getXpm())
