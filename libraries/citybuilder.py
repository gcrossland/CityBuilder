# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#  City Building Library
#  © Geoff Crossland 2016
# ------------------------------------------------------------------------------
import itertools
import math

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
EMPTY_O = object()

def empty (i):
  return next(i, EMPTY_O) is EMPTY_O

def max2 (a, b):
  if a > b:
    return a
  return b

def min2 (a, b):
  if a < b:
    return a
  return b

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

    selfRectangular = self.__class__ is RectangularShape
    assert not (selfRectangular and o.__class__ is RectangularShape)
    if selfRectangular or o.__class__ is RectangularShape:
      if selfRectangular:
        o1 = o
      else:
        o1 = self
      r = o1._any(boundingBoxIntersection)
      assert r == any(row for row in o1._getRows(boundingBoxIntersection))
      return r

    selfRows = self._getRows(boundingBoxIntersection)
    oRows = o._getRows(boundingBoxIntersection)
    for selfRow, oRow in itertools.izip(selfRows, oRows):
      if (selfRow & oRow) != 0b0:
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
    x0 = max2(self.x0, o.x0)
    x1 = min2(self.x1, o.x1)
    if x0 >= x1:
      return None
    z0 = max2(self.z0, o.z0)
    z1 = min2(self.z1, o.z1)
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
    return itertools.repeat((0b1 << (subBox.x1 - subBox.x0)) - 1, (subBox.z1 - subBox.z0))

  def _any (self, subBox):
    assert isinstance(subBox, RectangularShape)
    assert self.contains(subBox)
    return True

  def intersects (self, o):
    if o.__class__ is RectangularShape:
      return max2(self.x0, o.x0) < min2(self.x1, o.x1) and max2(self.z0, o.z0) < min2(self.z1, o.z1)
    return Shape.intersects(self, o)

class ArbitraryShape (Shape):
  class Template (object):
    @staticmethod
    def rows (*strRows):
      rows = []
      for strRow in strRows:
        row = 0b0
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
        row = 0b0
        for x in xrange(dX - 1, -1, -1):
          row = (row << 1) | self._get(z, dX - 1 - x)
        rows.append(row)

      return ArbitraryShape.Template(rows, dX)

    def getReflectionAroundXAxis (self):
      return ArbitraryShape.Template(reversed(self._rows), self._dX)

    def getReflectionAroundZAxis (self):
      rows = []
      for origRow in self._rows:
        row = 0b0
        for _ in xrange(0, self._dX):
          row = (row << 1) | (origRow & 0b1)
          origRow >>= 1
        rows.append(row)
      return ArbitraryShape.Template(rows, self._dX)

    def getOutline (self):
      dX = self._getDX()
      dZ = self._getDZ()

      rows = [0b0] * dZ
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
    x1RMask = (0b1 << (subBox.x1 - x0)) - 1
    rows = self._t._rows
    for z in xrange(subBox.z0 - z0, subBox.z1 - z0):
      yield (rows[z] & x1RMask) >> x0R

  def _any (self, subBox):
    assert isinstance(subBox, RectangularShape)
    assert self.getBoundingBox().contains(subBox)
    box = self._boundingBox
    x0 = box.x0
    z0 = box.z0
    xRMask = (0b1 << (subBox.x1 - x0)) - 1
    xRMask &= ~((0b1 << (subBox.x0 - x0)) - 1)
    rows = self._t._rows
    for z in xrange(subBox.z0 - z0, subBox.z1 - z0):
      if (rows[z] & xRMask) != 0b0:
        return True
    return False

