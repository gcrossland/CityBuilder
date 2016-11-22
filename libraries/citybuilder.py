# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#  City Building Library
#  © Geoff Crossland 2016
# ------------------------------------------------------------------------------
import new
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
class Enum (object):
  _Member = int
  if __debug__:
    class _Member (object):
      def __init__ (self, i):
        self._i = i

      def __int__ (self):
        return self._i

  def __init__ (self, *args):
    all = [None] * len(args)
    for i in xrange(0, len(args)):
      self.__dict__[args[i]] = all[i] = Enum._Member(i)
    self.all = tuple(all)

  def map (self, **kwargs):
    r = [None] * len(self.all)
    maxI = -1
    for k, v in kwargs.iteritems():
      i = self.__dict__.get(k)
      r[i] = v
      maxI = max2(maxI, i)
    return tuple(itertools.islice(r, 0, maxI + 1))
  if __debug__:
    def map (self, **kwargs):
      r = {}
      for k, v in kwargs.iteritems():
        i = self.__dict__.get(k, None)
        assert i in self.all
        r[i] = v
      return r

Direction = Enum('EAST', 'SOUTH', 'WEST', 'NORTH', 'SOUTH_EAST', 'SOUTH_WEST', 'NORTH_WEST', 'NORTH_EAST')
Direction.cardinalLinesDs = new.instancemethod(lambda self, s: self.map(WEST = (-s, 0), EAST = (s, 0), NORTH = (0, -s), SOUTH = (0, s)), Direction, Enum)
Direction.intercardinalLinesDs = new.instancemethod(lambda self, s: self.map(SOUTH_WEST = (-s, s), NORTH_EAST = (s, -s), NORTH_WEST = (-s, -s), SOUTH_EAST = (s, s)), Direction, Enum)
WEST, EAST, NORTH, SOUTH = Direction.WEST, Direction.EAST, Direction.NORTH, Direction.SOUTH
SOUTH_EAST, SOUTH_WEST, NORTH_WEST, NORTH_EAST = Direction.SOUTH_EAST, Direction.SOUTH_WEST, Direction.NORTH_WEST, Direction.NORTH_EAST

Reldirection = Enum('LEFT', 'RIGHT')
Reldirection.swapped = new.instancemethod(lambda self, m: Reldirection.map(LEFT = m[RIGHT], RIGHT = m[LEFT]), Reldirection, Enum)
LEFT, RIGHT = Reldirection.LEFT, Reldirection.RIGHT

DIRECTIONS_BY_DIRECTION_WITH_RELDIRECTION = Direction.map(
  EAST = Reldirection.map(LEFT = NORTH, RIGHT = SOUTH),
  SOUTH = Reldirection.map(LEFT = EAST, RIGHT = WEST),
  WEST = Reldirection.map(LEFT = SOUTH, RIGHT = NORTH),
  NORTH = Reldirection.map(LEFT = WEST, RIGHT = EAST),
  SOUTH_EAST = Reldirection.map(LEFT = NORTH_EAST, RIGHT = SOUTH_WEST),
  SOUTH_WEST = Reldirection.map(LEFT = SOUTH_EAST, RIGHT = NORTH_WEST),
  NORTH_WEST = Reldirection.map(LEFT = SOUTH_WEST, RIGHT = NORTH_EAST),
  NORTH_EAST = Reldirection.map(LEFT = NORTH_WEST, RIGHT = SOUTH_EAST)
)

class World (object):
  def placeStraightRoadTile (self, shape, direction):
    raise NotImplementedError

  def placeBendingStraightRoadTile (self, shape, direction):
    raise NotImplementedError

  def placeDiagonalRoadTile (self, shape, direction):
    raise NotImplementedError

  def placeStraightToDiagonalRoadTile (self, shape, direction):
    raise NotImplementedError

  def placeDiagonalToStraightRoadTile (self, shape, direction):
    raise NotImplementedError

  def placeTJunctionRoadTile (self, shape, direction, branchDirection):
    raise NotImplementedError

  def placeMarker (self, x, z):
    raise NotImplementedError

