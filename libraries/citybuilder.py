# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#  City Building Library
#  © Geoff Crossland 2016
# ------------------------------------------------------------------------------
import itertools
import math
import array

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
EMPTY_O = object()

def empty (i):
  return next(i, EMPTY_O) is EMPTY_O

class Shape (object):
  def getTranslation (self, dX, dZ):
    raise NotImplementedError

  def getBoundingBox (self):
    raise NotImplementedError

  def _getRows (self, subBox):
    raise NotImplementedError

  def _any (self, subBox):
    raise NotImplementedError

  def intersects (self, o):
    assert isinstance(o, Shape)
    boundingBoxIntersection = self.getBoundingBox().getIntersection(o.getBoundingBox())
    if boundingBoxIntersection is None:
      return False

    selfRectangular = isinstance(self, RectangularShape)
    oRectangular = isinstance(o, RectangularShape)

    if selfRectangular and oRectangular:
      return True

    if selfRectangular or oRectangular:
      if selfRectangular:
        o1 = o
      else:
        o1 = self
      r = o1._any(boundingBoxIntersection)
      assert r == any(row != 0 for row in o1._getRows(boundingBoxIntersection))
      return r

    selfRows = self._getRows(boundingBoxIntersection)
    oRows = o._getRows(boundingBoxIntersection)
    for selfRow, oRow in itertools.izip(selfRows, oRows):
      if (selfRow & oRow) != 0:
        return True
    assert empty(selfRows)
    assert empty(oRows)
    return False

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

  def contains (self, o):
    assert isinstance(o, RectangularShape)
    subBox = self.getIntersection(o)
    return subBox is not None and subBox.eq(o)

  def getTranslation (self, dX, dZ):
    return RectangularShape(self.x0 + dX, self.z0 + dZ, self.x1 + dX, self.z1 + dZ)

  def getBoundingBox (self):
    return self

  def _getRows (self, subBox):
    assert isinstance(subBox, RectangularShape)
    assert self.contains(subBox)
    return itertools.repeat((1 << (subBox.x1 - subBox.x0)) - 1, (subBox.z1 - subBox.z0))

  def _any (self, subBox):
    assert isinstance(subBox, RectangularShape)
    assert self.contains(subBox)
    return True

class ArbitraryShape (Shape):
  class Template (object):
    @staticmethod
    def rows (*strRows):
      rows = []
      for strRow in strRows:
        row = 0
        for c in reversed(strRow):
          row <<= 1
          if c != ' ':
            row |= 0b1
        rows.append(row)
      return rows

    def __init__ (self, rowsI, dX = None):
      rows = tuple(rowsI)
      assert len(rows) != 0
      if dX is None:
        dX = max(row.bit_length() for row in rows)
      else:
        assert dX >= max(row.bit_length() for row in rows)
      assert dX != 0

      self._rows = rows
      self._dX = dX

    def _getDX (self):
      return self._dX

    def _getDZ (self):
      return len(self._rows)

    def _get (self, x, z):
      return (self._rows[z] >> x) & 0b1

    def getClockwiseQuarterRotation (self):
      dX = self._getDZ()
      dZ = self._getDX()

      rows = []
      for z in xrange(0, dZ):
        row = 0
        for x in xrange(dX - 1, -1, -1):
          row = (row << 1) | self._get(z, dX - 1 - x)
        rows.append(row)

      return ArbitraryShape.Template(rows, dX)

    def getReflectionAroundXAxis (self):
      return ArbitraryShape.Template(reversed(self._rows), self._dX)

    def getReflectionAroundZAxis (self):
      rows = []
      for origRow in self._rows:
        row = 0
        for _ in xrange(0, self._dX):
          row = (row << 1) | (origRow & 0b1)
          origRow >>= 1
        rows.append(row)
      return ArbitraryShape.Template(rows, self._dX)

    def getOutline (self):
      dX = self._getDX()
      dZ = self._getDZ()

      rows = [0] * dZ
      for z in xrange(0, dZ):
        for i in xrange(0, dX):
          if self._get(i, z):
            rows[z] |= 0b1 << i
            break
        for i in xrange(dX - 1, 0, -1):
          if self._get(i, z):
            rows[z] |= 0b1 << i
            break
      for x in xrange(0, dX):
        for i in xrange(0, dZ):
          if self._get(x, i):
            rows[i] |= 0b1 << x
            break
        for i in xrange(dZ - 1, 0, -1):
          if self._get(x, i):
            rows[i] |= 0b1 << x
            break
      return ArbitraryShape.Template(rows, dX)

  def __init__ (self, t, x0, z0):
    assert isinstance(t, ArbitraryShape.Template)
    self._t = t
    self._boundingBox = RectangularShape(x0, z0, x0 + t._getDX(), z0 + t._getDZ())

  def getTranslation (self, dX, dZ):
    return ArbitraryShape(self._t, self._boundingBox.x0 + dX, self._boundingBox.z0 + dZ)

  def getBoundingBox (self):
    return self._boundingBox

  def _getRows (self, subBox):
    assert isinstance(subBox, RectangularShape)
    assert self.getBoundingBox().contains(subBox)
    box = self._boundingBox
    x0 = box.x0
    z0 = box.z0
    x0R = subBox.x0 - x0
    x1RMask = (1 << (subBox.x1 - x0)) - 1
    rows = self._t._rows
    for z in xrange(subBox.z0 - z0, subBox.z1 - z0):
      yield (rows[z] & x1RMask) >> x0R

  def _any (self, subBox):
    assert isinstance(subBox, RectangularShape)
    assert self.getBoundingBox().contains(subBox)
    box = self._boundingBox
    x0 = box.x0
    z0 = box.z0
    xRMask = (1 << (subBox.x1 - x0)) - 1
    xRMask &= ~((1 << (subBox.x0 - x0)) - 1)
    rows = self._t._rows
    for z in xrange(subBox.z0 - z0, subBox.z1 - z0):
      if (rows[z] & xRMask) != 0:
        return True
    return False

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

  def clear (self):
    self._shapes.clear()

  def __iter__ (self):
    return iter(self._shapes)

  def __contains__ (self, o):
    raise TypeError

  def getIntersectors (self, o):
    for shape in self._shapes:
      if shape.intersects(o):
        yield shape

  def intersects (self, o):
    return not empty(self.getIntersectors(o))

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
class World (object):
  def placeStraightRoadTile (self, shape, direction):
    raise NotImplementedError

  def placeBendingStraightRoadTile (self, shape, direction):
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

