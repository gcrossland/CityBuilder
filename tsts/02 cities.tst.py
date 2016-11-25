from citybuilder import ConstantRng, RectangularShape, City, BitmapWorld

D = "02 cities *"

def T (pathName):
  r = ConstantRng(0).choice
  boundaryExclusions = set()
  endpoints = []
  execfile(pathName)
  c = City(200, 200, RectangularShape(0, 0, 600, 500), boundaryExclusions, endpoints, r, (0.2,))

  c.extendPlottage(7)

  world = BitmapWorld(c._tileShapeSet._boundary)
  c.place(world)
  for shape in boundaryExclusions:
    world._d.drawBox(ord('X'), shape)
  b = c._tileShapeSet._boundary
  def pt (x, z):
    if x >= b.x0 and x < b.x1 and z >= b.z0 and z < b.z1:
      world.placeMarker(x, z)
  for x, z in endpoints:
    pt(x - 1, z - 1)
    pt(x,     z - 1)
    pt(x + 1, z - 1)
    pt(x - 1, z)
    pt(x + 1, z)
    pt(x - 1, z + 1)
    pt(x,     z + 1)
    pt(x + 1, z + 1)
    pt(x - 2, z - 2)
    pt(x + 2, z - 2)
    pt(x - 2, z + 2)
    pt(x + 2, z + 2)
  t("{}", world.getXpm())
