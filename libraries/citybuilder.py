# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#  City Building Library
#  © Geoff Crossland 2016
# ------------------------------------------------------------------------------
import sys
import itertools
import array

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
class Shape (object):
  def getBoundingBox (self):
    raise NotImplementedError

  def intersects (self, o, boundingBoxIntersection):
    assert isinstance(o, Shape)
    assert RectangularShape.eqs(boundingBoxIntersection, self.getBoundingBox().getIntersection(o.getBoundingBox()))

    if boundingBoxIntersection is None:
      return False
    if isinstance(self, RectangularShape) and isinstance(o, RectangularShape):
      return True
    assert False # TODO

  def contains (self, o, boundingBoxIntersection):
    assert isinstance(o, Shape)
    assert RectangularShape.eqs(boundingBoxIntersection, self.getBoundingBox().getIntersection(o.getBoundingBox()))

    if boundingBoxIntersection is None:
      return False
    if isinstance(self, RectangularShape) and isinstance(o, RectangularShape):
      return boundingBoxIntersection.eq(o)
    assert False # TODO

  def getMembershipGenerator (self, subBox):
    assert isinstance(subBox, RectangularShape)
    raise NotImplementedError

class RectangularShape (Shape):
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

  def eq (self, o):
    assert isinstance(o, RectangularShape)
    return self.x0 == o.x0 and self.z0 == o.z0 and self.x1 == o.x1 and self.z1 == o.z1

  @staticmethod
  def eqs (o0, o1):
    if o0 is None:
      return o1 is None
    if o1 is None:
      return False
    return o0.eq(o1)

  def getIntersection (self, o):
    assert isinstance(o, RectangularShape)
    x0 = max(self.x0, o.x0)
    x1 = min(self.x1, o.x1)
    if x0 >= x1:
      return None
    z0 = max(self.z0, o.z0)
    z1 = min(self.z1, o.z1)
    if z0 >= z1:
      return None
    return RectangularShape(x0, z0, x1, z1)

  def getBoundingBox (self):
    return self

  def getMembershipGenerator (self, subBox):
    assert isinstance(subBox, RectangularShape)
    assert self.contains(subBox, self.getIntersection(subBox))
    return itertools.repeat(True, (subBox.x1 - subBox.x0) * (subBox.z1 - subBox.z0))

class ShapeSet (object):
  def __init__ (self):
    self._shapes = []

  def add (self, o):
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

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
class World (object):
  def placeStraightRoadTile (self, shape, direction):
    raise NotImplementedError

  def placeTJunctionRoadTile (self, shape, direction, branchDirection):
    raise NotImplementedError

  def placeMarker (self, x, z):
    raise NotImplementedError

WEST = 1 << 1
EAST = 1 << 0
NORTH = 1 << 3
SOUTH = 1 << 2
NORTH_WEST = WEST | NORTH
NORTH_EAST = EAST | NORTH
SOUTH_WEST = WEST | SOUTH
SOUTH_EAST = EAST | SOUTH

class Tile (object):
  def place (self, world):
    raise NotImplementedError

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
      nextX = x - StraightRoadTile.LEN
      nextZ = z
      shape = RectangularShape(nextX + 1, z - StraightRoadTile.HLEN, x + 1, z - StraightRoadTile.HLEN + StraightRoadTile.LEN)
    elif direction == EAST:
      nextX = x + StraightRoadTile.LEN
      nextZ = z
      shape = RectangularShape(x, z - StraightRoadTile.HLEN, nextX, z - StraightRoadTile.HLEN + StraightRoadTile.LEN)
    elif direction == NORTH:
      nextX = x
      nextZ = z - StraightRoadTile.LEN
      shape = RectangularShape(x - StraightRoadTile.HLEN, nextZ + 1, x - StraightRoadTile.HLEN + StraightRoadTile.LEN, z + 1)
    elif direction == SOUTH:
      nextX = x
      nextZ = z + StraightRoadTile.LEN
      shape = RectangularShape(x - StraightRoadTile.HLEN, z, x - StraightRoadTile.HLEN + StraightRoadTile.LEN, nextZ)

    RoadTile.__init__(self, shape, direction, nextX, nextZ)
    self._x = x
    self._z = z

  def place (self, world):
    world.placeStraightRoadTile(self.getShape(), self.getNextDirection())