class Road (object):
  def __init__ (self):
    self._tiles = []

  def init (self, targetRang, branchisingState):
    self._targetRang = targetRang
    self._branchisingState = branchisingState

  def getTargetRang (self, tileI):
    targetRang = self._targetRang(self, tileI)
    assert targetRang >= 0 and targetRang < 4
    return targetRang

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
  def __init__ (self, direction, x, z, shape, nextX, nextZ, hasLeftPlots, hasRightPlots):
    assert isinstance(x, int)
    assert isinstance(z, int)
    assert isinstance(shape, Shape)
    assert isinstance(nextX, int)
    assert isinstance(nextZ, int)
    self._direction = direction
    self._x = x
    self._z = z
    self._shape = shape
    self._nextX = nextX
    self._nextZ = nextZ
    self._leftPlotShapes = None
    if hasLeftPlots:
      self._leftPlotShapes = []
    self._rightPlotShapes = None
    if hasRightPlots:
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

    if shapes is None:
      return None

    shape = self._getNextPlotShape(shapes, reldirection)
    if shape is None:
      assert shapes[-1] is None
      return None

    if not shapeSet.addIfNotIntersecting(shape):
      shape = None
    shapes.append(shape)
    return shape

  def _addMinimalPlotShapes (self, needsMinimalPlotShapes, shapeSet):
    l = self._addNextPlotShape(self._leftPlotShapes, LEFT, shapeSet)
    r = self._addNextPlotShape(self._rightPlotShapes, RIGHT, shapeSet)

    if needsMinimalPlotShapes:
      if self._leftPlotShapes is not None and l is None:
        created = False
      elif self._rightPlotShapes is not None and r is None:
        created = False
      else:
        created = True
      if not created:
        for shape in (l, r):
          if shape is not None:
            shapeSet.discardContained(shape)
        return False

    return True

  def _addMinimalShapes (self, needsMinimalPlotShapes, shapeSet):
    if not shapeSet.addIfNotIntersecting(self._shape):
      return None

    if not self._addMinimalPlotShapes(needsMinimalPlotShapes, shapeSet):
      shapeSet.discardContained(self._shape)
      return None

    return self

  def addNextPlotShapes (self, shapeSet):
    l = self._addNextPlotShape(self._leftPlotShapes, LEFT, shapeSet)
    r = self._addNextPlotShape(self._rightPlotShapes, RIGHT, shapeSet)
    return l is not None or r is not None

  def _reminimalisePlotShapes (self, shapes):
    assert shapes in (self._leftPlotShapes, self._rightPlotShapes)

    if shapes is None:
      return

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
      if shapes is not None:
        for s in shapes:
          if s is not None:
            shapeSet.addUncontained(s)

  def removeShapesFromSet (self, shapeSet):
    shapeSet.discardContained(self._shape)
    for shapes in (self._leftPlotShapes, self._rightPlotShapes):
      if shapes is not None:
        for s in shapes:
          if s is not None:
            shapeSet.discardContained(s)

  def branchise (self, branchReldirection, shapeSet):
    return None

  def _placePlots (self, world):
    for shapes, reldirection in ((self._leftPlotShapes, LEFT), (self._rightPlotShapes, RIGHT)):
      if shapes is not None:
        direction = DIRECTIONS_BY_DIRECTION_WITH_RELDIRECTION[self.getDirection()][reldirection]
        for shape in shapes:
          if shape is not None:
            world.placePlot(shape, direction)

def dsAdd (x, z, *args):
  for dX, dZ in args:
    x += dX
    z += dZ
  return x, z

class StraightRoadTile (RoadTile):
  LEN = 11
  HLEN = (LEN - 1) / 2
  TILE_ORIGIN_DS = Direction.map(WEST = (-LEN + 1, -HLEN), EAST = (0, -HLEN), NORTH = (-HLEN, -LEN + 1), SOUTH = (-HLEN, 0))
  NEXT_DS = Direction.cardinalLinesDs(LEN)

  def __init__ (self, direction, x, z, hasLeftPlots = True, hasRightPlots = True):
    x0, z0 = dsAdd(x, z, StraightRoadTile.TILE_ORIGIN_DS[direction])
    shape = RectangularShape(x0, z0, x0 + StraightRoadTile.LEN, z0 + StraightRoadTile.LEN)

    nextX, nextZ = dsAdd(x, z, StraightRoadTile.NEXT_DS[direction])
    RoadTile.__init__(self, direction, x, z, shape, nextX, nextZ, hasLeftPlots, hasRightPlots)

  def getNextDirection (self):
    return self.getDirection()

  PLOT_DEPTH = 7
  PLOT_NEXT_DS = Direction.cardinalLinesDs(PLOT_DEPTH)

  WEST_LEFT = RectangularShape(0, LEN, LEN, LEN + PLOT_DEPTH)
  WEST_RIGHT = RectangularShape(0, -PLOT_DEPTH, LEN, 0)
  W = Reldirection.map(LEFT = WEST_LEFT, RIGHT = WEST_RIGHT)
  E = Reldirection.swapped(W)
  NORTH_LEFT = RectangularShape(-PLOT_DEPTH, 0, 0, LEN)
  NORTH_RIGHT = RectangularShape(LEN, 0, LEN + PLOT_DEPTH, LEN)
  N = Reldirection.map(LEFT = NORTH_LEFT, RIGHT = NORTH_RIGHT)
  S = Reldirection.swapped(N)
  PLOT_SHAPES = Direction.map(WEST = W, EAST = E, NORTH = N, SOUTH = S)

  def _getNextPlotShape (self, shapes, reldirection):
    if len(shapes) == 0:
      box = self.getShape()
      return StraightRoadTile.PLOT_SHAPES[self.getDirection()][reldirection].getTranslation(box.x0, box.z0)
    else:
      parentShape = shapes[-1]
      if parentShape is None:
        return None
      plotDirection = DIRECTIONS_BY_DIRECTION_WITH_RELDIRECTION[self.getDirection()][reldirection]
      dX, dZ = StraightRoadTile.PLOT_NEXT_DS[plotDirection]
      return parentShape.getTranslation(dX, dZ)

  @staticmethod
  def create (direction, x, z, shapeSet, needsMinimalPlotShapes = True):
    tile = StraightRoadTile(direction, x, z)
    return tile._addMinimalShapes(needsMinimalPlotShapes, shapeSet)

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
    world.placeStraightRoadTile(self.getShape(), self.getNextDirection())
    self._placePlots(world)