class Road (object):
  def __init__ (self, generation):
    self._generation = generation
    self._tiles = []

  def getGeneration (self):
    return self._generation

  def getTiles (self):
    return self._tiles

  def addShapesToSet (self, shapeSet):
    for tile in self._tiles:
      tile.addShapesToSet(shapeSet)

  def removeShapesFromSet (self, shapeSet):
    for tile in self._tiles:
      tile.removeShapesFromSet(shapeSet)

  def place (self, world):
    for tile in self._tiles:
      tile.place(world)

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

  def addShapesToSet (self, shapeSet):
    assert self._shape not in shapeSet._shapes
    shapeSet.add(self._shape)
    for shapes in (self._leftPlotShapes, self._rightPlotShapes):
      for s in shapes:
        if s is not None:
          assert s not in shapeSet._shapes
          shapeSet.add(s)

  def removeShapesFromSet (self, shapeSet):
    assert self._shape in shapeSet._shapes
    shapeSet.remove(self._shape)
    for shapes in (self._leftPlotShapes, self._rightPlotShapes):
      for s in shapes:
        if s is not None:
          assert s in shapeSet._shapes
          shapeSet.remove(s)

  def branchise (self, branchReldirection, branchGeneration, shapeSet):
    return None

class StraightRoadTile (RoadTile):
  LEN = 11
  HLEN = (LEN - 1) / 2
  NEXT_D_XZ = {WEST: (-LEN, 0), EAST: (LEN, 0), NORTH: (0, -LEN), SOUTH: (0, LEN)}
  TILE_D_XZ = {WEST: (-LEN + 1, -HLEN), EAST: (0, -HLEN), NORTH: (-HLEN, -LEN + 1), SOUTH: (-HLEN, 0)}

  def __init__ (self, direction, x, z):
    assert direction in (WEST, EAST, NORTH, SOUTH)
    assert isinstance(x, int)
    assert isinstance(z, int)

    dX, dZ = StraightRoadTile.NEXT_D_XZ[direction]
    nextX = x + dX
    nextZ = z + dZ
    dX, dZ = StraightRoadTile.TILE_D_XZ[direction]
    x0 = x + dX
    z0 = z + dZ
    shape = RectangularShape(x0, z0, x0 + StraightRoadTile.LEN, z0 + StraightRoadTile.LEN)

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

    plotDirection = RELDIRECTIONS_TO_DIRECTIONS[self.getDirection()][reldirection]
    dX, dZ = StraightRoadTile.NEXT_D_XZ[plotDirection]

    return parentShape.getTranslation(dX, dZ)

  @staticmethod
  def create (direction, x, z, shapeSet, needsMinimalPlotShapes = True):
    tile = StraightRoadTile(direction, x, z)
    if not shapeSet.addIfNotIntersecting(tile.getShape()):
      return None

    if not tile._addMinimalPlotShapes((0, 2)[needsMinimalPlotShapes], shapeSet):
      shapeSet.remove(tile.getShape())
      return None

    return tile

  def branchise (self, branchReldirection, branchGeneration, shapeSet):
    self.removeShapesFromSet(shapeSet)

    tile = TJunctionRoadTile.create(self.getDirection(), self.getX(), self.getZ(), branchReldirection, branchGeneration, shapeSet)
    if tile is None:
      self.addShapesToSet(shapeSet)
      return None
    assert self.getNextDirection() == tile.getNextDirection()
    assert self.getNextX() == tile.getNextX()
    assert self.getNextZ() == tile.getNextZ()

    tile1 = StraightRoadTile.create(tile.getBranchDirection(), tile.getBranchX(), tile.getBranchZ(), shapeSet, False)
    if tile1 is None:
      tile.removeShapesFromSet(shapeSet)
      self.addShapesToSet(shapeSet)
      return None
    tile.getBranchRoad().getTiles().append(tile1)

    return tile

  def place (self, world):
    world.placeStraightRoadTile(self.getShape(), self.getDirection())
    for shapes, reldirection in itertools.izip((self._leftPlotShapes, self._rightPlotShapes), (LEFT, RIGHT)):
      direction = RELDIRECTIONS_TO_DIRECTIONS[self.getDirection()][reldirection]
      for shape in shapes:
        if shape is not None:
          world.placePlot(shape, direction)

