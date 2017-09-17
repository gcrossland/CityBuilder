#!/usr/bin/env python2
import math
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

def getCirclePoint (angle, radius):
  assert angle <= 180 and angle >= -180 # 0 south, 90 west, -90 east
  v0 = float(radius) / (1 + math.tan(math.radians(angle)) ** 2) ** 0.5
  v1 = (radius ** 2 - v0 ** 2) ** 0.5
  if angle >= 90:
    return (-v1, -v0)
  elif angle >= 0:
    return (-v1, v0)
  elif angle >= -90:
    return (v1, v0)
  else:
    return (v1, -v0)

for rng, rngName in ((ConstantRng(0).choice, "ConstantRng"), (LinearRng().choice, "LinearRng"), (random.Random(42).choice, "Random")):
  for angle in xrange(-180, 180, 1):
    variant = "angle-" + rngName

    rx, rz = getCirclePoint(angle, 1000)

    branchisableChoices = (0,)

    boundaryExclusions = set()
    endpoints = ((1200 / 2 + int(rx), 1000 / 2 + int(rz)),)
    c = City(1200 / 2, 1000 / 2, RectangularShape(0, 0, 1200, 1000), boundaryExclusions, endpoints, rng, branchisableChoices)
    save(c, variant)
