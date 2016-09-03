# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#  City Building Library
#  © Geoff Crossland 2016
# ------------------------------------------------------------------------------
import itertools
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

  def __init__ (self, t, x0, z0):
    assert isinstance(t, ArbitraryShape.Template)
    self._t = t
    self._x0 = x0
    self._z0 = z0
    self._boundingBox = RectangularShape(x0, z0, x0 + t._getDX(), z0 + t._getDZ())

  def getTranslation (self, dX, dZ):
    return ArbitraryShape(self._t, self._x0 + dX, self._z0 + dZ)

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

  def branchise (self, branchReldirection, shapeSet):
    return None

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

  def branchise (self, branchReldirection, shapeSet):
    self.removeShapesFromSet(shapeSet)

    tile = TJunctionRoadTile.create(self.getDirection(), self.getX(), self.getZ(), branchReldirection, shapeSet)
    if tile is None:
      self.addShapesToSet(shapeSet)
      return None
    assert self.getNextDirection() == tile.getNextDirection()
    assert self.getNextX() == tile.getNextX()
    assert self.getNextZ() == tile.getNextZ()

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

  def addShapesToSet (self, shapeSet):
    RoadTile.addShapesToSet(self, shapeSet)
    for tile in self._branchRoadTiles:
      tile.addShapesToSet(shapeSet)

  def removeShapesFromSet (self, shapeSet):
    RoadTile.removeShapesFromSet(self, shapeSet)
    for tile in self._branchRoadTiles:
      tile.removeShapesFromSet(shapeSet)

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
      shapeSet.remove(tile.getShape())
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
    for tile in self.getBranchRoadTiles():
      tile.place(world)

class PlotTile (Tile):
  pass

class City (object):
  def __init__ (self, centreX, centreZ, boundary, boundaryExclusions):
    assert isinstance(centreX, int)
    assert isinstance(centreZ, int)
    assert isinstance(boundary, RectangularShape)
    assert isinstance(boundaryExclusions, ShapeSet)
    # TODO target population, initial target population density

    self._centreX = centreX
    self._centreZ = centreZ
    self._boundary = boundary
    self._boundaryExclusions = boundaryExclusions
    self._roads = ([], [])
    self._tileShapeSet = ShapeSet()

    self._reinitTileShapeSet()
    for roadTiles, direction, x, z in itertools.izip(self._roads, (WEST, EAST), (self._centreX - 1, self._centreX), (self._centreZ, self._centreZ)):
      self._buildMainRoad(roadTiles, direction, x, z)

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

  def _buildMainRoad (self, roadTiles, direction, x, z):
    while True:
      tile = StraightRoadTile.create(direction, x, z, self._tileShapeSet)
      if tile is None:
        break
      roadTiles.append(tile)

      direction = tile.getNextDirection()
      x = tile.getNextX()
      z = tile.getNextZ()

  @staticmethod
  def walkRoadTiles (rootTilesSet, rootGeneration, fn):
    this = list(rootTilesSet)
    next = []
    generation = rootGeneration
    while len(this) != 0:
      for tiles in this:
        fn(tiles, generation)
        for tile in tiles:
          if isinstance(tile, BranchBaseRoadTile):
            next.append(tile.getBranchRoadTiles())
      t = this
      this = next
      next = t
      del next[:]
      generation += 1

  def performGrowthIteration (self, rng):
    def reminimalisePlotShapes (tiles):
      for tile in tiles:
        tile.reminimalisePlotShapes()
        if isinstance(tile, BranchBaseRoadTile):
          reminimalisePlotShapes(tile.getBranchRoadTiles())
    for tiles in self._roads:
      reminimalisePlotShapes(tiles)
    self._reinitTileShapeSet()
    tileShapeSet = self._tileShapeSet
    for tiles in self._roads:
      for tile in tiles:
        tile.addShapesToSet(tileShapeSet)

    def addBranches (tiles, generation):
      reldirectionBranchTiles = (
        [isinstance(t, BranchBaseRoadTile) and t.getBranchReldirection() == LEFT for t in tiles],
        [isinstance(t, BranchBaseRoadTile) and t.getBranchReldirection() == RIGHT for t in tiles]
      )
      for i in xrange(2, len(tiles) - 2):
        tile = tiles[i]
        if not isinstance(tile, BranchBaseRoadTile) and rng.randrange(0, 10) == 0:
          reldirection = rng.choice((LEFT, RIGHT))
          if not any(itertools.islice(reldirectionBranchTiles[reldirection], i - 2, i + 3)):
            tile0 = tile.branchise(reldirection, tileShapeSet)
            if tile0 is not None:
              tile1 = StraightRoadTile.create(tile0.getBranchDirection(), tile0.getBranchX(), tile0.getBranchZ(), tileShapeSet, False)
              if tile1 is not None:
                tile0.getBranchRoadTiles().append(tile1)
                tiles[i] = tile0
                reldirectionBranchTiles[reldirection][i] = True
              else:
                tile0.removeShapesFromSet(tileShapeSet)
                tile.addShapesToSet(tileShapeSet)
    City.walkRoadTiles(self._roads, 0, addBranches)

    def extendRoad (tiles, generation):
      for i in xrange(0, rng.randrange(0, 5 + 1)):
        direction = tiles[-1].getNextDirection()
        x = tiles[-1].getNextX()
        z = tiles[-1].getNextZ()
        tile = StraightRoadTile.create(direction, x, z, tileShapeSet)
        if tile is None:
          break
        tiles.append(tile)
    City.walkRoadTiles(self._roads, 0, extendRoad)

  def extendPlotage (self, rng, maxDepth = 0x3FFFFFFF):
    r_plotsAdded = [False]
    def markPlots (tiles, generation):
      for tile in tiles:
        added = tile.addNextPlotShapes(self._tileShapeSet)
        if added:
          r_plotsAdded[0] = True
    for _ in xrange(1, maxDepth):
      r_plotsAdded[0] = False
      City.walkRoadTiles(self._roads, 0, markPlots)
      if not r_plotsAdded[0]:
        break

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

  def drawShape (self, c, shape):
    assert isinstance(shape, Shape)
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
    assert isinstance(shape, RectangularShape) # TODO for now
    box = shape

    self._d.drawBox('#', box)
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

  def placePlot (self, box, direction):
    self._d.drawBox('.', box)
    if direction == WEST:
      self._d.drawNS('o', box.x1 - 1, (box.z0 + box.z1) / 2 - 1, 3)
    elif direction == EAST:
      self._d.drawNS('o', box.x0, (box.z0 + box.z1) / 2 - 1, 3)
    elif direction == NORTH:
      self._d.drawWE('o', (box.x0 + box.x1) / 2 - 1, box.z1 - 1, 3)
    elif direction == SOUTH:
      self._d.drawWE('o', (box.x0 + box.x1) / 2 - 1, box.z0, 3)

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