class BendingStraightRoadTile (RoadTile):
  OFF = 2
  OFF_D_XZ = {WEST: (-OFF, 0), EAST: (OFF, 0), NORTH: (0, -OFF), SOUTH: (0, OFF)}

  WEST_LEFT = ArbitraryShape.Template(ArbitraryShape.Template.rows(
    "      *****",
    " **********",
    "***********",
    "***********",
    "*******XXXX",
    "**XXXXXX***",
    "XXX*****XXX",
    "***XXXXXX**",
    "XXXX*******",
    "***********",
    "***********",
    "********** ",
    "*****      "
  ))
  assert WEST_LEFT._getDX() == StraightRoadTile.LEN
  assert WEST_LEFT._getDZ() == StraightRoadTile.LEN + OFF
  WE = (WEST_LEFT, WEST_LEFT.getReflectionAroundXAxis())
  NORTH_LEFT = WEST_LEFT.getClockwiseQuarterRotation()
  NS = (NORTH_LEFT, NORTH_LEFT.getReflectionAroundZAxis())
  TEMPLATES = {
    WEST: WE,
    EAST: WE,
    NORTH: NS,
    SOUTH: NS
  }

  WEST_LEFT_LEFT = ArbitraryShape.Template(ArbitraryShape.Template.rows(
    "          %",
    "     -%%%%%",
    "%%%%%%%%%%%",
    "%%%%%%%%%%%",
    "%%%%%%%%%%%",
    "%%%%%%%%%%%",
    "%%%%%%%%%%%",
    "%%%%%%%%%%%",
    "%%%%%%%%%%%",
    "%%%%%%%%%%%",
    "%%%%%%%%%%%",
    "%%%%%%%%%% ",
    "%%%%%      "
  ))
  WEST_LEFT_RIGHT = WEST_LEFT_LEFT.getClockwiseQuarterRotation().getClockwiseQuarterRotation()
  W = ((WEST_LEFT_LEFT, WEST_LEFT_RIGHT), (WEST_LEFT_RIGHT.getReflectionAroundXAxis(), WEST_LEFT_LEFT.getReflectionAroundXAxis()))
  E = (tuple(reversed(W[LEFT])), tuple(reversed(W[RIGHT])))
  NORTH_LEFT_LEFT = WEST_LEFT_LEFT.getClockwiseQuarterRotation()
  NORTH_LEFT_RIGHT = NORTH_LEFT_LEFT.getClockwiseQuarterRotation().getClockwiseQuarterRotation()
  N = ((NORTH_LEFT_LEFT, NORTH_LEFT_RIGHT), (NORTH_LEFT_RIGHT.getReflectionAroundZAxis(), NORTH_LEFT_LEFT.getReflectionAroundZAxis()))
  S = (tuple(reversed(N[LEFT])), tuple(reversed(N[RIGHT])))
  PLOT_TEMPLATES = {
    WEST: W,
    EAST: E,
    NORTH: N,
    SOUTH: S
  }

  def __init__ (self, direction, x, z, bendReldirection):
    assert direction in (WEST, EAST, NORTH, SOUTH)
    assert bendReldirection in (LEFT, RIGHT)
    assert isinstance(x, int)
    assert isinstance(z, int)

    dX, dZ = StraightRoadTile.NEXT_D_XZ[direction]
    nextX = x + dX
    nextZ = z + dZ
    dX, dZ = BendingStraightRoadTile.OFF_D_XZ[RELDIRECTIONS_TO_DIRECTIONS[direction][bendReldirection]]
    nextX += dX
    nextZ += dZ

    dX, dZ = StraightRoadTile.TILE_D_XZ[direction]
    x0 = x + dX
    z0 = z + dZ
    dX, dZ = BendingStraightRoadTile.OFF_D_XZ[RELDIRECTIONS_TO_DIRECTIONS[direction][bendReldirection]]
    assert all(abs(d) in (0, BendingStraightRoadTile.OFF) for d in (dX, dZ))
    if dX == BendingStraightRoadTile.OFF:
      dX = 0
    if dZ == BendingStraightRoadTile.OFF:
      dZ = 0
    x0 += dX
    z0 += dZ
    shape = ArbitraryShape(BendingStraightRoadTile.TEMPLATES[direction][bendReldirection], x0, z0)

    RoadTile.__init__(self, direction, x, z, shape, nextX, nextZ)

    self._bendReldirection = bendReldirection

  def getNextDirection (self):
    return self.getDirection()

  def _getNextPlotShape (self, shapes, reldirection):
    if len(shapes) == 0:
      box = self.getShape().getBoundingBox()
      parentShape = ArbitraryShape(BendingStraightRoadTile.PLOT_TEMPLATES[self.getDirection()][self._bendReldirection][reldirection], box.x0, box.z0)
    else:
      parentShape = shapes[-1]
      if parentShape is None:
        return None

    plotDirection = RELDIRECTIONS_TO_DIRECTIONS[self.getDirection()][reldirection]
    dX, dZ = StraightRoadTile.NEXT_D_XZ[plotDirection]

    return parentShape.getTranslation(dX, dZ)

  @staticmethod
  def create (direction, x, z, bendReldirection, shapeSet, needsMinimalPlotShapes = True):
    tile = BendingStraightRoadTile(direction, x, z, bendReldirection)
    if not shapeSet.addIfNotIntersecting(tile.getShape()):
      return None

    if not tile._addMinimalPlotShapes((0, 2)[needsMinimalPlotShapes], shapeSet):
      shapeSet.remove(tile.getShape())
      return None

    return tile

  def branchise (self, branchReldirection, branchGeneration, shapeSet):
    return None

  def place (self, world):
    world.placeBendingStraightRoadTile(self.getShape(), self.getDirection())
    for shapes, reldirection in itertools.izip((self._leftPlotShapes, self._rightPlotShapes), (LEFT, RIGHT)):
      direction = RELDIRECTIONS_TO_DIRECTIONS[self.getDirection()][reldirection]
      for shape in shapes:
        if shape is not None:
          world.placePlot(shape, direction)

