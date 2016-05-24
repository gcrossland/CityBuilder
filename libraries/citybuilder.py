import sys
import itertools
import array



# x, z coords
# width, height always positive (i.e. box is from north-west to south-east)
# inclusive on north-west sides; exclusive on south-east sides
class Box (object):
  def __init__ (self, x0, z0, x1, z1):
    assert isinstance(x0, int)
    assert isinstance(z0, int)
    assert isinstance(x1, int)
    assert isinstance(z1, int)
    assert x1 > x0
    assert z1 > z0
    self.x0 = x0
    self.z0 = z0
    self.x1 = x1
    self.z1 = z1

  def __eq__ (self, o):
    if not isinstance(o, Box):
      return NotImplemented
    return self.x0 == o.x0 and self.z0 == o.z0 and self.x1 == o.x1 and self.z1 == o.z1

  # XXXX
  #def __hash__ (self):
  #  return self.x0 ^ (self.z0 << 8) ^ (self.x1 << 16) ^ (self.z1 << 24)

  def getIntersection (self, o):
    assert isinstance(o, Box)
    x0 = max(self.x0, o.x0)
    x1 = min(self.x1, o.x1)
    if x0 >= x1:
      return None
    z0 = max(self.z0, o.z0)
    z1 = min(self.z1, o.z1)
    if z0 >= z1:
      return None
    return Box(x0, z0, x1, z1)

  def intersects (self, o):
    return self.getIntersection(o) is not None

  def contains (self, o):
    assert isinstance(o, Box)
    return self.x0 <= o.x0 and self.z0 <= o.z0 and self.x1 >= o.x1 and self.z1 >= o.z1
