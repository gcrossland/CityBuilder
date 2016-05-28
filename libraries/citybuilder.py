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

class Shape (object):
  def getBoundingBox (self):
    raise NotImplementedError

  def intersects (self, o, boundingBoxIntersection):
    assert isinstance(o, Shape)
    assert boundingBoxIntersection == self.getBoundingBox().getIntersection(o.getBoundingBox())

    if boundingBoxIntersection is None:
      return False
    if isinstance(self, RectangularShape) and isinstance(o, RectangularShape):
      return True
    assert False # TODO

  def contains (self, o, boundingBoxIntersection):
    assert isinstance(o, Shape)
    assert boundingBoxIntersection == self.getBoundingBox().getIntersection(o.getBoundingBox())

    if boundingBoxIntersection is None:
      return False
    if isinstance(self, RectangularShape) and isinstance(o, RectangularShape):
      assert self._box.contains(o.box) == (boundingBoxIntersection == o._box)
      return boundingBoxIntersection == o._box
    assert False # TODO

  def getMembershipGenerator (self, subBox):
    raise NotImplementedError

class RectangularShape (Shape):
  def __init__ (self, x0, z0, x1, z1):
    self._box = Box(x0, z0, x1, z1)

  def getBoundingBox (self):
    return self._box

  def getMembershipGenerator (self, subBox):
    assert isinstance(subBox, Box)
    assert self.box.contains(subBox)
    return itertools.repeat(True, (subBox.x1 - subBox.x0) * (subBox.z1 - subBox.z0))

class ShapeSet (object):
  def __init__ (self):
    self._shapes = []

  def add (self, o)
    assert isinstance(o, Shape)

    self._shapes.append(o)

  # TODO do we need to be able to go from Shapes to their parent Tiles?
  # -> well, we can always monkey on a parent field if we do want to...
  def getIntersectors (self, o):
    assert isinstance(o, Shape)

    oBox = o.getBoundingBox()
    for shape in self._shapes:
      if shape.intersects(o, shape.getBoundingBox().getIntersection(oBox)):
        yield shape

  def intersects (self, o):
    return next(self.getIntersectors(o), None) is not None

WEST = 1 << 1
EAST = 1 << 0
NORTH = 1 << 3
SOUTH = 1 << 2
NORTH_WEST = WEST | NORTH
NORTH_EAST = EAST | NORTH
SOUTH_WEST = WEST | SOUTH
SOUTH_EAST = EAST | SOUTH

class Tile (object):

class RoadTile (Tile):
  def __init__ (self, shape, nextDirection, nextX, nextZ):
    self._shape = shape
    self._nextDirection = nextDirection
    self._nextX = nextX
    self._nextZ = nextZ
    # TODO self._leftPlotTiles? ([] or None) (or maybe just PlotShapes?)
    # TODO self._rightPlotTiles?
    # TODO self._endPlotTiles?

  def getShape (self):
    return self._shape

  def getNextDirection (self):
    return self._nextDirection

  def getNextX (self):
    return self._nextX

  def getNextZ (self):
    return self._nextZ

class StraightRoadTile (RoadTile):
  LEN = 11
  HLEN = (LEN - 1) / 2

  def __init__ (self, direction, x, z):
    assert direction in (WEST, EAST, NORTH, SOUTH)
    assert isinstance(x, int)
    assert isinstance(z, int)

    if direction == WEST:
      nextX = x - LEN
      nextZ = z
      shape = RectangularShape(nextX + 1, z - HLEN, x + 1, z - HLEN + LEN)
    elif direction == EAST:
      nextX = x + LEN
      nextZ = z
      shape = RectangularShape(x, z - HLEN, nextX, z - HLEN + LEN)
    elif direction == NORTH:
      nextX = x
      nextZ = z - LEN
      shape = RectangularShape(x - HLEN, nextZ + 1, x - HLEN + LEN, z + 1)
    elif direction == SOUTH:
      nextX = x
      nextZ = z + LEN
      shape = RectangularShape(x - HLEN, z, x - HLEN + LEN, nextZ)

    RoadTile.__init__(self, shape, direction, nextX, nextZ):
    self._x = x
    self._z = z

class BranchBaseRoadTile (RoadTile):
  def __init__ (self, shape, nextDirection, nextX, nextZ, branchNextDirection, branchNextX, branchNextZ):
    RoadTile.__init__(self, shape, nextDirection, nextX, nextZ)
    self._branchNextDirection = branchNextDirection
    self._branchNextX = branchNextX
    self._branchNextZ = branchNextZ
    self._branchRoadTiles = []
    # TODO self._branchGeneration?

  def getBranchNextDirection (self):
    return self._branchNextDirection

  def getBranchNextX (self):
    return self._branchNextX

  def getBranchNextZ (self):
    return self._branchNextZ

  def getBranchRoadTiles (self):
    return self._branchRoadTiles

class TJunctionRoadTile (BranchBaseRoadTile):
  def __init__ (self, direction, x, z, branchDirection, branchGeneration):
    assert isinstance(x, int)
    assert isinstance(z, int)
    assert (direction in (WEST, EAST) and branchDirection in (NORTH, SOUTH)) or (direction in (NORTH, SOUTH) and branchDirection in (WEST, EAST))

    o = StraightRoadTile(direction, x, z)

    shape = o.getShape()
    assert isinstance(shape, RectangularShape)
    box = shape.getBoundingBox()
    if branchDirection == WEST:
      branchNextX = box.x0 - 1
      branchNextZ = box.z0 + StraightRoadTile.HLEN
    elif branchDirection == EAST:
      branchNextX = box.x1
      branchNextZ = box.z0 + StraightRoadTile.HLEN
    elif branchDirection == NORTH:
      branchNextX = box.x0 + StraightRoadTile.HLEN
      branchNextZ = box.z0 - 1
    elif branchDirection == SOUTH:
      branchNextX = box.x0 + StraightRoadTile.HLEN
      branchNextZ = box.z1
    BranchBaseRoadTile.__init__(self, shape, o.getNextDirection(), o.getNextX(), o.getNextZ(), branchDirection, branchNextX, branchNextZ)
    self._x = o.x
    self._z = o.z

