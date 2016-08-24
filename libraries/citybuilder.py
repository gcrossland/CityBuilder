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

  def transform (self, dX, dZ):
    return Box(self.x0 + dX, self.z0 + dZ, self.x1 + dX, self.z1 + dZ)

  def getBoundingBox (self):
    return self

  def getMembershipGenerator (self, subBox):
    assert isinstance(subBox, RectangularShape)
    assert self.contains(subBox, self.getIntersection(subBox))
    return itertools.repeat(True, (subBox.x1 - subBox.x0) * (subBox.z1 - subBox.z0))

class ShapeSet (object):
  def __init__ (self):
    self._shapes = set()

  def add (self, o):
    assert isinstance(o, Shape)

    self._shapes.add(o)

  def addIfNotIntersecting (self, o):
    if self.intersects(o):
      return False
    else:
      self.add(o)
      return True

  def remove (self, o):
    self._shapes.remove(o)

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

LEFT = 0
RIGHT = 1
RELDIRECTIONS_TO_DIRECTIONS = {WEST: (SOUTH, NORTH), EAST: (NORTH, SOUTH), NORTH: (WEST, EAST), SOUTH: (EAST, WEST)}

class Tile (object):
  def place (self, world):
    raise NotImplementedError

class RoadTile (Tile):
  def __init__ (self, direction, x, z, shape, nextX, nextZ):
    self._direction = direction
    self._x = x
    self._z = z
    self._shape = shape
    self._nextX = nextX
    self._nextZ = nextZ
    self._leftPlotShapes = []
    self._rightPlotShapes = []
    # TODO self._endPlotTiles?

  def getDirection (self):
    return self._direction

  def getX (self):
    return self._x

  def getZ (self):
    return self._z

  def getShape (self):
    return self._shape

  def getNextDirection (self):
    raise NotImplementedError

  def getNextX (self):
    return self._nextX

  def getNextZ (self):
    return self._nextZ

  def _getNextPlotShape (self, shapes, reldirection):
    raise NotImplementedError

  def _addNextPlotShape (self, shapes, reldirection, shapeSet):
    assert shapes in (self._leftPlotShapes, self._rightPlotShapes)
    assert reldirection in (LEFT, RIGHT)

    shape = self._getNextPlotShape(shapes, reldirection)
    if shape is None:
      assert shapes[-1] is None
      return None

    if not shapeSet.addIfNotIntersecting(shape):
      shape = None
    shapes.append(shape)
    return shape

  def _addMinimalPlotShapes (self, minCount, shapeSet):
    l = self._addNextPlotShape(self._leftPlotShapes, LEFT, shapeSet)
    r = self._addNextPlotShape(self._rightPlotShapes, RIGHT, shapeSet)
    if (l is not None) + (r is not None) < minCount:
      for shape in (l, r):
        if shape is not None:
          shapeSet.remove(shape)
      return False
    return True

  def addNextPlotShapes (self, shapeSet):
    l = self._addNextPlotShape(self._leftPlotShapes, LEFT, shapeSet)
    r = self._addNextPlotShape(self._rightPlotShapes, RIGHT, shapeSet)
    return l is not None or r is not None

  def _reminimalisePlotShapes (self, shapes):
    assert shapes in (self._leftPlotShapes, self._rightPlotShapes)

    if len(shapes) != 0:
      del shapes[1:]
      if shapes[0] is None:
        del shapes[0]

  def reminimalisePlotShapes (self):
    self._reminimalisePlotShapes(self._leftPlotShapes)
    self._reminimalisePlotShapes(self._rightPlotShapes)

  def getPlotShapes (self):
    return [shape for shape in itertools.chain(self._leftPlotShapes, self._rightPlotShapes) if shape is not None]

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

    RoadTile.__init__(self, direction, x, z, shape, nextX, nextZ)

  def getNextDirection (self):
    return self.getDirection()

  def _getNextPlotShape (self, shapes, reldirection):
    if len(shapes) == 0:
      parentShape = self.getShape()
    else:
      parentShape = shapes[-1]
      if parentShape is None:
        return None
    assert isinstance(parentShape, RectangularShape)

    plotDirection = RELDIRECTIONS_TO_DIRECTIONS[self.getDirection()][reldirection]
    if plotDirection == WEST:
      dX = -StraightRoadTile.LEN
      dZ = 0
    elif plotDirection == EAST:
      dX = StraightRoadTile.LEN
      dZ = 0
    elif plotDirection == NORTH:
      dX = 0
      dZ = -StraightRoadTile.LEN
    elif plotDirection == SOUTH:
      dX = 0
      dZ = StraightRoadTile.LEN

    return RectangularShape(parentShape.getBoundingBox().transform(dX, dZ))

  @staticmethod
  def create (direction, x, z, shapeSet):
    tile = StraightRoadTile(direction, x, z)
    if not shapeSet.addIfNotIntersecting(tile.getShape()):
      return None

    if not tile._addMinimalPlotShapes(2, shapeSet):
      shapeSet.remove(tile.getShape())
      return None

    return tile

  def place (self, world):
    world.placeStraightRoadTile(self.getShape(), self.getDirection())
    for shapes, reldirection in itertools.izip((self._leftPlotShapes, self._rightPlotShapes), (LEFT, RIGHT)):
      direction = RELDIRECTIONS_TO_DIRECTIONS[self.getDirection()][reldirection]
      for shape in shapes:
        if shape is not None:
          world.placePlot(shape, direction)