class BranchBaseRoadTile (RoadTile):
  def __init__ (self, branchReldirection, branchX, branchZ, branchGeneration):
    self._branchReldirection = branchReldirection
    self._branchX = branchX
    self._branchZ = branchZ
    self._branchRoad = Road(branchGeneration)

  def getBranchReldirection (self):
    return self._branchReldirection

  def getBranchDirection (self):
    return RELDIRECTIONS_TO_DIRECTIONS[self.getDirection()][self._branchReldirection]

  def getBranchX (self):
    return self._branchX

  def getBranchZ (self):
    return self._branchZ

  def getBranchRoad (self):
    return self._branchRoad

  def addShapesToSet (self, shapeSet):
    RoadTile.addShapesToSet(self, shapeSet)
    self._branchRoad.addShapesToSet(shapeSet)

  def removeShapesFromSet (self, shapeSet):
    RoadTile.removeShapesFromSet(self, shapeSet)
    self._branchRoad.removeShapesFromSet(shapeSet)

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

    BranchBaseRoadTile.__init__(self, branchReldirection, branchX, branchZ, branchGeneration)

  @staticmethod
  def create (direction, x, z, branchReldirection, branchGeneration, shapeSet):
    tile = TJunctionRoadTile(direction, x, z, branchReldirection, branchGeneration)
    if not shapeSet.addIfNotIntersecting(tile.getShape()):
      return None

    (tile._leftPlotShapes, tile._rightPlotShapes)[tile.getBranchReldirection()].append(None)
    if not tile._addMinimalPlotShapes(1, shapeSet):
      shapeSet.remove(tile.getShape())
      return None

    return tile

  def reminimalisePlotShapes (self):
    StraightRoadTile.reminimalisePlotShapes(self)
    assert len((self._leftPlotShapes, self._rightPlotShapes)[self.getBranchReldirection()]) == 0
    (self._leftPlotShapes, self._rightPlotShapes)[self.getBranchReldirection()].append(None)

  def branchise (self, branchReldirection, branchGeneration, shapeSet):
    return None

  def place (self, world):
    world.placeTJunctionRoadTile(self.getShape(), self.getDirection(), self.getBranchDirection())
    for shapes, reldirection in itertools.izip((self._leftPlotShapes, self._rightPlotShapes), (LEFT, RIGHT)):
      direction = RELDIRECTIONS_TO_DIRECTIONS[self.getDirection()][reldirection]
      for shape in shapes:
        if shape is not None:
          world.placePlot(shape, direction)
    self.getBranchRoad().place(world)

class PlotTile (Tile):
  pass

_RADS_TO_RANGS_FACTOR = 1 / (math.pi * 0.5)

def rang (dX, dZ):
  return (math.atan2(dZ, dX) * _RADS_TO_RANGS_FACTOR) % 4
assert rang(4, 0) == 0
assert rang(4, 4) == 0.5
assert rang(0, 4) == 1
assert rang(-4, 4) == 1.5
assert rang(-4, 0) == 2
assert rang(-4, -4) == 2.5
assert rang(0, -4) == 3
assert rang(4, -4) == 3.5