class ShapeSet (object):
  def __init__ (self, boundary):
    assert isinstance(boundary, RectangularShape)
    self._bucketDXExp = 5
    self._bucketDX = 1 << self._bucketDXExp
    self._bucketDZExp = 5
    self._bucketDZ = 1 << self._bucketDZExp
    self._boundary = boundary
    _, _, self._bucketsXSize, bucketsZSize = self._getBs(boundary)
    self._buckets = [None] * (self._bucketsXSize * bucketsZSize)

  def _getBs (self, box):
    boundary = self._boundary
    x0 = boundary.x0
    z0 = boundary.z0
    bucketDXExp = self._bucketDXExp
    bucketDZExp = self._bucketDZExp
    return (
      (box.x0 - x0) >> bucketDXExp,
      (box.z0 - z0) >> bucketDZExp,
      (box.x1 - x0 + self._bucketDX - 1) >> bucketDXExp,
      (box.z1 - z0 + self._bucketDZ - 1) >> bucketDZExp
    )

  def _getBucketsI (self, bx, bz):
    assert bx >= 0
    assert bx < self._bucketsXSize
    assert bz >= 0
    r = bz * self._bucketsXSize + bx
    assert r < len(self._buckets)
    return r

  def _getBucketsIs (self, box, withBs = False):
    bx0, bz0, bx1, bz1 = self._getBs(box)

    i = self._getBucketsI(bx0, bz0)
    iSkip = self._bucketsXSize - (bx1 - bx0)
    for bz in xrange(bz0, bz1):
      assert i == self._getBucketsI(bx0, bz)
      for bx in xrange(bx0, bx1):
        if withBs:
          yield i, bx, bz
        else:
          yield i
        i += 1
      i += iSkip

  def add (self, o):
    assert isinstance(o, Shape)
    self._add(o, self._boundary.getIntersection(o.getBoundingBox()))

  def _add (self, o, boundingBoxIntersection):
    if boundingBoxIntersection is None:
      assert all(o not in bucket for bucket in self._buckets if bucket is not None)
      return

    buckets = self._buckets
    tmp = RectangularShape(0, 0, 1, 1)
    for i, bx, bz in self._getBucketsIs(boundingBoxIntersection, True):
      tmp.x0 = self._boundary.x0 + (bx * self._bucketDX)
      tmp.z0 = self._boundary.z0 + (bz * self._bucketDZ)
      tmp.x1 = tmp.x0 + self._bucketDX
      tmp.z1 = tmp.z0 + self._bucketDZ
      if tmp.intersects(o):
        bucket = buckets[i]
        if bucket is None:
          buckets[i] = bucket = set()
        bucket.add(o)

  addUncontained = add
  if __debug__:
    def addUncontained (self, o):
      assert all(o not in bucket for bucket in self._buckets if bucket is not None)
      self.add(o)

  def addIfNotIntersecting (self, o):
    assert isinstance(o, Shape)
    boundingBoxIntersection = self._boundary.getIntersection(o.getBoundingBox())
    if not empty(self._getIntersectors(o, boundingBoxIntersection)):
      return False
    else:
      self._add(o, boundingBoxIntersection)
      return True

  def discard (self, o):
    assert isinstance(o, Shape)
    boundingBoxIntersection = self._boundary.getIntersection(o.getBoundingBox())
    if boundingBoxIntersection is None:
      assert all(o not in bucket for bucket in self._buckets if bucket is not None)
      return

    buckets = self._buckets
    for i in self._getBucketsIs(boundingBoxIntersection):
      bucket = buckets[i]
      if bucket is not None:
        bucket.discard(o)

  discardContained = discard
  if __debug__:
    def discardContained (self, o):
      assert not self._boundary.intersects(o) or any(o in bucket for bucket in self._buckets if bucket is not None)
      self.discard(o)

  def clear (self):
    for bucket in self._buckets:
      if bucket is not None:
        bucket.clear()

  def __contains__ (self, o):
    raise TypeError

  def getIntersectors (self, o):
    assert isinstance(o, Shape)
    return self._getIntersectors(o, self._boundary.getIntersection(o.getBoundingBox()))

  def _getIntersectors (self, o, boundingBoxIntersection):
    if boundingBoxIntersection is None:
      # DODGY o might be a totally empty shape
      yield None
      return

    buckets = self._buckets
    for i in self._getBucketsIs(boundingBoxIntersection):
      bucket = buckets[i]
      if bucket is not None:
        for shape in bucket:
          if shape.intersects(o):
            yield shape
    if not boundingBoxIntersection.eq(o.getBoundingBox()):
      # DODGY o might be empty outside the boundary
      yield None

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
  def __init__ (self):
    self._tiles = []

  def init (self, targetRang, branchisingState):
    assert targetRang >= 0 and targetRang < 4
    self._targetRang = targetRang
    self._branchisingState = branchisingState

  def getTargetRang (self, tileI):
    return self._targetRang

  def getBranchisingState (self):
    return self._branchisingState

  def setBranchisingState (self, branchisingState):
    self._branchisingState = branchisingState

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
          shapeSet.discardContained(shape)
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
    shapeSet.addUncontained(self._shape)
    for shapes in (self._leftPlotShapes, self._rightPlotShapes):
      for s in shapes:
        if s is not None:
          shapeSet.addUncontained(s)

  def removeShapesFromSet (self, shapeSet):
    shapeSet.discardContained(self._shape)
    for shapes in (self._leftPlotShapes, self._rightPlotShapes):
      for s in shapes:
        if s is not None:
          shapeSet.discardContained(s)

  def branchise (self, branchReldirection, shapeSet):
    return None