class BranchBaseRoadTile (RoadTile):
  def __init__ (self, branchReldirection, branchX, branchZ):
    self._branchReldirection = branchReldirection
    self._branchX = branchX
    self._branchZ = branchZ
    self._branchRoadTiles = []
    # TODO self._branchGeneration?

  def getBranchReldirection (self):
    return self._branchReldirection

  def getBranchDirection (self):
    return RELDIRECTIONS_TO_DIRECTIONS[self.getDirection()][self._branchReldirection]

  def getBranchX (self):
    return self._branchX

  def getBranchZ (self):
    return self._branchZ

  def getBranchRoadTiles (self):
    return self._branchRoadTiles

class TJunctionRoadTile (StraightRoadTile, BranchBaseRoadTile):
  def __init__ (self, direction, x, z, branchReldirection, branchGeneration):
    assert branchReldirection in (LEFT, RIGHT)
    StraightRoadTile.__init__(self, direction, x, z)

    box = self.getShape()
    assert isinstance(box, RectangularShape)
    branchDirection = RELDIRECTIONS_TO_DIRECTIONS[direction][branchReldirection]
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

    BranchBaseRoadTile.__init__(self, branchReldirection, branchX, branchZ)

  @staticmethod
  def create (direction, x, z, branchReldirection, branchGeneration, shapeSet):
    tile = TJunctionRoadTile(direction, x, z, branchReldirection, branchGeneration)
    if not shapeSet.addIfNotIntersecting(tile.getShape()):
      return None

    (tile._leftPlotShapes, tile._rightPlotShapes)[tile.getBranchReldirection()].append(None)
    if not self._addMinimalPlotShapes(1, shapeSet):
      shapeSet.remove(tile.getShape())
      return None

    return tile

  def reminimalisePlotShapes (self):
    StraightRoadTile.reminimalisePlotShapes()
    assert len((self._leftPlotShapes, self._rightPlotShapes)[self.getBranchReldirection()]) == 0
    (self._leftPlotShapes, self._rightPlotShapes)[self.getBranchReldirection()].append(None)

  def place (self, world):
    world.placeTJunctionRoadTile(self.getShape(), self.getDirection(), self.getBranchDirection())
    for shapes, reldirection in itertools.izip((self._leftPlotShapes, self._rightPlotShapes), (LEFT, RIGHT)):
      direction = RELDIRECTIONS_TO_DIRECTIONS[self.getDirection()][reldirection]
      for shape in shapes:
        if shape is not None:
          world.placePlot(shape, direction)
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

    for roadTiles, direction, x, z in itertools.izip(self._roads, (WEST, EAST), (self._centreX - 1, self._centreX), (self._centreZ, self._centreZ)):
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

  def placePlot (self, box, direction):
    self._d.drawBox('.', box)
    if direction == WEST:
      self._d.drawNS('|', box.x1 - 1, (box.z0 + box.z1) / 2 - 1, 3)
    elif direction == EAST:
      self._d.drawNS('|', box.x0, (box.z0 + box.z1) / 2 - 1, 3)
    elif direction == NORTH:
      self._d.drawWE('-', (box.x0 + box.x1) / 2 - 1, box.z1 - 1, 3)
    elif direction == SOUTH:
      self._d.drawWE('-', (box.x0 + box.x1) / 2 - 1, box.z0, 3)

  def placeMarker (self, x, z):
    self._d.drawWE('X', x, z, 1)

  def get (self):
    return self._d.get()