class City (object):
  def __init__ (self, centreX, centreZ, boundary, boundaryExclusions, endpoints, rng):
    assert isinstance(centreX, int)
    assert isinstance(centreZ, int)
    assert isinstance(boundary, RectangularShape)
    assert isinstance(boundaryExclusions, ShapeSet)
    # TODO target population, initial target population density

    self._centreX = centreX
    self._centreZ = centreZ
    self._boundary = boundary
    self._boundaryExclusions = boundaryExclusions
    self._roads = (Road(0), Road(0))
    self._tileShapeSet = ShapeSet()

    self._reinitTileShapeSet()
    self._buildMainRoads(endpoints, rng)

  @staticmethod
  def invertRectangularShape (s, max = 0x3FFFFFFF):
    assert isinstance(s, RectangularShape)
    return (
      RectangularShape(-max, -max, s.x0, max),
      RectangularShape(s.x1, -max, max, max),
      RectangularShape(s.x0, -max, s.x1, s.z0),
      RectangularShape(s.x0, s.z1, s.x1, max)
    )

  def _reinitTileShapeSet (self):
    tileShapeSet = self._tileShapeSet
    tileShapeSet.clear()
    for shape in itertools.chain(City.invertRectangularShape(self._boundary), self._boundaryExclusions):
      tileShapeSet.add(shape)

  def _buildMainRoads (self, endpoints, rng):
    endpoints = list(endpoints)
    assert len(endpoints) >= 1
    assert all(isinstance(x, int) and isinstance(z, int) for x, z in endpoints)

    primaryDirection, eis = self._buildPrimaryMainRoads(endpoints, rng)
    for i in reversed(eis):
      del endpoints[i]

    self._buildSecondaryMainRoads(endpoints, primaryDirection, rng)

  OPPOSITE_DIRECTIONS = {WEST: EAST, EAST: WEST, NORTH: SOUTH, SOUTH: NORTH}
  D_XZ = {WEST: (-1, 0), EAST: (1, 0), NORTH: (0, -1), SOUTH: (0, 1)}

  def _buildPrimaryMainRoads (self, endpoints, rng):
    endpointDirections = tuple(City._getMainRoadDirection(self._centreX, self._centreZ, x, z) for x, z in endpoints)

    primaryEndpoint0I, primaryEndpoint1I = City._getPrimaryMainRoadEndpoints(endpoints, endpointDirections)

    x, z = endpoints[primaryEndpoint0I]
    primaryDirection = endpointDirections[primaryEndpoint0I]
    self._buildMainRoad(self._roads[0], primaryDirection, self._centreX, self._centreZ, x, z, rng)

    oppositeDirection = City.OPPOSITE_DIRECTIONS[primaryDirection]
    dX, dZ = City.D_XZ[oppositeDirection]

    if primaryEndpoint1I is None:
      tile = StraightRoadTile.create(oppositeDirection, self._centreX + dX, self._centreZ + dZ, self._tileShapeSet)
      if tile is not None:
        self._roads[1].getTiles().append(tile)
      return (primaryDirection, (primaryEndpoint0I,))

    x, z = endpoints[primaryEndpoint1I]
    assert oppositeDirection == endpointDirections[primaryEndpoint1I]
    self._buildMainRoad(self._roads[1], oppositeDirection, self._centreX + dX, self._centreZ + dZ, x, z, rng)

    return (primaryDirection, (primaryEndpoint0I, primaryEndpoint1I))

  @staticmethod
  def _getMainRoadDirection (srcX, srcZ, destX, destZ):
    dX = destX - srcX
    dZ = destZ - srcZ
    assert dX != 0 or dZ != 0
    moreXThanZ = abs(dX) > abs(dZ)
    if dX >= 0:
      if dZ >= 0:
        return (SOUTH, EAST)[moreXThanZ]
      else:
        return (NORTH, EAST)[moreXThanZ]
    else:
      if dZ >= 0:
        return (SOUTH, WEST)[moreXThanZ]
      else:
        return (NORTH, WEST)[moreXThanZ]

  @staticmethod
  def _getPrimaryMainRoadEndpoints (endpoints, endpointDirections):
    oppositeDirection = City.OPPOSITE_DIRECTIONS[endpointDirections[0]]
    for i in xrange(1, len(endpoints)):
      if endpointDirections[i] == oppositeDirection:
        return (0, i)

    wtdDirections = (WEST, EAST)
    if oppositeDirection in wtdDirections:
      wtdDirections = (NORTH, SOUTH)
    for i in xrange(0, len(endpoints)):
      if endpointDirections[i] in wtdDirections:
        oppositeDirection = wtdDirections[endpointDirections[i] == wtdDirections[0]]
        assert oppositeDirection != endpointDirections[i]
        for j in xrange(i + 1, len(endpoints)):
          if endpointDirections[j] == oppositeDirection:
            return (i, j)
        break

    return (0, None)

  def _buildMainRoad (self, road, direction, x, z, destX, destZ, rng):
    tiles = road.getTiles()
    assert len(tiles) == 0 or (direction == tiles[-1].getNextDirection() and x == tiles[-1].getNextX() and z == tiles[-1].getNextZ())

    max = 0x3FFFFFFF
    if direction == WEST:
      assert destX < x
      limitBox = RectangularShape(-max, -max, destX, max)
    elif direction == EAST:
      assert destX > x
      limitBox = RectangularShape(destX, -max, max, max)
    elif direction == NORTH:
      assert destZ < z
      limitBox = RectangularShape(-max, -max, max, destZ)
    elif direction == SOUTH:
      assert destZ > z
      limitBox = RectangularShape(-max, destZ, max, max)

    self._tileShapeSet.add(limitBox)
    try:
      tile = StraightRoadTile.create(direction, x, z, self._tileShapeSet)
      if tile is None:
        return
      tiles.append(tile)
      assert direction == tile.getNextDirection()
      x = tile.getNextX()
      z = tile.getNextZ()

      self._extendRoad(road, direction, x, z, rang(destX - x, destZ - z), rng)
    finally:
      self._tileShapeSet.remove(limitBox)

  DIRECTIONS_AND_CREATORS = (
    (0,                                                         (EAST,  lambda x, z, shapeSet: StraightRoadTile.create(EAST, x, z, shapeSet))),
    (rang(StraightRoadTile.LEN, BendingStraightRoadTile.OFF),   (EAST,  lambda x, z, shapeSet: BendingStraightRoadTile.create(EAST, x, z, RIGHT, shapeSet))),
    (rang(BendingStraightRoadTile.OFF, StraightRoadTile.LEN),   (SOUTH, lambda x, z, shapeSet: BendingStraightRoadTile.create(SOUTH, x, z, LEFT, shapeSet))),
    (1,                                                         (SOUTH, lambda x, z, shapeSet: StraightRoadTile.create(SOUTH, x, z, shapeSet))),
    (rang(-BendingStraightRoadTile.OFF, StraightRoadTile.LEN),  (SOUTH, lambda x, z, shapeSet: BendingStraightRoadTile.create(SOUTH, x, z, RIGHT, shapeSet))),
    (rang(-StraightRoadTile.LEN, BendingStraightRoadTile.OFF),  (WEST,  lambda x, z, shapeSet: BendingStraightRoadTile.create(WEST, x, z, LEFT, shapeSet))),
    (2,                                                         (WEST,  lambda x, z, shapeSet: StraightRoadTile.create(WEST, x, z, shapeSet))),
    (rang(-StraightRoadTile.LEN, -BendingStraightRoadTile.OFF), (WEST,  lambda x, z, shapeSet: BendingStraightRoadTile.create(WEST, x, z, RIGHT, shapeSet))),
    (rang(-BendingStraightRoadTile.OFF, -StraightRoadTile.LEN), (NORTH, lambda x, z, shapeSet: BendingStraightRoadTile.create(NORTH, x, z, LEFT, shapeSet))),
    (3,                                                         (NORTH, lambda x, z, shapeSet: StraightRoadTile.create(NORTH, x, z, shapeSet))),
    (rang(BendingStraightRoadTile.OFF, -StraightRoadTile.LEN),  (NORTH, lambda x, z, shapeSet: BendingStraightRoadTile.create(NORTH, x, z, RIGHT, shapeSet))),
    (rang(StraightRoadTile.LEN, -BendingStraightRoadTile.OFF),  (EAST,  lambda x, z, shapeSet: BendingStraightRoadTile.create(EAST, x, z, LEFT, shapeSet)))
  )
  DIRECTIONS_AND_CREATORS += ((4, DIRECTIONS_AND_CREATORS[0][1]),)
  assert tuple(sorted(DIRECTIONS_AND_CREATORS)) == DIRECTIONS_AND_CREATORS

  @staticmethod
  def _getDirectionAndCreatorPairForRang (rang):
    assert rang >= 0 and rang < 4
    i0 = -1
    i1 = len(City.DIRECTIONS_AND_CREATORS)
    while True:
      assert i0 < i1
      if i0 + 1 == i1:
        assert i0 != -1
        assert i1 != len(City.DIRECTIONS_AND_CREATORS)
        return (City.DIRECTIONS_AND_CREATORS[i0][1], City.DIRECTIONS_AND_CREATORS[i1][1])
      i = (i0 + i1) >> 1
      assert i > i0 and i < i1
      v = City.DIRECTIONS_AND_CREATORS[i][0]
      if rang < v:
        i1 = i
      elif rang > v:
        i0 = i
      else:
        c = City.DIRECTIONS_AND_CREATORS[i][1]
        return (c, c)

  def _extendRoad (self, road, direction, x, z, targetRang, rng):
    tileShapeSet = self._tileShapeSet
    tiles = road.getTiles()
    assert len(tiles) == 0 or (direction == tiles[-1].getNextDirection() and x == tiles[-1].getNextX() and z == tiles[-1].getNextZ())

    srcX = x
    srcZ = z
    attainedRang = targetRang
    while True:
      cs = [c for d, c in City._getDirectionAndCreatorPairForRang(targetRang) if d == direction]
      if len(cs) == 2:
        if (attainedRang - targetRang) % 4 < 2:
          creators = (cs[0],) * 6 + (cs[1],)
        else:
          creators = (cs[1],) * 6 + (cs[0],)
      elif len(cs) == 1:
        creators = (cs[0],)
      else:
        assert False

      tile = rng.choice(creators)(x, z, tileShapeSet)
      if tile is None:
        break
      assert tile.getDirection() == direction
      tiles.append(tile)

      direction = tile.getNextDirection()
      x = tile.getNextX()
      z = tile.getNextZ()
      attainedRang = rang(x - srcX, z - srcZ)

  def _buildSecondaryMainRoads (self, endpoints, primaryDirection, rng):
    if primaryDirection in (WEST, EAST):
      coordinator = lambda x, z: (x - self._centreX, z - self._centreZ)
      reldirectionByOppositeQuadrantPair = (RIGHT, LEFT)
    else:
      coordinator = lambda x, z: (z - self._centreZ, x - self._centreX)
      reldirectionByOppositeQuadrantPair = (LEFT, RIGHT)
    if primaryDirection in (WEST, NORTH):
      negRoad, posRoad = self._roads
    else:
      posRoad, negRoad = self._roads

    for x, z in endpoints:
      maj, min = coordinator(x, z)

      maxMajOffset = abs(min) * BendingStraightRoadTile.OFF / StraightRoadTile.LEN
      assert isinstance(maxMajOffset, int) and maxMajOffset >= 0
      intersectionMaj = maj
      if maj >= 0:
        intersectionMaj = maj - maxMajOffset
        road = posRoad
      else:
        intersectionMaj = maj + maxMajOffset
        road = negRoad

      tiles = road.getTiles()
      for i in xrange(0, len(tiles)):
        tileMaj = coordinator(tiles[i].getX(), tiles[i].getZ())[0]
        assert (maj >= 0 and tileMaj >= 0) or (maj <= 0 and tileMaj <= 0)
        if abs(tileMaj) >= abs(intersectionMaj):
          for j in xrange(i, len(tiles)):
            tile = tiles[j]
            tile0 = tile.branchise(reldirectionByOppositeQuadrantPair[(maj >= 0) ^ (min >= 0)], 0, self._tileShapeSet)
            if tile0 is not None:
              tiles[j] = tile0
              branchTiles = tile0.getBranchRoad().getTiles()
              self._buildMainRoad(tile0.getBranchRoad(), branchTiles[-1].getNextDirection(), branchTiles[-1].getNextX(), branchTiles[-1].getNextZ(), x, z, rng)
              break
          break

  @staticmethod
  def walkRoadTiles (rootRoads, fn):
    this = list(rootRoads)
    next = []
    while len(this) != 0:
      for road in this:
        fn(road)
        for tile in road.getTiles():
          if isinstance(tile, BranchBaseRoadTile):
            next.append(tile.getBranchRoad())
      t = this
      this = next
      next = t
      del next[:]

  def performGrowthIteration (self, rng):
    def reminimalisePlotShapes (road):
      for tile in road.getTiles():
        tile.reminimalisePlotShapes()
        if isinstance(tile, BranchBaseRoadTile):
          reminimalisePlotShapes(tile.getBranchRoad())
    for road in self._roads:
      reminimalisePlotShapes(road)
    self._reinitTileShapeSet()
    tileShapeSet = self._tileShapeSet
    for road in self._roads:
      road.addShapesToSet(tileShapeSet)

    def addBranches (road):
      tiles = road.getTiles()
      reldirectionBranchTiles = (
        [isinstance(t, BranchBaseRoadTile) and t.getBranchReldirection() == LEFT for t in tiles],
        [isinstance(t, BranchBaseRoadTile) and t.getBranchReldirection() == RIGHT for t in tiles]
      )
      for i in xrange(2, len(tiles) - 2):
        tile = tiles[i]
        if not isinstance(tile, BranchBaseRoadTile) and rng.randrange(0, 10) == 0:
          reldirection = rng.choice((LEFT, RIGHT))
          if not any(itertools.islice(reldirectionBranchTiles[reldirection], i - 2, i + 3)):
            tile0 = tile.branchise(reldirection, road.getGeneration() + 1, tileShapeSet)
            if tile0 is not None:
              tiles[i] = tile0
              reldirectionBranchTiles[reldirection][i] = True
    City.walkRoadTiles(self._roads, addBranches)

    def extendRoad (road):
      tiles = road.getTiles()
      for i in xrange(0, rng.randrange(0, 5 + 1)):
        direction = tiles[-1].getNextDirection()
        x = tiles[-1].getNextX()
        z = tiles[-1].getNextZ()
        tile = StraightRoadTile.create(direction, x, z, tileShapeSet)
        if tile is None:
          break
        tiles.append(tile)
    City.walkRoadTiles(self._roads, extendRoad)

  def extendPlotage (self, rng, maxDepth = 0x3FFFFFFF):
    r_plotsAdded = [False]
    def markPlots (road):
      for tile in road.getTiles():
        added = tile.addNextPlotShapes(self._tileShapeSet)
        if added:
          r_plotsAdded[0] = True
    for _ in xrange(1, maxDepth):
      r_plotsAdded[0] = False
      City.walkRoadTiles(self._roads, markPlots)
      if not r_plotsAdded[0]:
        break

  def place (self, world):
    for road in self._roads:
      road.place(world)
      world.placeMarker(self._centreX, self._centreZ)

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
class Display (object):
  def __init__ (self, viewport):
    assert isinstance(viewport, RectangularShape)
    self.viewport = viewport
    self._viewportWidth = viewport.x1 - viewport.x0
    self._vBuffer = array.array('B', itertools.repeat(ord(' '), (viewport.z1 - viewport.z0) * self._viewportWidth))

  def _getI (self, x, z):
    assert isinstance(x, int)
    assert isinstance(z, int)
    viewport = self.viewport
    assert x >= viewport.x0
    assert x < viewport.x1
    assert z >= viewport.z0
    assert z < viewport.z1
    return (z - viewport.z0) * self._viewportWidth + (x - viewport.x0)

  def drawPel (self, c, x0, z0):
    self._vBuffer[self._getI(x0, z0)] = ord(c)

  def drawWE (self, c, x0, z0, l):
    assert isinstance(l, int)
    assert l >= 0
    assert x0 + l <= self.viewport.x1
    i = self._getI(x0, z0)
    pel = ord(c)
    vBuffer = self._vBuffer
    for _ in xrange(0, l):
      vBuffer[i] = pel
      i += 1

  def drawNS (self, c, x0, z0, l):
    assert isinstance(l, int)
    assert l >= 0
    assert z0 + l <= self.viewport.z1
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

  def drawShape (self, c, shape, box = None):
    assert isinstance(shape, Shape)
    if box is None:
      box = shape.getBoundingBox()
    z = box.z0
    for row in shape._getRows(box):
      x = box.x0
      while row:
        if row & 0b1:
          self.drawPel(c, x, z)
        row >>= 1
        x += 1
      z += 1

  def get (self):
    viewport = self.viewport
    viewportWidth = self._viewportWidth
    vBuffer = self._vBuffer
    return [vBuffer[i:i + viewportWidth].tostring() for i in xrange(0, (viewport.z1 - viewport.z0) * viewportWidth, viewportWidth)]