class PlotTile (Tile):
  pass

class City (object):
  def __init__ (self, centreX, centreZ, boundary, boundaryExclusions):
    assert isinstance(centreX, int)
    assert isinstance(centreZ, int)
    assert isinstance(boundary, Shape)
    assert isinstance(boundaryExclusions, ShapeSet)
    # TODO target population, initial target population density

    self._centreX = centreX
    self._centreZ = centreZ
    self._boundary = boundary
    self._boundaryExclusions = boundaryExclusions
    self._roads = ([], [])
    self._tileShapes = ShapeSet()

    for roadTiles, direction, x, z in zip(self._roads, (WEST, EAST), (self._centreX - 1, self._centreX), (self._centreZ, self._centreZ)):
      self._buildMainRoad(roadTiles, direction, x, z)

  def _shapeInBoundary (self, shape):
    if not self._boundary.contains(shape, self._boundary.getBoundingBox().getIntersection(shape.getBoundingBox())):
      return False
    if self._boundaryExclusions.intersects(shape):
      return False
    return True

  def _buildMainRoad (self, roadTiles, direction, x, z):
    while True:
      tile = StraightRoadTile(direction, x, z)
      tileShape = tile.getShape()
      if not self._shapeInBoundary(tileShape)
        break

      roadTiles.append(tile)
      self._tileShapes.add(tileShape)

      direction = tile.getNextDirection()
      x = tile.getNextX()
      z = tile.getNextZ()

  def render (self):
    viewport = self._boundary.getBoundingBox()
    viewportWidth = viewport.x1 - viewport.x0
    vBuffer = array.array('B', itertools.repeat(ord(' '), (viewport.z1 - viewport.z0) * viewportWidth))
    def getI (x, z):
      assert isinstance(x, int)
      assert isinstance(z, int)
      assert x >= viewport.x0
      assert x < viewport.x1
      assert z >= viewport.z0
      assert z < viewport.z1
      return (z - viewport.z0) * viewportWidth + (x - viewport.x0)
    def drawWE (c, x0, z0, l):
      assert isinstance(l, int)
      assert l >= 0
      assert x0 + l <= viewport.x1
      i = getI(x0, z0)
      pel = ord(c)
      for _ in xrange(0, l):
        vBuffer[i] = pel
        i += 1
    def drawNS (c, x0, z0, l):
      assert isinstance(l, int)
      assert l >= 0
      assert z0 + l <= viewport.z1
      i = getI(x0, z0)
      pel = ord(c)
      for _ in xrange(0, l):
        vBuffer[i] = pel
        i += viewportWidth
    def drawBox (c, box):
      drawWE(c, box.x0, box.z0, box.x1 - box.x0)
      drawWE(c, box.x0, box.z1 - 1, box.x1 - box.x0)
      drawNS(c, box.x0, box.z0, box.z1 - box.x0)
      drawNS(c, box.x1 - 1, box.z0, box.z1 - box.x0)

    DIRECTION_STRONGS = {WEST: 'W', EAST: 'E', NORTH: 'N', SOUTH: 'S'}
    DIRECTION_WEAKS = {WEST: 'w', EAST: 'e', NORTH: 'n', SOUTH: 's'}
    def renderRoad (tiles, generation):
      for tile in tiles:
        if isinstance(tile, StraightRoadTile) or isinstance(tile, TJunctionRoadTile):
          assert isinstance(tile.getShape(), RectangularShape) # TODO for now
          box = tile.getShape().getBoundingBox()
          direction = tile.getNextDirection()
          drawBox(DIRECTION_STRONGS[direction], box)
          drawBox(DIRECTION_WEAKS[direction], Box(box.x0 + 1, box.z0 + 1, box.x1 - 1, box.z1 - 1))
          if direction in (WEST, EAST):
            drawWE('-', box.x0 + 2, (box.z0 + box.z1) / 2, box.x1 - box.x0 - 4)
          elif direction in (NORTH, SOUTH):
            drawNS('|', (box.x0 + box.x1) / 2, box.z0 + 2, box.z1 - box.z0 - 4)
          else:
            assert False

          if isinstance(tile, TJunctionRoadTile):
            branchDirection = tile.getBranchNextDirection()
            l = (box.x1 - box.x0 - 4) / 2
            assert l == (box.z1 - box.z0 - 4) / 2
            if branchDirection == WEST:
              drawWE('-', box.x0 + 2, (box.z0 + box.z1) / 2, l)
            elif branchDirection == EAST:
              drawWE('-', (box.x0 + box.x1) / 2 + 1, (box.z0 + box.z1) / 2, l)
            elif branchDirection == NORTH:
              drawNS('|', (box.x0 + box.x1) / 2, box.z0 + 2, l)
            elif branchDirection == SOUTH:
              drawNS('|', (box.x0 + box.x1) / 2, (box.z0 + box.z1) / 2 + 1, l)
            else:
              assert False
            renderRoad(tile.getBranchRoadTiles(), generation + 1)
        else:
          assert False

    for roadTiles in self._roads:
      renderRoad(roadTiles, 0)
    drawWE('X', self._centreX, self._centreZ, 1)