class BranchBaseRoadTile (RoadTile):
  def __init__ (self, shape, nextDirection, nextX, nextZ, branchDirection, branchX, branchZ):
    RoadTile.__init__(self, shape, nextDirection, nextX, nextZ)
    self._branchDirection = branchDirection
    self._branchX = branchX
    self._branchZ = branchZ
    self._branchRoadTiles = []
    # TODO self._branchGeneration?

  def getBranchDirection (self):
    return self._branchDirection

  def getBranchX (self):
    return self._branchX

  def getBranchZ (self):
    return self._branchZ

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
    box = shape
    if branchDirection == WEST:
      branchX = box.x0 - 1
      branchZ = box.z0 + StraightRoadTile.HLEN
    elif branchDirection == EAST:
      branchX = box.x1
      branchZ = box.z0 + StraightRoadTile.HLEN
    elif branchDirection == NORTH:
      branchX = box.x0 + StraightRoadTile.HLEN
      branchZ = box.z0 - 1
    elif branchDirection == SOUTH:
      branchX = box.x0 + StraightRoadTile.HLEN
      branchZ = box.z1
    BranchBaseRoadTile.__init__(self, shape, o.getNextDirection(), o.getNextX(), o.getNextZ(), branchDirection, branchX, branchZ)
    self._x = o._x
    self._z = o._z

  def place (self, world):
    world.placeTJunctionRoadTile(self.getShape(), self.getNextDirection(), self.getBranchDirection())
    for tile in self.getBranchRoadTiles():
      tile.place(world)

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
      if not self._shapeInBoundary(tileShape):
        break

      roadTiles.append(tile)
      self._tileShapes.add(tileShape)

      direction = tile.getNextDirection()
      x = tile.getNextX()
      z = tile.getNextZ()

  def place (self, world):
    for roadTiles in self._roads:
      for roadTile in roadTiles:
        roadTile.place(world)
      world.placeMarker(self._centreX, self._centreZ)

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
class Display (object):
  def __init__ (self, viewport):
    assert isinstance(viewport, RectangularShape)
    self._viewport = viewport
    self._viewportWidth = viewport.x1 - viewport.x0
    self._vBuffer = array.array('B', itertools.repeat(ord(' '), (viewport.z1 - viewport.z0) * self._viewportWidth))

  def _getI (self, x, z):
    assert isinstance(x, int)
    assert isinstance(z, int)
    viewport = self._viewport
    assert x >= viewport.x0
    assert x < viewport.x1
    assert z >= viewport.z0
    assert z < viewport.z1
    return (z - viewport.z0) * self._viewportWidth + (x - viewport.x0)

  def drawWE (self, c, x0, z0, l):
    assert isinstance(l, int)
    assert l >= 0
    assert x0 + l <= self._viewport.x1
    i = self._getI(x0, z0)
    pel = ord(c)
    vBuffer = self._vBuffer
    for _ in xrange(0, l):
      vBuffer[i] = pel
      i += 1

  def drawNS (self, c, x0, z0, l):
    assert isinstance(l, int)
    assert l >= 0
    assert z0 + l <= self._viewport.z1
    i = self._getI(x0, z0)
    pel = ord(c)
    vBuffer = self._vBuffer
    viewportWidth = self._viewportWidth
    for _ in xrange(0, l):
      vBuffer[i] = pel
      i += viewportWidth

  def drawBox (self, c, box):
    assert isinstance(box, RectangularShape)
    dX = box.x1 - box.x0
    self.drawWE(c, box.x0, box.z0, dX)
    self.drawWE(c, box.x0, box.z1 - 1, dX)
    dZ = box.z1 - box.z0 - 2
    if dZ > 0:
      z = box.z0 + 1
      self.drawNS(c, box.x0, z, dZ)
      self.drawNS(c, box.x1 - 1, z, dZ)

  def get (self):
    viewport = self._viewport
    viewportWidth = self._viewportWidth
    vBuffer = self._vBuffer
    return [vBuffer[i:i + viewportWidth].tostring() for i in xrange(0, (viewport.z1 - viewport.z0) * viewportWidth, viewportWidth)]

class BitmapWorld (World):
  def __init__ (self, boundingBox):
    self._d = Display(boundingBox)

  DIRECTION_STRONGS = {WEST: 'W', EAST: 'E', NORTH: 'N', SOUTH: 'S'}
  DIRECTION_WEAKS = {WEST: 'w', EAST: 'e', NORTH: 'n', SOUTH: 's'}

  def placeStraightRoadTile (self, shape, direction):
    assert isinstance(shape, RectangularShape) # TODO for now
    box = shape

    self._d.drawBox(BitmapWorld.DIRECTION_STRONGS[direction], box)
    self._d.drawBox(BitmapWorld.DIRECTION_WEAKS[direction], RectangularShape(box.x0 + 1, box.z0 + 1, box.x1 - 1, box.z1 - 1))
    if direction in (WEST, EAST):
      self._d.drawWE('-', box.x0 + 2, (box.z0 + box.z1) / 2, box.x1 - box.x0 - 4)
    elif direction in (NORTH, SOUTH):
      self._d.drawNS('|', (box.x0 + box.x1) / 2, box.z0 + 2, box.z1 - box.z0 - 4)
    else:
      assert False

  def placeTJunctionRoadTile (self, shape, direction, branchDirection):
    box = shape

    self.placeStraightRoadTile(shape, direction)

    l = (box.x1 - box.x0 - 4) / 2
    assert l == (box.z1 - box.z0 - 4) / 2
    if branchDirection == WEST:
      self._d.drawWE('-', box.x0 + 2, (box.z0 + box.z1) / 2, l)
    elif branchDirection == EAST:
      self._d.drawWE('-', (box.x0 + box.x1) / 2 + 1, (box.z0 + box.z1) / 2, l)
    elif branchDirection == NORTH:
      self._d.drawNS('|', (box.x0 + box.x1) / 2, box.z0 + 2, l)
    elif branchDirection == SOUTH:
      self._d.drawNS('|', (box.x0 + box.x1) / 2, (box.z0 + box.z1) / 2 + 1, l)
    else:
      assert False

  def placeMarker (self, x, z):
    self._d.drawWE('X', x, z, 1)

  def get (self):
    return self._d.get()