class BendingStraightRoadTile (RoadTile):
  LEN = StraightRoadTile.LEN
  TILE_ORIGIN_DS = StraightRoadTile.TILE_ORIGIN_DS
  OFF = 2
  TILE_ORIGIN_OFF_DS = Direction.map(WEST = (-OFF, 0), EAST = (0, 0), NORTH = (0, -OFF), SOUTH = (0, 0))
  NEXT_DS = StraightRoadTile.NEXT_DS
  NEXT_OFF_DS = Direction.cardinalLinesDs(2)

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
  WE = Reldirection.map(LEFT = WEST_LEFT, RIGHT = WEST_LEFT.getReflectionAroundXAxis())
  NORTH_LEFT = WEST_LEFT.getClockwiseQuarterRotation()
  NS = Reldirection.map(LEFT = NORTH_LEFT, RIGHT = NORTH_LEFT.getReflectionAroundZAxis())
  TEMPLATES = Direction.map(WEST = WE, EAST = WE, NORTH = NS, SOUTH = NS)

  def __init__ (self, direction, x, z, bendReldirection):
    bendDirection = DIRECTIONS_BY_DIRECTION_WITH_RELDIRECTION[direction][bendReldirection]

    x0, z0 = dsAdd(x, z, BendingStraightRoadTile.TILE_ORIGIN_DS[direction], BendingStraightRoadTile.TILE_ORIGIN_OFF_DS[bendDirection])
    shape = ArbitraryShape(BendingStraightRoadTile.TEMPLATES[direction][bendReldirection], x0, z0)

    nextX, nextZ = dsAdd(x, z, BendingStraightRoadTile.NEXT_DS[direction], BendingStraightRoadTile.NEXT_OFF_DS[bendDirection])
    RoadTile.__init__(self, direction, x, z, shape, nextX, nextZ, True, True)

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
  W = Reldirection.map(
    LEFT = Reldirection.map(LEFT = WEST_LEFT_LEFT, RIGHT = WEST_LEFT_RIGHT),
    RIGHT = Reldirection.map(LEFT = WEST_RIGHT_LEFT, RIGHT = WEST_RIGHT_RIGHT)
  )
  E = Reldirection.map(
    LEFT = Reldirection.swapped(W[LEFT]),
    RIGHT = Reldirection.swapped(W[RIGHT]) 
  )
  NORTH_LEFT_LEFT = ArbitraryShape(WEST_LEFT_LEFT._t.getClockwiseQuarterRotation(), -PLOT_DEPTH, 0)
  NORTH_LEFT_RIGHT = ArbitraryShape(NORTH_LEFT_LEFT._t.getClockwiseQuarterRotation().getClockwiseQuarterRotation(), LEN, 0)
  NORTH_RIGHT_LEFT = ArbitraryShape(NORTH_LEFT_RIGHT._t.getReflectionAroundZAxis(), -PLOT_DEPTH, 0)
  NORTH_RIGHT_RIGHT = ArbitraryShape(NORTH_LEFT_LEFT._t.getReflectionAroundZAxis(), LEN, 0)
  N = Reldirection.map(
    LEFT = Reldirection.map(LEFT = NORTH_LEFT_LEFT, RIGHT = NORTH_LEFT_RIGHT),
    RIGHT = Reldirection.map(LEFT = NORTH_RIGHT_LEFT, RIGHT = NORTH_RIGHT_RIGHT)
  )
  S = Reldirection.map(
    LEFT = Reldirection.swapped(N[LEFT]),
    RIGHT = Reldirection.swapped(N[RIGHT]) 
  )
  PLOT_SHAPES = Direction.map(WEST = W, EAST = E, NORTH = N, SOUTH = S)

  def _getNextPlotShape (self, shapes, reldirection):
    if len(shapes) == 0:
      box = self.getShape().getBoundingBox()
      return BendingStraightRoadTile.PLOT_SHAPES[self.getDirection()][self._bendReldirection][reldirection].getTranslation(box.x0, box.z0)
    else:
      parentShape = shapes[-1]
      if parentShape is None:
        return None
      plotDirection = DIRECTIONS_BY_DIRECTION_WITH_RELDIRECTION[self.getDirection()][reldirection]
      dX, dZ = BendingStraightRoadTile.PLOT_NEXT_DS[plotDirection]
      return parentShape.getTranslation(dX, dZ)

  @staticmethod
  def create (direction, x, z, bendReldirection, shapeSet, needsMinimalPlotShapes = True):
    tile = BendingStraightRoadTile(direction, x, z, bendReldirection)
    return tile._addMinimalShapes(needsMinimalPlotShapes, shapeSet)

  def branchise (self, branchReldirection, shapeSet):
    return None

  def place (self, world):
    world.placeBendingStraightRoadTile(self.getShape(), self.getNextDirection())
    self._placePlots(world)