class BitmapWorld (World):
  def __init__ (self, boundingBox):
    self._d = Display(boundingBox)

  def placeStraightRoadTile (self, shape, direction):
    assert isinstance(shape, RectangularShape)
    box = shape

    self._d.drawBox('#', box)
    self._placeRoadTileRoad(box, direction)

  def _placeRoadTileRoad (self, box, direction):
    if direction in (WEST, EAST):
      z = (box.z0 + box.z1) / 2
      self._d.drawWE('-', box.x0 + 1, z, box.x1 - box.x0 - 2)
      if direction == WEST:
        x0 = box.x0 + 1
        x1 = x0 + 1
      else:
        x0 = box.x1 - 2
        x1 = x0 - 1
      self._d.drawPel('*', x0, z)
      self._d.drawPel('*', x1, z - 1)
      self._d.drawPel('*', x1, z + 1)
    elif direction in (NORTH, SOUTH):
      x = (box.x0 + box.x1) / 2
      self._d.drawNS('|', x, box.z0 + 1, box.z1 - box.z0 - 2)
      if direction == NORTH:
        z0 = box.z0 + 1
        z1 = z0 + 1
      else:
        z0 = box.z1 - 2
        z1 = z0 - 1
      self._d.drawPel('*', x, z0)
      self._d.drawPel('*', x - 1, z1)
      self._d.drawPel('*', x + 1, z1)
    else:
      assert False

  _arbitraryShapeTemplateOutlines = {}

  @staticmethod
  def getArbitraryShapeOutline (shape):
    assert isinstance(shape, ArbitraryShape)
    t0 = shape._t
    t1 = BitmapWorld._arbitraryShapeTemplateOutlines.get(t0, None)
    if t1 is None:
      BitmapWorld._arbitraryShapeTemplateOutlines[t0] = t1 = t0.getOutline()
    return t1

  def placeBendingStraightRoadTile (self, shape, direction):
    box = shape.getBoundingBox()

    self._d.drawShape('#', ArbitraryShape(BitmapWorld.getArbitraryShapeOutline(shape), box.x0, box.z0))
    self._placeRoadTileRoad(box, direction)

  def placeTJunctionRoadTile (self, shape, direction, branchDirection):
    box = shape

    self.placeStraightRoadTile(shape, direction)

    l = (box.x1 - box.x0 - 2) / 2
    assert l == (box.z1 - box.z0 - 2) / 2
    if branchDirection == WEST:
      self._d.drawWE('-', box.x0 + 1, (box.z0 + box.z1) / 2, l)
    elif branchDirection == EAST:
      self._d.drawWE('-', (box.x0 + box.x1) / 2 + 1, (box.z0 + box.z1) / 2, l)
    elif branchDirection == NORTH:
      self._d.drawNS('|', (box.x0 + box.x1) / 2, box.z0 + 1, l)
    elif branchDirection == SOUTH:
      self._d.drawNS('|', (box.x0 + box.x1) / 2, (box.z0 + box.z1) / 2 + 1, l)
    else:
      assert False

  def placePlot (self, shape, direction):
    box = shape.getBoundingBox()
    if isinstance(shape, RectangularShape):
      self._d.drawBox('.', shape)
      if direction == WEST:
        self._d.drawNS('o', box.x1 - 1, (box.z0 + box.z1) / 2 - 1, 3)
      elif direction == EAST:
        self._d.drawNS('o', box.x0, (box.z0 + box.z1) / 2 - 1, 3)
      elif direction == NORTH:
        self._d.drawWE('o', (box.x0 + box.x1) / 2 - 1, box.z1 - 1, 3)
      elif direction == SOUTH:
        self._d.drawWE('o', (box.x0 + box.x1) / 2 - 1, box.z0, 3)
    else:
      shape = ArbitraryShape(BitmapWorld.getArbitraryShapeOutline(shape), box.x0, box.z0)
      self._d.drawShape('.', shape)
      if direction in (WEST, EAST):
        z0 = (box.z0 + box.z1) / 2  - 1
        z1 = z0 + 3
        xMid = (box.x0 + box.x1) / 2
        if direction == WEST:
          x0 = xMid
          x1 = box.x1
        else:
          x0 = box.x0
          x1 = xMid
      elif direction in (NORTH, SOUTH):
        x0 = (box.x0 + box.x1) / 2  - 1
        x1 = x0 + 3
        zMid = (box.z0 + box.z1) / 2
        if direction == NORTH:
          z0 = zMid
          z1 = box.z1
        else:
          z0 = box.z0
          z1 = zMid
      self._d.drawShape('o', shape, RectangularShape(x0, z0, x1, z1))

  def placeMarker (self, x, z):
    self._d.drawWE('X', x, z, 1)

  def getXpm (self):
    d = self._d
    return ""\
      "! XPM2\n"\
      "" + "{} {} 8 1\n".format(d.viewport.x1 - d.viewport.x0, d.viewport.z1 - d.viewport.z0) + ""\
      "  c #FFFFFF\n"\
      "# c #000000\n"\
      "- c #7F7FFF\n"\
      "| c #7F7FFF\n"\
      "* c #0000FF\n"\
      ". c #7F7F7F\n"\
      "o c #BFBFBF\n"\
      "X c #FF0000\n"\
      "" + "\n".join(d.get())

class Rng (object):
  def _r (self):
    raise NotImplementedError

  def randrange (self, start, stop):
    return self._r() % (stop - start) + start

  def choice (self, seq):
    return seq[self._r() % len(seq)]

class ConstantRng (Rng):
  def __init__ (self, v):
    self._v = v

  def _r (self):
    return self._v

class LinearRng (Rng):
  def __init__ (self):
    self._v = 0

  def _r (self):
    v = self._v
    self._v += 1
    return v