class StraightRoadTile (RoadTile):
  LEN = 11
  NEXT_DS = {WEST: (-LEN, 0), EAST: (LEN, 0), NORTH: (0, -LEN), SOUTH: (0, LEN)}
  HLEN = (LEN - 1) / 2
  TILE_ORIGIN_DS = {WEST: (-LEN + 1, -HLEN), EAST: (0, -HLEN), NORTH: (-HLEN, -LEN + 1), SOUTH: (-HLEN, 0)}

  def __init__ (self, direction, x, z):
    assert direction in (WEST, EAST, NORTH, SOUTH)
    assert isinstance(x, int)
    assert isinstance(z, int)

    dX, dZ = StraightRoadTile.NEXT_DS[direction]
    nextX = x + dX
    nextZ = z + dZ
    dX, dZ = StraightRoadTile.TILE_ORIGIN_DS[direction]
    x0 = x + dX
    z0 = z + dZ
    shape = RectangularShape(x0, z0, x0 + StraightRoadTile.LEN, z0 + StraightRoadTile.LEN)

    RoadTile.__init__(self, direction, x, z, shape, nextX, nextZ)

  def getNextDirection (self):
    return self.getDirection()

  PLOT_DEPTH = 7
  PLOT_NEXT_DS = {WEST: (-PLOT_DEPTH, 0), EAST: (PLOT_DEPTH, 0), NORTH: (0, -PLOT_DEPTH), SOUTH: (0, PLOT_DEPTH)}

  WEST_LEFT = RectangularShape(0, LEN, LEN, LEN + PLOT_DEPTH)
  WEST_RIGHT = RectangularShape(0, -PLOT_DEPTH, LEN, 0)
  W = (WEST_LEFT, WEST_RIGHT)
  E = tuple(reversed(W))
  NORTH_LEFT = RectangularShape(-PLOT_DEPTH, 0, 0, LEN)
  NORTH_RIGHT = RectangularShape(LEN, 0, LEN + PLOT_DEPTH, LEN)
  N = (NORTH_LEFT, NORTH_RIGHT)
  S = tuple(reversed(N))
  PLOT_SHAPES = {
    WEST: W,
    EAST: E,
    NORTH: N,
    SOUTH: S
  }

  def _getNextPlotShape (self, shapes, reldirection):
    if len(shapes) == 0:
      box = self.getShape()
      return StraightRoadTile.PLOT_SHAPES[self.getDirection()][reldirection].getTranslation(box.x0, box.z0)
    else:
      parentShape = shapes[-1]
      if parentShape is None:
        return None
      plotDirection = RELDIRECTIONS_TO_DIRECTIONS[self.getDirection()][reldirection]
      dX, dZ = StraightRoadTile.PLOT_NEXT_DS[plotDirection]
      return parentShape.getTranslation(dX, dZ)

  @staticmethod
  def create (direction, x, z, shapeSet, needsMinimalPlotShapes = True):
    tile = StraightRoadTile(direction, x, z)
    if not shapeSet.addIfNotIntersecting(tile.getShape()):
      return None

    if not tile._addMinimalPlotShapes((0, 2)[needsMinimalPlotShapes], shapeSet):
      shapeSet.discardContained(tile.getShape())
      return None

    return tile

  def branchise (self, branchReldirection, shapeSet):
    self.removeShapesFromSet(shapeSet)

    tile = TJunctionRoadTile.create(self.getDirection(), self.getX(), self.getZ(), branchReldirection, shapeSet)
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
  LEN = StraightRoadTile.LEN
  NEXT_DS = StraightRoadTile.NEXT_DS
  HLEN = StraightRoadTile.HLEN
  TILE_ORIGIN_DS = StraightRoadTile.TILE_ORIGIN_DS
  OFF = 2
  OFF_DS = {WEST: (-OFF, 0), EAST: (OFF, 0), NORTH: (0, -OFF), SOUTH: (0, OFF)}

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
  assert WEST_LEFT._getDX() == LEN
  assert WEST_LEFT._getDZ() == LEN + OFF
  WE = (WEST_LEFT, WEST_LEFT.getReflectionAroundXAxis())
  NORTH_LEFT = WEST_LEFT.getClockwiseQuarterRotation()
  NS = (NORTH_LEFT, NORTH_LEFT.getReflectionAroundZAxis())
  TEMPLATES = {
    WEST: WE,
    EAST: WE,
    NORTH: NS,
    SOUTH: NS
  }

  def __init__ (self, direction, x, z, bendReldirection):
    assert direction in (WEST, EAST, NORTH, SOUTH)
    assert bendReldirection in (LEFT, RIGHT)
    assert isinstance(x, int)
    assert isinstance(z, int)

    dX, dZ = BendingStraightRoadTile.NEXT_DS[direction]
    nextX = x + dX
    nextZ = z + dZ
    dX, dZ = BendingStraightRoadTile.OFF_DS[RELDIRECTIONS_TO_DIRECTIONS[direction][bendReldirection]]
    nextX += dX
    nextZ += dZ

    dX, dZ = BendingStraightRoadTile.TILE_ORIGIN_DS[direction]
    x0 = x + dX
    z0 = z + dZ
    dX, dZ = BendingStraightRoadTile.OFF_DS[RELDIRECTIONS_TO_DIRECTIONS[direction][bendReldirection]]
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

  PLOT_DEPTH = StraightRoadTile.PLOT_DEPTH
  PLOT_NEXT_DS = StraightRoadTile.PLOT_NEXT_DS

  WEST_LEFT_LEFT = ArbitraryShape(ArbitraryShape.Template(ArbitraryShape.Template.rows(
    "          %",
    "     -%%%%%",
    "%%%%%%%%%%%",
    "%%%%%%%%%%%",
    "%%%%%%%%%%%",
    "%%%%%%%%%%%",
    "%%%%%%%%%%%",
    "%%%%%%%%%% ",
    "%%%%%      "
  )), 0, LEN)
  assert WEST_LEFT_LEFT._t._getDX() == LEN
  assert WEST_LEFT_LEFT._t._getDZ() == PLOT_DEPTH + OFF
  WEST_LEFT_RIGHT = ArbitraryShape(WEST_LEFT_LEFT._t.getClockwiseQuarterRotation().getClockwiseQuarterRotation(), 0, -PLOT_DEPTH)
  WEST_RIGHT_LEFT = ArbitraryShape(WEST_LEFT_RIGHT._t.getReflectionAroundXAxis(), 0, LEN)
  WEST_RIGHT_RIGHT = ArbitraryShape(WEST_LEFT_LEFT._t.getReflectionAroundXAxis(), 0, -PLOT_DEPTH)
  W = ((WEST_LEFT_LEFT, WEST_LEFT_RIGHT), (WEST_RIGHT_LEFT, WEST_RIGHT_RIGHT))
  E = (tuple(reversed(W[LEFT])), tuple(reversed(W[RIGHT])))
  NORTH_LEFT_LEFT = ArbitraryShape(WEST_LEFT_LEFT._t.getClockwiseQuarterRotation(), -PLOT_DEPTH, 0)
  NORTH_LEFT_RIGHT = ArbitraryShape(NORTH_LEFT_LEFT._t.getClockwiseQuarterRotation().getClockwiseQuarterRotation(), LEN, 0)
  NORTH_RIGHT_LEFT = ArbitraryShape(NORTH_LEFT_RIGHT._t.getReflectionAroundZAxis(), -PLOT_DEPTH, 0)
  NORTH_RIGHT_RIGHT = ArbitraryShape(NORTH_LEFT_LEFT._t.getReflectionAroundZAxis(), LEN, 0)
  N = ((NORTH_LEFT_LEFT, NORTH_LEFT_RIGHT), (NORTH_RIGHT_LEFT, NORTH_RIGHT_RIGHT))
  S = (tuple(reversed(N[LEFT])), tuple(reversed(N[RIGHT])))
  PLOT_SHAPES = {
    WEST: W,
    EAST: E,
    NORTH: N,
    SOUTH: S
  }

  def _getNextPlotShape (self, shapes, reldirection):
    if len(shapes) == 0:
      box = self.getShape().getBoundingBox()
      return BendingStraightRoadTile.PLOT_SHAPES[self.getDirection()][self._bendReldirection][reldirection].getTranslation(box.x0, box.z0)
    else:
      parentShape = shapes[-1]
      if parentShape is None:
        return None
      plotDirection = RELDIRECTIONS_TO_DIRECTIONS[self.getDirection()][reldirection]
      dX, dZ = BendingStraightRoadTile.PLOT_NEXT_DS[plotDirection]
      return parentShape.getTranslation(dX, dZ)

  @staticmethod
  def create (direction, x, z, bendReldirection, shapeSet, needsMinimalPlotShapes = True):
    tile = BendingStraightRoadTile(direction, x, z, bendReldirection)
    if not shapeSet.addIfNotIntersecting(tile.getShape()):
      return None

    if not tile._addMinimalPlotShapes((0, 2)[needsMinimalPlotShapes], shapeSet):
      shapeSet.discardContained(tile.getShape())
      return None

    return tile

  def branchise (self, branchReldirection, shapeSet):
    return None

  def place (self, world):
    world.placeBendingStraightRoadTile(self.getShape(), self.getDirection())
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
    self._branchRoad = Road()

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
  def __init__ (self, direction, x, z, branchReldirection):
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
  def create (direction, x, z, branchReldirection, shapeSet):
    tile = TJunctionRoadTile(direction, x, z, branchReldirection)
    if not shapeSet.addIfNotIntersecting(tile.getShape()):
      return None

    (tile._leftPlotShapes, tile._rightPlotShapes)[tile.getBranchReldirection()].append(None)
    if not tile._addMinimalPlotShapes(1, shapeSet):
      shapeSet.discardContained(tile.getShape())
      return None

    return tile

  def reminimalisePlotShapes (self):
    StraightRoadTile.reminimalisePlotShapes(self)
    assert len((self._leftPlotShapes, self._rightPlotShapes)[self.getBranchReldirection()]) == 0
    (self._leftPlotShapes, self._rightPlotShapes)[self.getBranchReldirection()].append(None)

  def branchise (self, branchReldirection, shapeSet):
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
    # TODO target population, initial target population density
    self._centreX = centreX
    self._centreZ = centreZ
    self._tileShapeSet = ShapeSet(boundary)
    self._boundaryExclusions = tuple(boundaryExclusions)
    assert all(isinstance(s, Shape) for s in self._boundaryExclusions)
    self._maxGeneration = 0
    self._plottageExtended = False
    self._primaryMainRoads = None
    self._secondaryMainRoads = None

    self._reinitTileShapeSet()
    self._buildMainRoads(endpoints, rng)

  def _reinitTileShapeSet (self):
    tileShapeSet = self._tileShapeSet
    tileShapeSet.clear()
    for shape in self._boundaryExclusions:
      tileShapeSet.addUncontained(shape)

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
    assert self._primaryMainRoads is None
    self._primaryMainRoads = (Road(), Road())

    endpointDirections = tuple(City._getMainRoadDirection(self._centreX, self._centreZ, x, z) for x, z in endpoints)

    primaryEndpoint0I, primaryEndpoint1I = City._getPrimaryMainRoadEndpoints(endpointDirections)

    x, z = endpoints[primaryEndpoint0I]
    primaryDirection = endpointDirections[primaryEndpoint0I]
    self._buildMainRoad(self._primaryMainRoads[0], primaryDirection, self._centreX, self._centreZ, x, z, rng)

    oppositeDirection = City.OPPOSITE_DIRECTIONS[primaryDirection]
    dX, dZ = City.D_XZ[oppositeDirection]

    if primaryEndpoint1I is None:
      tile = StraightRoadTile.create(oppositeDirection, self._centreX + dX, self._centreZ + dZ, self._tileShapeSet)
      if tile is not None:
        self._primaryMainRoads[1].getTiles().append(tile)
      self._primaryMainRoads[1].init(rang(dX, dZ), City._INIT_BRANCHISING_STATE)
      return (primaryDirection, (primaryEndpoint0I,))

    x, z = endpoints[primaryEndpoint1I]
    assert oppositeDirection == endpointDirections[primaryEndpoint1I]
    self._buildMainRoad(self._primaryMainRoads[1], oppositeDirection, self._centreX + dX, self._centreZ + dZ, x, z, rng)

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
  def _getPrimaryMainRoadEndpoints (endpointDirections):
    oppositeDirection = City.OPPOSITE_DIRECTIONS[endpointDirections[0]]
    for i in xrange(1, len(endpointDirections)):
      if endpointDirections[i] == oppositeDirection:
        return (0, i)

    wtdDirections = (WEST, EAST)
    if oppositeDirection in wtdDirections:
      wtdDirections = (NORTH, SOUTH)
    for i in xrange(0, len(endpointDirections)):
      if endpointDirections[i] in wtdDirections:
        oppositeDirection = wtdDirections[endpointDirections[i] == wtdDirections[0]]
        assert oppositeDirection != endpointDirections[i]
        for j in xrange(i + 1, len(endpointDirections)):
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

    self._tileShapeSet.addUncontained(limitBox)
    try:
      tile = StraightRoadTile.create(direction, x, z, self._tileShapeSet)
      if tile is None:
        return
      tiles.append(tile)
      assert direction == tile.getNextDirection()
      x = tile.getNextX()
      z = tile.getNextZ()

      road.init(rang(destX - x, destZ - z), City._INIT_BRANCHISING_STATE)
      self._extendRoad(road, direction, x, z, -1, rng)
    finally:
      self._tileShapeSet.discardContained(limitBox)

  DIRECTIONS_AND_CREATORS = (
    (0,                                                                (EAST,  lambda x, z, shapeSet: StraightRoadTile.create(EAST, x, z, shapeSet))),
    (rang(BendingStraightRoadTile.LEN, BendingStraightRoadTile.OFF),   (EAST,  lambda x, z, shapeSet: BendingStraightRoadTile.create(EAST, x, z, RIGHT, shapeSet))),
    (rang(BendingStraightRoadTile.OFF, BendingStraightRoadTile.LEN),   (SOUTH, lambda x, z, shapeSet: BendingStraightRoadTile.create(SOUTH, x, z, LEFT, shapeSet))),
    (1,                                                                (SOUTH, lambda x, z, shapeSet: StraightRoadTile.create(SOUTH, x, z, shapeSet))),
    (rang(-BendingStraightRoadTile.OFF, BendingStraightRoadTile.LEN),  (SOUTH, lambda x, z, shapeSet: BendingStraightRoadTile.create(SOUTH, x, z, RIGHT, shapeSet))),
    (rang(-BendingStraightRoadTile.LEN, BendingStraightRoadTile.OFF),  (WEST,  lambda x, z, shapeSet: BendingStraightRoadTile.create(WEST, x, z, LEFT, shapeSet))),
    (2,                                                                (WEST,  lambda x, z, shapeSet: StraightRoadTile.create(WEST, x, z, shapeSet))),
    (rang(-BendingStraightRoadTile.LEN, -BendingStraightRoadTile.OFF), (WEST,  lambda x, z, shapeSet: BendingStraightRoadTile.create(WEST, x, z, RIGHT, shapeSet))),
    (rang(-BendingStraightRoadTile.OFF, -BendingStraightRoadTile.LEN), (NORTH, lambda x, z, shapeSet: BendingStraightRoadTile.create(NORTH, x, z, LEFT, shapeSet))),
    (3,                                                                (NORTH, lambda x, z, shapeSet: StraightRoadTile.create(NORTH, x, z, shapeSet))),
    (rang(BendingStraightRoadTile.OFF, -BendingStraightRoadTile.LEN),  (NORTH, lambda x, z, shapeSet: BendingStraightRoadTile.create(NORTH, x, z, RIGHT, shapeSet))),
    (rang(BendingStraightRoadTile.LEN, -BendingStraightRoadTile.OFF),  (EAST,  lambda x, z, shapeSet: BendingStraightRoadTile.create(EAST, x, z, LEFT, shapeSet)))
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

  def _extendRoad (self, road, direction, x, z, maxTiles, rng):
    assert isinstance(maxTiles, int)
    assert maxTiles == -1 or maxTiles >= 0
    tileShapeSet = self._tileShapeSet
    tiles = road.getTiles()
    assert len(tiles) == 0 or (direction == tiles[-1].getNextDirection() and x == tiles[-1].getNextX() and z == tiles[-1].getNextZ())

    srcX = x
    srcZ = z
    tc = 0
    attainedRang = targetRang = road.getTargetRang(len(tiles))
    while True:
      if tc == maxTiles:
        return

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

      tile = rng(creators)(x, z, tileShapeSet)
      if tile is None:
        break
      assert tile.getDirection() == direction
      tiles.append(tile)
      tc += 1

      direction = tile.getNextDirection()
      x = tile.getNextX()
      z = tile.getNextZ()
      targetRang = road.getTargetRang(len(tiles))
      attainedRang = rang(x - srcX, z - srcZ)

  def _buildSecondaryMainRoads (self, endpoints, primaryDirection, rng):
    assert self._primaryMainRoads is not None
    assert self._secondaryMainRoads is None
    secondaryMainRoads = []

    if primaryDirection in (WEST, EAST):
      coordinator = lambda x, z: (x - self._centreX, z - self._centreZ)
      reldirectionByOppositeQuadrantPair = (RIGHT, LEFT)
    else:
      coordinator = lambda x, z: (z - self._centreZ, x - self._centreX)
      reldirectionByOppositeQuadrantPair = (LEFT, RIGHT)
    if primaryDirection in (WEST, NORTH):
      negRoad, posRoad = self._primaryMainRoads
    else:
      posRoad, negRoad = self._primaryMainRoads

    for x, z in endpoints:
      maj, min = coordinator(x, z)

      maxMajOffset = abs(min) * BendingStraightRoadTile.OFF / BendingStraightRoadTile.LEN
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
            tile0 = tile.branchise(reldirectionByOppositeQuadrantPair[(maj >= 0) ^ (min >= 0)], self._tileShapeSet)
            if tile0 is not None:
              tiles[j] = tile0
              branchRoad = tile0.getBranchRoad()
              secondaryMainRoads.append(branchRoad)
              branchTiles = branchRoad.getTiles()
              self._buildMainRoad(branchRoad, branchTiles[-1].getNextDirection(), branchTiles[-1].getNextX(), branchTiles[-1].getNextZ(), x, z, rng)
              break
          break

    self._secondaryMainRoads = tuple(secondaryMainRoads)

  def getMaxGeneration (self):
    return self._maxGeneration

  def getRoads (self, targetGeneration = -1):
    assert isinstance(targetGeneration, int)
    assert targetGeneration == -1 or targetGeneration >= 0
    this = list(self._primaryMainRoads)
    this += self._secondaryMainRoads
    thisGeneration = 0
    next = []
    while len(this) != 0:
      assert targetGeneration == -1 or thisGeneration <= targetGeneration
      for road in this:
        if targetGeneration == -1 or thisGeneration != targetGeneration:
          for tile in road.getTiles():
            if isinstance(tile, BranchBaseRoadTile):
              branchRoad = tile.getBranchRoad()
              if thisGeneration != 0 or branchRoad not in self._secondaryMainRoads:
                next.append(branchRoad)
        if targetGeneration == -1 or thisGeneration == targetGeneration:
          yield (road, thisGeneration)

      if thisGeneration == targetGeneration:
        return

      t = this
      this = next
      next = t
      thisGeneration += 1
      del next[:]

  _INIT_BRANCHISING_STATE = (0, 0.0)
  _GAP = 3

  def addBranches (self, targetGeneration, wholeRoad, rng, branchChoices, lengthChoices):
    assert not self._plottageExtended
    for road, generation in self.getRoads(targetGeneration):
      if wholeRoad:
        i, branchProb = City._INIT_BRANCHISING_STATE
      else:
        i, branchProb = road.getBranchisingState()

      while i < City._GAP:
        branchProb += rng(branchChoices)
        i += 1

      tiles = road.getTiles()
      reldirectionBranchTiles = (
        [isinstance(t, BranchBaseRoadTile) and t.getBranchReldirection() == LEFT for t in tiles],
        [isinstance(t, BranchBaseRoadTile) and t.getBranchReldirection() == RIGHT for t in tiles]
      )
      while i < len(tiles) - City._GAP:
        tile = tiles[i]
        branchProb += rng(branchChoices)
        if branchProb >= 1:
          reldirection = rng((LEFT, RIGHT))
          if not any(itertools.islice(reldirectionBranchTiles[reldirection], i - City._GAP, i + City._GAP + 1)):
            tile0 = tile.branchise(reldirection, self._tileShapeSet)
            if tile0 is not None:
              tiles[i] = tile0
              reldirectionBranchTiles[reldirection][i] = True
              branchProb -= 1

              branchRoad = tile0.getBranchRoad()
              branchTiles = branchRoad.getTiles()
              assert len(branchTiles) != 0
              self._maxGeneration = max(self._maxGeneration, generation + 1)
              branchRoad.init((road.getTargetRang(i) + (-1, 1)[reldirection]) % 4, City._INIT_BRANCHISING_STATE)
              self._extendRoad(branchRoad, branchTiles[-1].getNextDirection(), branchTiles[-1].getNextX(), branchTiles[-1].getNextZ(), max(0, rng(lengthChoices) - len(branchTiles)), rng)
        i += 1

      if not wholeRoad:
        road.setBranchisingState((i, branchProb))

  def extendRoads (self, targetGeneration, rng, lengthChoices):
    assert not self._plottageExtended
    for road, generation in self.getRoads(targetGeneration):
      tiles = road.getTiles()
      self._extendRoad(road, tiles[-1].getNextDirection(), tiles[-1].getNextX(), tiles[-1].getNextZ(), rng(lengthChoices), rng)

  def extendPlottage (self, count = 0x3FFFFFFF):
    if __debug__:
      if not self._plottageExtended:
        self.resetPlottage()

    self._plottageExtended = True
    roads = [road for road, generation in self.getRoads()]
    for _ in xrange(0, count):
      plotsAdded = False
      for road in roads:
        for tile in road.getTiles():
          added = tile.addNextPlotShapes(self._tileShapeSet)
          if added:
            plotsAdded = True
      if not plotsAdded:
        break

  def resetPlottage (self):
    if not self._plottageExtended:
      if not __debug__:
        return

    if __debug__:
      def getShapeSet (shapeSet):
        return set(itertools.chain.from_iterable(bucket for bucket in shapeSet._buckets if bucket is not None))

      oldTileShapeSet__ = None
      if not self._plottageExtended:
        def dumpTileShapeSet ():
          r = []
          for shape in getShapeSet(self._tileShapeSet):
            box = shape.getBoundingBox()
            r.append((box.x0, box.z0, box.x1, box.z1))
          r.sort()
          return tuple(r)
        oldTileShapeSet__ = dumpTileShapeSet()

      for road in self._primaryMainRoads:
        road.removeShapesFromSet(self._tileShapeSet)
      for shape in self._boundaryExclusions:
        self._tileShapeSet.discardContained(shape)
      assert len(getShapeSet(self._tileShapeSet)) == 0

    def reminimalisePlotShapes (road):
      for tile in road.getTiles():
        tile.reminimalisePlotShapes()
        if isinstance(tile, BranchBaseRoadTile):
          reminimalisePlotShapes(tile.getBranchRoad())
    for road in self._primaryMainRoads:
      reminimalisePlotShapes(road)

    self._reinitTileShapeSet()
    for road in self._primaryMainRoads:
      road.addShapesToSet(self._tileShapeSet)
    assert oldTileShapeSet__ is None or oldTileShapeSet__ == dumpTileShapeSet()
    self._plottageExtended = False

  def place (self, world):
    for road in self._primaryMainRoads:
      road.place(world)
      world.placeMarker(self._centreX, self._centreZ)

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
class Display (object):
  def __init__ (self, viewport):
    assert isinstance(viewport, RectangularShape)
    self.viewport = viewport
    self._viewportWidth = viewport.x1 - viewport.x0
    self._vBuffer = bytearray((ord(' '),)) * ((viewport.z1 - viewport.z0) * self._viewportWidth)

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
    self._vBuffer[self._getI(x0, z0)] = c

  def drawWE (self, c, x0, z0, l):
    assert isinstance(l, int)
    assert l >= 0
    assert x0 + l <= self.viewport.x1
    i = self._getI(x0, z0)
    vBuffer = self._vBuffer
    for _ in xrange(0, l):
      vBuffer[i] = c
      i += 1

  def drawNS (self, c, x0, z0, l):
    assert isinstance(l, int)
    assert l >= 0
    assert z0 + l <= self.viewport.z1
    i = self._getI(x0, z0)
    vBuffer = self._vBuffer
    viewportWidth = self._viewportWidth
    for _ in xrange(0, l):
      vBuffer[i] = c
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
    vBuffer = self._vBuffer
    viewportWidth = self._viewportWidth
    viewportX0 = self.viewport.x0
    vz = box.z0 - self.viewport.z0
    for row in shape._getRows(box):
      vx = box.x0 - viewportX0
      i = vz * viewportWidth + vx
      while row:
        if row & 0b1:
          assert i == self._getI(vx + self.viewport.x0, vz + self.viewport.z0)
          vBuffer[i] = c
        row >>= 1
        i += 1
        vx += 1
      vz += 1

  def get (self):
    viewport = self.viewport
    viewportWidth = self._viewportWidth
    vBuffer = memoryview(self._vBuffer)
    return [vBuffer[i:i + viewportWidth].tobytes() for i in xrange(0, (viewport.z1 - viewport.z0) * viewportWidth, viewportWidth)]

class BitmapWorld (World):
  def __init__ (self, boundingBox):
    self._d = Display(boundingBox)

  def placeStraightRoadTile (self, shape, direction):
    assert isinstance(shape, RectangularShape)
    box = shape

    self._d.drawBox(ord('#'), box)
    self._placeRoadTileRoad(box, direction)

  def _placeRoadTileRoad (self, box, direction):
    if direction in (WEST, EAST):
      z = (box.z0 + box.z1) / 2
      self._d.drawWE(ord('-'), box.x0 + 1, z, box.x1 - box.x0 - 2)
      if direction == WEST:
        x0 = box.x0 + 1
        x1 = x0 + 1
      else:
        x0 = box.x1 - 2
        x1 = x0 - 1
      self._d.drawPel(ord('*'), x0, z)
      self._d.drawPel(ord('*'), x1, z - 1)
      self._d.drawPel(ord('*'), x1, z + 1)
    elif direction in (NORTH, SOUTH):
      x = (box.x0 + box.x1) / 2
      self._d.drawNS(ord('|'), x, box.z0 + 1, box.z1 - box.z0 - 2)
      if direction == NORTH:
        z0 = box.z0 + 1
        z1 = z0 + 1
      else:
        z0 = box.z1 - 2
        z1 = z0 - 1
      self._d.drawPel(ord('*'), x, z0)
      self._d.drawPel(ord('*'), x - 1, z1)
      self._d.drawPel(ord('*'), x + 1, z1)
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

    self._d.drawShape(ord('#'), ArbitraryShape(BitmapWorld.getArbitraryShapeOutline(shape), box.x0, box.z0))
    self._placeRoadTileRoad(box, direction)

  def placeTJunctionRoadTile (self, shape, direction, branchDirection):
    box = shape

    self.placeStraightRoadTile(shape, direction)

    l = (box.x1 - box.x0 - 2) / 2
    assert l == (box.z1 - box.z0 - 2) / 2
    if branchDirection == WEST:
      self._d.drawWE(ord('-'), box.x0 + 1, (box.z0 + box.z1) / 2, l)
    elif branchDirection == EAST:
      self._d.drawWE(ord('-'), (box.x0 + box.x1) / 2 + 1, (box.z0 + box.z1) / 2, l)
    elif branchDirection == NORTH:
      self._d.drawNS(ord('|'), (box.x0 + box.x1) / 2, box.z0 + 1, l)
    elif branchDirection == SOUTH:
      self._d.drawNS(ord('|'), (box.x0 + box.x1) / 2, (box.z0 + box.z1) / 2 + 1, l)
    else:
      assert False

  def placePlot (self, shape, direction):
    box = shape.getBoundingBox()
    if isinstance(shape, RectangularShape):
      self._d.drawBox(ord('.'), shape)
      if direction == WEST:
        self._d.drawNS(ord('o'), box.x1 - 1, (box.z0 + box.z1) / 2 - 1, 3)
      elif direction == EAST:
        self._d.drawNS(ord('o'), box.x0, (box.z0 + box.z1) / 2 - 1, 3)
      elif direction == NORTH:
        self._d.drawWE(ord('o'), (box.x0 + box.x1) / 2 - 1, box.z1 - 1, 3)
      elif direction == SOUTH:
        self._d.drawWE(ord('o'), (box.x0 + box.x1) / 2 - 1, box.z0, 3)
    else:
      shape = ArbitraryShape(BitmapWorld.getArbitraryShapeOutline(shape), box.x0, box.z0)
      self._d.drawShape(ord('.'), shape)
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
      self._d.drawShape(ord('o'), shape, RectangularShape(x0, z0, x1, z1))

  def placeMarker (self, x, z):
    self._d.drawWE(ord('X'), x, z, 1)

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
