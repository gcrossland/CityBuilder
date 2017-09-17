#!/usr/bin/env python2
import random
from citybuilder import RectangularShape, City, BitmapWorld, Reldirection, ConstantRng, LinearRng

frames = {}
def save (c, variant, frame = None):
  #c.extendPlottage(3)

  world = BitmapWorld(c._tileShapeSet._boundary)
  c.place(world)
  for shape in boundaryExclusions:
    world._d.drawBox(ord('X'), shape)

  if frame is None:
    frame = frames.get(variant, 0)
  with open(variant + "-" + str(frame).zfill(3) + ".xpm", "wb") as f:
    f.write(world.getXpm())
    f.write("\n")
  frames[variant] = frame + 1

  #c.resetPlottage()

def appendRectangularShape (l, x0, z0, x1, z1):
  if not (x1 > x0 and z1 > z0):
    return
  l.append(RectangularShape(x0, z0, x1, z1))

def invertRectangularShape (shape, bound):
  assert isinstance(shape, RectangularShape)
  assert isinstance(bound, RectangularShape)
  assert bound.contains(shape)
  shapes = []
  appendRectangularShape(shapes, bound.x0, bound.z0, shape.x0, bound.z1)
  appendRectangularShape(shapes, shape.x1, bound.z0, bound.x1, bound.z1)
  appendRectangularShape(shapes, shape.x0, bound.z0, shape.x1, shape.z0)
  appendRectangularShape(shapes, shape.x0, shape.z1, shape.x1, bound.z1)
  return shapes

for cityPixelMinorRadius in xrange(200, 800 + 1, 100):
  variant = "radius" + str(cityPixelMinorRadius)

  rng = LinearRng().choice
  #rng = random.Random(42).choice
  branchisableChoices = (0.05,)

  worldBoundary = RectangularShape(0, 0, 2400, 2000)
  cityBoundary = RectangularShape(800 - cityPixelMinorRadius, 800 - cityPixelMinorRadius, 800 + cityPixelMinorRadius * 2, 800 + int(cityPixelMinorRadius * 1.5))
  riverBoundary = [
    RectangularShape(i, 720 + i / 5, i + 100, 780 + i / 5) for i in range(0, 700, 100) + range(800, 1000, 100)
  ] + [
    RectangularShape(i, 720 + 342 + - i / 7, i + 100, 780 + 342 - i / 7) for i in range(1000, 2400, 100)
  ]

  boundaryExclusions = set()
  boundaryExclusions.update(invertRectangularShape(cityBoundary, worldBoundary))
  boundaryExclusions.update(riverBoundary)
  endpoints = [(800 + x, 800 + z) for x, z in ((100, -2000), (-1902, -618), (1902, -618), (-1176, 1618), (1176, 1618))]
  c = City(800, 800, worldBoundary, boundaryExclusions, endpoints, rng, branchisableChoices)
  save(c, variant)

  cityRadius = cityPixelMinorRadius / 10

  c.addBranches(0, True, c.getCirclingTargetRangFactory(), rng, (1.5 / cityRadius,), (99999,), branchisableChoices)
  save(c, variant)

  generationSpecs = []
  scale = 1
  while True:
    branchChoice = 0.10625 / scale
    lengthChoices = xrange(int(1 / branchChoice), int(5 / branchChoice))
    branchisableChoice = branchChoice
    generationSpecs.append(((branchChoice,), lengthChoices, (branchisableChoice,)))
    if branchChoice <= 3 * 1.5 / cityRadius:
      break
    scale *= 1.25
  for branchChoices, lengthChoices, branchisableChoices in reversed(generationSpecs):
    c.addBranches(-1, True, c.getConstantTargetRangFactory(), rng, branchChoices, lengthChoices, branchisableChoices)
    save(c, variant)

  save(c, variant, 999)