class DiagonalRoadTile (RoadTile):
  TILE_ORIGIN_DS = Direction.map(SOUTH_WEST = (-11, -3), NORTH_EAST = (-3, -11), NORTH_WEST = (-11, -11), SOUTH_EAST = (-3, -3))
  NEXT_DS = Direction.intercardinalLinesDs(8)

  SOUTH_WEST = ArbitraryShape.Template(ArbitraryShape.Template.rows(
    "       **      ",
    "      ****     ",
    "     *****X    ",
    "    *****XX*   ",
    "   *****XX*XX  ",
    "  *****XX*XX** ",
    " *****XX*XX****",
    "*****XX*XX*****",
    " ***XX*XX***** ",
    "  *XX*XX*****  ",
    "   X*XX*****   ",
    "    XX*****    ",
    "     *****     ",
    "      ***      ",
    "       *       "
  ))
  NORTH_EAST = SOUTH_WEST.getClockwiseQuarterRotation().getClockwiseQuarterRotation()
  NORTH_WEST = SOUTH_WEST.getClockwiseQuarterRotation()
  SOUTH_EAST = NORTH_EAST.getClockwiseQuarterRotation()
  TEMPLATES = Direction.map(SOUTH_WEST = SOUTH_WEST, NORTH_EAST = NORTH_EAST, NORTH_WEST = NORTH_WEST, SOUTH_EAST = SOUTH_EAST)

  def __init__ (self, direction, x, z):
    x0, z0 = dsAdd(x, z, DiagonalRoadTile.TILE_ORIGIN_DS[direction])
    shape = ArbitraryShape(DiagonalRoadTile.TEMPLATES[direction], x0, z0)

    nextX, nextZ = dsAdd(x, z, DiagonalRoadTile.NEXT_DS[direction])
    RoadTile.__init__(self, direction, x, z, shape, nextX, nextZ, False, False) # TODO add plots

  def getNextDirection (self):
    return self.getDirection()

  def _getNextPlotShape (self, shapes, reldirection):
    # TODO this
    assert False

  @staticmethod
  def create (direction, x, z, shapeSet, needsMinimalPlotShapes = True):
    tile = DiagonalRoadTile(direction, x, z)
    return tile._addMinimalShapes(needsMinimalPlotShapes, shapeSet)

  def branchise (self, branchReldirection, shapeSet):
    return None

  def place (self, world):
    world.placeDiagonalRoadTile(self.getShape(), self.getNextDirection())
    self._placePlots(world)

class StraightToDiagonalRoadTile (RoadTile):
  TILE_ORIGIN_DS = Direction.map(WEST = (-11, -5), EAST = (0, -5), NORTH = (-5, -11), SOUTH = (-5, 0))
  OFF = 2
  TILE_ORIGIN_OFF_DS = Direction.map(WEST = (-OFF, 0), EAST = (0, 0), NORTH = (0, -OFF), SOUTH = (0, 0))
  NEXT_DS = Direction.cardinalLinesDs(8)
  NEXT_OFF_DS = Direction.cardinalLinesDs(4)

  WEST_LEFT = ArbitraryShape.Template(ArbitraryShape.Template.rows(
    "     *******",
    "    ********",
    "   *********",
    "  **********",
    " *****XXXXXX",
    "*****XX*****",
    " ***XX*XXXXX",
    "  *XX*XX****",
    "   X*XX*****",
    "    XX******",
    "     *******",
    "      ***   ",
    "       *    "
  ))
  W = Reldirection.map(LEFT = WEST_LEFT, RIGHT = WEST_LEFT.getReflectionAroundXAxis())
  EAST_LEFT = WEST_LEFT.getClockwiseQuarterRotation().getClockwiseQuarterRotation()
  E = Reldirection.map(LEFT = EAST_LEFT, RIGHT = EAST_LEFT.getReflectionAroundXAxis())
  NORTH_LEFT = WEST_LEFT.getClockwiseQuarterRotation()
  N = Reldirection.map(LEFT = NORTH_LEFT, RIGHT = NORTH_LEFT.getReflectionAroundZAxis())
  SOUTH_LEFT = NORTH_LEFT.getClockwiseQuarterRotation().getClockwiseQuarterRotation()
  S = Reldirection.map(LEFT = SOUTH_LEFT, RIGHT = SOUTH_LEFT.getReflectionAroundZAxis())
  TEMPLATES = Direction.map(WEST = W, EAST = E, NORTH = N, SOUTH = S)

  def __init__ (self, direction, x, z, bendReldirection):
    bendDirection = DIRECTIONS_BY_DIRECTION_WITH_RELDIRECTION[direction][bendReldirection]

    x0, z0 = dsAdd(x, z, StraightToDiagonalRoadTile.TILE_ORIGIN_DS[direction], StraightToDiagonalRoadTile.TILE_ORIGIN_OFF_DS[bendDirection])
    shape = ArbitraryShape(StraightToDiagonalRoadTile.TEMPLATES[direction][bendReldirection], x0, z0)

    nextX, nextZ = dsAdd(x, z, StraightToDiagonalRoadTile.NEXT_DS[direction], StraightToDiagonalRoadTile.NEXT_OFF_DS[bendDirection])
    RoadTile.__init__(self, direction, x, z, shape, nextX, nextZ, False, False) # TODO add plots - bendReldirection != Reldirection.LEFT, bendReldirection != Reldirection.RIGHT)

    self._bendReldirection = bendReldirection

  NEXT_DIRECTION = Direction.map(
    WEST = Reldirection.map(LEFT = SOUTH_WEST, RIGHT = NORTH_WEST),
    EAST = Reldirection.map(LEFT = NORTH_EAST, RIGHT = SOUTH_EAST),
    NORTH = Reldirection.map(LEFT = NORTH_WEST, RIGHT = NORTH_EAST),
    SOUTH = Reldirection.map(LEFT = SOUTH_EAST, RIGHT = SOUTH_WEST)
  )

  def getNextDirection (self):
    return StraightToDiagonalRoadTile.NEXT_DIRECTION[self.getDirection()][self._bendReldirection]

  def _getNextPlotShape (self, shapes, reldirection):
    # TODO this
    assert False

  @staticmethod
  def create (direction, x, z, bendReldirection, shapeSet, needsMinimalPlotShapes = True):
    tile = StraightToDiagonalRoadTile(direction, x, z, bendReldirection)
    return tile._addMinimalShapes(needsMinimalPlotShapes, shapeSet)

  def branchise (self, branchReldirection, shapeSet):
    return None

  def place (self, world):
    world.placeStraightToDiagonalRoadTile(self.getShape(), self.getNextDirection())
    self._placePlots(world)

class DiagonalToStraightRoadTile (RoadTile):
  TILE_ORIGIN_DS = Direction.map(SOUTH_WEST = (-9, -3), NORTH_EAST = (-3, -9), NORTH_WEST = (-9, -9), SOUTH_EAST = (-3, -3))
  OFF = -1
  TILE_ORIGIN_OFF_DS = Direction.map(WEST = (-OFF, 0), EAST = (0, 0), NORTH = (0, -OFF), SOUTH = (0, 0))
  NEXT_DS = Direction.intercardinalLinesDs(4)
  NEXT_OFF_DS = Direction.cardinalLinesDs(5)

  SOUTH_WEST_LEFT = ArbitraryShape.Template(ArbitraryShape.Template.rows(
    "     **      ",
    "    ****     ",
    "   *****X    ",
    "  *****XX*   ",
    " *****XX*XX  ",
    "*****XX*XX** ",
    "****XX*XX****",
    "****X*XX*****",
    "****X*X***** ",
    "****X*X****  ",
    "****X*X****  ",
    "****X*X****  "
  ))
  SOUTH_WEST_RIGHT = ArbitraryShape.Template(ArbitraryShape.Template.rows(
    "    **      ",
    "   ****     ",
    "*******X    ",
    "******XX*   ",
    "*****XX*XX  ",
    "****XX*XX** ",
    "XXXXX*XX****",
    "*****XX*****",
    "XXXXXX***** ",
    "**********  ",
    "*********   ",
    "********    ",
    "*******     "
  ))
  S_W = Reldirection.map(LEFT = SOUTH_WEST_LEFT, RIGHT = SOUTH_WEST_RIGHT)
  NORTH_EAST_LEFT = SOUTH_WEST_LEFT.getClockwiseQuarterRotation().getClockwiseQuarterRotation()
  NORTH_EAST_RIGHT = SOUTH_WEST_RIGHT.getClockwiseQuarterRotation().getClockwiseQuarterRotation()
  N_E = Reldirection.map(LEFT = NORTH_EAST_LEFT, RIGHT = NORTH_EAST_RIGHT)
  NORTH_WEST_LEFT = SOUTH_WEST_LEFT.getClockwiseQuarterRotation()
  NORTH_WEST_RIGHT = SOUTH_WEST_RIGHT.getClockwiseQuarterRotation()
  N_W = Reldirection.map(LEFT = NORTH_WEST_LEFT, RIGHT = NORTH_WEST_RIGHT)
  SOUTH_EAST_LEFT = NORTH_WEST_LEFT.getClockwiseQuarterRotation().getClockwiseQuarterRotation()
  SOUTH_EAST_RIGHT = NORTH_WEST_RIGHT.getClockwiseQuarterRotation().getClockwiseQuarterRotation()
  S_E = Reldirection.map(LEFT = SOUTH_EAST_LEFT, RIGHT = SOUTH_EAST_RIGHT)
  TEMPLATES = Direction.map(SOUTH_WEST = S_W, NORTH_EAST = N_E, NORTH_WEST = N_W, SOUTH_EAST = S_E)

  def __init__ (self, direction, x, z, bendReldirection):
    bendDirection = DiagonalToStraightRoadTile.NEXT_DIRECTION[direction][bendReldirection]

    x0, z0 = dsAdd(x, z, DiagonalToStraightRoadTile.TILE_ORIGIN_DS[direction], DiagonalToStraightRoadTile.TILE_ORIGIN_OFF_DS[bendDirection])
    shape = ArbitraryShape(DiagonalToStraightRoadTile.TEMPLATES[direction][bendReldirection], x0, z0)

    nextX, nextZ = dsAdd(x, z, DiagonalToStraightRoadTile.NEXT_DS[direction], DiagonalToStraightRoadTile.NEXT_OFF_DS[bendDirection])
    RoadTile.__init__(self, direction, x, z, shape, nextX, nextZ, False, False) # TODO add plots - bendReldirection != Reldirection.LEFT, bendReldirection != Reldirection.RIGHT)

    self._bendReldirection = bendReldirection

  NEXT_DIRECTION = Direction.map(
    SOUTH_WEST = Reldirection.map(LEFT = SOUTH, RIGHT = WEST),
    NORTH_EAST = Reldirection.map(LEFT = NORTH, RIGHT = EAST),
    NORTH_WEST = Reldirection.map(LEFT = WEST, RIGHT = NORTH),
    SOUTH_EAST = Reldirection.map(LEFT = EAST, RIGHT = SOUTH)
  )

  def getNextDirection (self):
    return DiagonalToStraightRoadTile.NEXT_DIRECTION[self.getDirection()][self._bendReldirection]

  def _getNextPlotShape (self, shapes, reldirection):
    # TODO this
    assert False

  @staticmethod
  def create (direction, x, z, bendReldirection, shapeSet, needsMinimalPlotShapes = True):
    tile = DiagonalToStraightRoadTile(direction, x, z, bendReldirection)
    return tile._addMinimalShapes(needsMinimalPlotShapes, shapeSet)

  def branchise (self, branchReldirection, shapeSet):
    return None

  def place (self, world):
    world.placeDiagonalToStraightRoadTile(self.getShape(), self.getNextDirection())
    self._placePlots(world)

class BranchBaseRoadTile (RoadTile):
  def __init__ (self, branchReldirection, branchX, branchZ):
    self._branchReldirection = branchReldirection
    self._branchX = branchX
    self._branchZ = branchZ
    self._branchRoad = Road()

  def getBranchReldirection (self):
    return self._branchReldirection

  def getBranchDirection (self):
    return DIRECTIONS_BY_DIRECTION_WITH_RELDIRECTION[self.getDirection()][self._branchReldirection]

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
    StraightRoadTile.__init__(self, direction, x, z, branchReldirection != Reldirection.LEFT, branchReldirection != Reldirection.RIGHT)

    box = self.getShape()
    assert isinstance(box, RectangularShape)
    branchDirection = DIRECTIONS_BY_DIRECTION_WITH_RELDIRECTION[direction][branchReldirection]
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
    return tile._addMinimalShapes(True, shapeSet)

  def branchise (self, branchReldirection, shapeSet):
    return None

  def place (self, world):
    world.placeTJunctionRoadTile(self.getShape(), self.getNextDirection(), self.getBranchDirection())
    self._placePlots(world)
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

RANGS_BY_DIRECTION = Direction.map(EAST = 0, SOUTH_EAST = 0.5, SOUTH = 1, SOUTH_WEST = 1.5, WEST = 2, NORTH_WEST = 2.5, NORTH = 3, NORTH_EAST = 3.5)

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

  OPPOSITE_DIRECTIONS = Direction.map(WEST = EAST, EAST = WEST, NORTH = SOUTH, SOUTH = NORTH)
  DS = Direction.cardinalLinesDs(1)

  def _buildPrimaryMainRoads (self, endpoints, rng):
    assert self._primaryMainRoads is None
    self._primaryMainRoads = (Road(), Road())

    endpointDirections = tuple(City._getMainRoadDirection(self._centreX, self._centreZ, x, z) for x, z in endpoints)

    primaryEndpoint0I, primaryEndpoint1I = City._getPrimaryMainRoadEndpoints(endpointDirections)

    x, z = endpoints[primaryEndpoint0I]
    primaryDirection = endpointDirections[primaryEndpoint0I]
    self._buildMainRoad(self._primaryMainRoads[0], primaryDirection, self._centreX, self._centreZ, x, z, rng)

    oppositeDirection = City.OPPOSITE_DIRECTIONS[primaryDirection]
    dX, dZ = City.DS[oppositeDirection]

    if primaryEndpoint1I is None:
      tile = StraightRoadTile.create(oppositeDirection, self._centreX + dX, self._centreZ + dZ, self._tileShapeSet)
      if tile is not None:
        self._primaryMainRoads[1].getTiles().append(tile)
      self._primaryMainRoads[1].init(self.constantTargetRangFactory(rang(dX, dZ)), City._INIT_BRANCHISING_STATE)
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

      road.init(self.constantTargetRangFactory(rang(destX - x, destZ - z)), City._INIT_BRANCHISING_STATE)
      self._extendRoad(road, direction, x, z, -1, rng)
    finally:
      self._tileShapeSet.discardContained(limitBox)

  DIRECTIONS_AND_CREATORS = (
    (0,                                                                (EAST,       lambda x, z, shapeSet: StraightRoadTile.create(EAST, x, z, shapeSet))),
    (rang(BendingStraightRoadTile.LEN, BendingStraightRoadTile.OFF),   (EAST,       lambda x, z, shapeSet: BendingStraightRoadTile.create(EAST, x, z, RIGHT, shapeSet))),
    (0.5,                                                              (SOUTH_EAST, lambda x, z, shapeSet: DiagonalRoadTile.create(SOUTH_EAST, x, z, shapeSet))),
    (rang(BendingStraightRoadTile.OFF, BendingStraightRoadTile.LEN),   (SOUTH,      lambda x, z, shapeSet: BendingStraightRoadTile.create(SOUTH, x, z, LEFT, shapeSet))),
    (1,                                                                (SOUTH,      lambda x, z, shapeSet: StraightRoadTile.create(SOUTH, x, z, shapeSet))),
    (rang(-BendingStraightRoadTile.OFF, BendingStraightRoadTile.LEN),  (SOUTH,      lambda x, z, shapeSet: BendingStraightRoadTile.create(SOUTH, x, z, RIGHT, shapeSet))),
    (1.5,                                                              (SOUTH_WEST, lambda x, z, shapeSet: DiagonalRoadTile.create(SOUTH_WEST, x, z, shapeSet))),
    (rang(-BendingStraightRoadTile.LEN, BendingStraightRoadTile.OFF),  (WEST,       lambda x, z, shapeSet: BendingStraightRoadTile.create(WEST, x, z, LEFT, shapeSet))),
    (2,                                                                (WEST,       lambda x, z, shapeSet: StraightRoadTile.create(WEST, x, z, shapeSet))),
    (rang(-BendingStraightRoadTile.LEN, -BendingStraightRoadTile.OFF), (WEST,       lambda x, z, shapeSet: BendingStraightRoadTile.create(WEST, x, z, RIGHT, shapeSet))),
    (2.5,                                                              (NORTH_WEST, lambda x, z, shapeSet: DiagonalRoadTile.create(NORTH_WEST, x, z, shapeSet))),
    (rang(-BendingStraightRoadTile.OFF, -BendingStraightRoadTile.LEN), (NORTH,      lambda x, z, shapeSet: BendingStraightRoadTile.create(NORTH, x, z, LEFT, shapeSet))),
    (3,                                                                (NORTH,      lambda x, z, shapeSet: StraightRoadTile.create(NORTH, x, z, shapeSet))),
    (rang(BendingStraightRoadTile.OFF, -BendingStraightRoadTile.LEN),  (NORTH,      lambda x, z, shapeSet: BendingStraightRoadTile.create(NORTH, x, z, RIGHT, shapeSet))),
    (3.5,                                                              (NORTH_EAST, lambda x, z, shapeSet: DiagonalRoadTile.create(NORTH_EAST, x, z, shapeSet))),
    (rang(BendingStraightRoadTile.LEN, -BendingStraightRoadTile.OFF),  (EAST,       lambda x, z, shapeSet: BendingStraightRoadTile.create(EAST, x, z, LEFT, shapeSet)))
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

  def cardinal (direction):
    return Reldirection.map(
      LEFT = lambda x, z, shapeSet: StraightToDiagonalRoadTile.create(direction, x, z, LEFT, shapeSet),
      RIGHT = lambda x, z, shapeSet: StraightToDiagonalRoadTile.create(direction, x, z, RIGHT, shapeSet)
    )
  def intercardinal (direction):
    return Reldirection.map(
      LEFT = lambda x, z, shapeSet: DiagonalToStraightRoadTile.create(direction, x, z, LEFT, shapeSet),
      RIGHT = lambda x, z, shapeSet: DiagonalToStraightRoadTile.create(direction, x, z, RIGHT, shapeSet)
    )
  DIRECTION_CHANGE_CREATORS = Direction.map(
    EAST = cardinal(EAST),
    SOUTH = cardinal(SOUTH),
    WEST = cardinal(WEST),
    NORTH = cardinal(NORTH),
    SOUTH_EAST = intercardinal(SOUTH_EAST),
    SOUTH_WEST = intercardinal(SOUTH_WEST),
    NORTH_WEST = intercardinal(NORTH_WEST),
    NORTH_EAST = intercardinal(NORTH_EAST)
  )
  del cardinal, intercardinal

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

      dcs = City._getDirectionAndCreatorPairForRang(targetRang)
      assert len(dcs) in (1, 2)
      if len(dcs) == 2:
        if (attainedRang - targetRang) % 4 < 2:
          dcs = (dcs[0],) * 6 + (dcs[1],)
        else:
          dcs = (dcs[1],) * 6 + (dcs[0],)
      rqdDirection, creator = rng(dcs)
      if rqdDirection != direction:
        reldirection = (LEFT, RIGHT)[(RANGS_BY_DIRECTION[rqdDirection] - RANGS_BY_DIRECTION[direction]) % 4 < 2]
        creator = City.DIRECTION_CHANGE_CREATORS[direction][reldirection]

      tile = creator(x, z, tileShapeSet)
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
  _RANG_BY_RELDIRECTION = Reldirection.map(LEFT = -1, RIGHT = 1)

  def constantTargetRangFactory (self, initialRang):
    return lambda road, tileI: initialRang

  def circlingTargetRangFactory (self, initialRang):
    def _ (road, tileI):
      tiles = road.getTiles()
      assert tileI <= len(tiles)
      if len(tiles) == 0:
        return initialRang
      rang0 = rang(tiles[0].getX() - self._centreX, tiles[0].getZ() - self._centreZ)
      rang1 = rang(tiles[tileI - 1].getNextX() - self._centreX, tiles[tileI - 1].getNextZ() - self._centreZ)
      dRang = rang1 - rang0
      return (initialRang + dRang) % 4
    return _

  def addBranches (self, targetGeneration, wholeRoad, rng, branchChoices, lengthChoices, targetRangFactory):
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
      reldirectionBranchTiles = Reldirection.map(
        LEFT = [isinstance(t, BranchBaseRoadTile) and t.getBranchReldirection() == LEFT for t in tiles],
        RIGHT = [isinstance(t, BranchBaseRoadTile) and t.getBranchReldirection() == RIGHT for t in tiles]
      )
      while i < len(tiles) - City._GAP:
        tile = tiles[i]
        branchProb += rng(branchChoices)
        if branchProb >= 1:
          reldirection = rng(Reldirection.all)
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
              branchRoad.init(targetRangFactory((road.getTargetRang(i) + City._RANG_BY_RELDIRECTION[reldirection]) % 4), City._INIT_BRANCHISING_STATE)
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
      pass # TODO

  _arbitraryShapeTemplateOutlines = {}

  @staticmethod
  def getArbitraryShapeOutline (shape):
    assert isinstance(shape, ArbitraryShape)
    t0 = shape._t
    t1 = BitmapWorld._arbitraryShapeTemplateOutlines.get(t0, None)
    if t1 is None:
      BitmapWorld._arbitraryShapeTemplateOutlines[t0] = t1 = t0.getOutline()
    return t1

  def _placeArbitraryShapedRoadTile (self, shape, direction):
    box = shape.getBoundingBox()

    self._d.drawShape(ord('#'), ArbitraryShape(BitmapWorld.getArbitraryShapeOutline(shape), box.x0, box.z0))
    self._placeRoadTileRoad(box, direction)

  def placeBendingStraightRoadTile (self, shape, direction):
    self._placeArbitraryShapedRoadTile(shape, direction)

  def placeDiagonalRoadTile (self, shape, direction):
    self._placeArbitraryShapedRoadTile(shape, direction)

  def placeStraightToDiagonalRoadTile (self, shape, direction):
    self._placeArbitraryShapedRoadTile(shape, direction)

  def placeDiagonalToStraightRoadTile (self, shape, direction):
    self._placeArbitraryShapedRoadTile(shape, direction)

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
